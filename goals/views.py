from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.status import *
from django.db.models import Q

from .models import Goal
from .serializers import GoalSerializer
from rest_framework.serializers import ValidationError

import Parent.utils as orm
from .utils import *

class GoalsAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request):

        search_query = request.query_params.get('search', None)
        if search_query is not None:
            goals = Goal.objects.filter(Q(title__contains=search_query) | Q(title__iexact=search_query), user=request.user.id)
            serializer = GoalSerializer(instance=goals, many=True)

            return Response(data=serializer.data, status=HTTP_200_OK)
        

        goals = orm.get_all_objs(
            Goal, GoalSerializer,
            request.user.id,
            '-update_date'
        )


        return Response(data=goals, status=HTTP_200_OK)
    

    def post(self, request):
        try:
            data = request.data
            data['user'] = request.user.id
            
            if 'missions' in data:
                mission_ids = []
                try:
                    mission_ids = create_indivisual_missions(data['missions'])
                except ValidationError:
                    return Response(status=HTTP_400_BAD_REQUEST)
            
                data['missions'] = mission_ids
            
            serializer = GoalSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                if len(serializer.data['rewards']) > 0:
                    try:
                        lockEntertainment(serializer.data['rewards'], serializer.data['id'])
                    except ValidationError:
                        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response(data=serializer.data, status=HTTP_201_CREATED)
            
            return Response(status=HTTP_400_BAD_REQUEST)

        except:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class GoalAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request, pk):
        try:
            goal, data = orm.get_obj_by(
                Goal, GoalSerializer,
                request.user.id,
                {'id': pk}
            )

            progress = calculateProgress(data)
            
            if progress[0] == 100 :
                try:
                    serializer = GoalSerializer(instance=goal, data={'done': True}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        data = serializer.data

                        unlockEntertainment(data['rewards'])
                except ValidationError:
                    return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
            
            elif progress[0] < 100 and data['done']:
                try:
                    serializer = GoalSerializer(instance=goal, data={'done': False}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        data = serializer.data

                        lockEntertainment(data['rewards'], data['id'])
                except ValidationError:
                    return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
            

            data['progress'] = progress[0]

            data['rewards'] = get_rewards(data['rewards'])
            data['projects'] = get_projects(data['projects'])
            data['courses'] = get_courses(data['courses'])
            data['missions'] = get_missions(data['missions'])

            return Response(data=data, status=HTTP_200_OK)
        
        except Goal.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
    

    def patch(self, request, pk):
        try:
            goal = Goal.objects.get(user=request.user.id, id=pk)
            serializer = GoalSerializer(instance=goal, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response(status=HTTP_202_ACCEPTED)
            
            return Response(status=HTTP_400_BAD_REQUEST)

        except Goal.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        try:
            goal = Goal.objects.get(id=pk)
            
            unlockEntertainment(goal.rewards)
            goal.delete()

            return Response(status=HTTP_204_NO_CONTENT)

        except Goal.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        

