from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.status import *
from django.db.models import Q
from django.conf import settings

from .models import List, Mission
from .serializers import ListSerializer, MissionSerializer

import Parent.utils as orm
from .utils import handle_lock_entertainment, handle_unlock_entertainment

from datetime import datetime


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def set_cookie(request):    
    response = Response(status=200)
    response.set_cookie(request.data['key'], request.data['value'], max_age=(60 * 60 * 24 * 365) if request.data['life'] == 'long' else (60 * 60 * 24 * 30), domain=settings.DOMAIN, httponly=True)

    return response

class ListsAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]


    def get(self, request):

        try:
            data = orm.get_all_objs(
                model=List,
                modelSerializer=ListSerializer,
                user=request.user.id,
                order_by=['-create_date', '-id']
            )

            return Response(data=data, status=HTTP_200_OK)

        except:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            user = request.user.id
                
            list_data = request.data['list']
            missions_data = request.data['missions']

            # Creating List in DB

            try:
                if list_data['reward']:
                    if list_data['lock_reward']:
                        handle_lock_entertainment(list_data['reward'])

                    del list_data['lock_reward']

            except ValidationError:
                return Response(status=HTTP_400_BAD_REQUEST)

            list_data['user'] = user
            list_serializer = ListSerializer(data=list_data)
                
            if list_serializer.is_valid():
                list_serializer.save()

                    # Creating List's Mission Objects
                if len(missions_data) > 0:
                    for mission in missions_data:
                        mission['list'] = list_serializer.data['id']

                    missions_serializer = MissionSerializer(data=missions_data, many=True)

                    if missions_serializer.is_valid():
                        missions_serializer.save()

                        return Response(data=list_serializer.data, status=HTTP_201_CREATED)
                        
                    return Response(data=missions_serializer.errors, status=HTTP_400_BAD_REQUEST)

                return Response(status=HTTP_411_LENGTH_REQUIRED)
                    
            return Response(data=list_serializer.errors, status=HTTP_400_BAD_REQUEST)

        except:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
def get_today_list(request, date):

    try:
        user = request.user.id

        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        list_ = List.objects.get(user=user, date=date_obj)
        missions = list_.mission_set.all()

        list_serializer = ListSerializer(instance=list_)
        missions_serializer = MissionSerializer(instance=missions, many=True)

        data = list_serializer.data
        data['missions'] = missions_serializer.data

        list_style = request.COOKIES.get('list_style')
        data['style'] = list_style
        
        return Response(data=data, status=HTTP_200_OK)
    
    except List.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)
    

class ListAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request, pk):

        try:
            list_, data = orm.get_obj_by(
                List, ListSerializer,
                request.user.id,
                {'id': pk}
            )

            data['missions'] = MissionSerializer(instance=list_.mission_set.all(), many=True).data

            return Response(data=data, status=HTTP_200_OK)
        
        except List.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
    

    def patch(self, request, pk):
        
        try:
            list_ = List.objects.get(id=pk, user=request.user.id)
            serializer = ListSerializer(instance=list_, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response(status=HTTP_202_ACCEPTED)
            
            return Response(status=HTTP_400_BAD_REQUEST)
        
        except List.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

    
    def delete(self, request, pk):
        try:
            orm.delete_obj(List, request.user.id, {'id': pk})

            return Response(status=HTTP_204_NO_CONTENT)
        
        except List.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
def mission_operations(request, pk):

    if request.method == 'PATCH':
        mission = Mission.objects.get(id=pk)

        serializer = MissionSerializer(instance=mission, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            if serializer.data['list']:
                missions_list = List.objects.get(id=serializer.data['list'])
                all_missions = missions_list.mission_set.all()
                done_missions = Mission.objects.filter(list=missions_list.id, status='done')

                if done_missions.count() == all_missions.count(): # auto complete the list when all missions are done.
                    list_serializer = ListSerializer(instance=missions_list, data={"done": True}, partial=True)

                    if list_serializer.is_valid():
                        list_serializer.save()

                        if list_serializer.data['reward']:
                            if handle_unlock_entertainment(list_serializer.data['reward']):

                                return Response(status=HTTP_200_OK)
                        else:
                            return Response(status=HTTP_200_OK)
                    return Response(data=list_serializer.errors, status=HTTP_400_BAD_REQUEST)

            return Response(data=serializer.data, status=HTTP_202_ACCEPTED)
        
        return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
def get_sequence_list(request, pk, sequence): # Get's the id of next and previous mission lists of currrent opened list.
    try:
        user = request.user.id
        
        lists = List.objects.filter(user=user).order_by('id')
        current_list_ = List.objects.get(user=user, id=pk)
        current_index = list(lists).index(current_list_)
        
        try:
            if sequence == 'next':
                list_ = lists[current_index + 1]

            elif sequence == 'prev':
                list_ = lists[current_index - 1]

            return Response(data={'id': list_.id}, status=HTTP_200_OK)
        
        except IndexError:
            return Response(status=HTTP_404_NOT_FOUND)

    except:
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
