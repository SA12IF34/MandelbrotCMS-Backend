from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.status import *
from django.db.models import Q


from .models import Entertainment, TYPE_CHOICES
from .serializers import EntertainmentSerializer
from rest_framework.serializers import ValidationError

import Parent.utils as orm
from .utils import *


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_material_by_link(request):
    if 'link' in request.data and 'status' in request.data:
        if 'myanimelist' in request.data['link']:
            data, relatives = get_mal(request.data['link'])

        elif 'anilist' in request.data['link']:
            data, relatives = get_anilist(request.data['link'])

        elif 'steam' in request.data['link']:
            data, relatives = get_steam(request.data['link'])

        elif 'rottentomatoes' in request.data['link']:
            data, relatives = get_rottentomatoes(request.data['link'])

        else:
            return Response(data={'data': 'invalid link'}, status=HTTP_400_BAD_REQUEST)

        data['user'] = request.user.id
        data['status'] = request.data['status']

        main_serializer = EntertainmentSerializer(data=data)
        if main_serializer.is_valid():
            main_serializer.save()

            id_list = []

            try:
                for material in relatives:
                    material['user'] = request.user.id
                    serializer = EntertainmentSerializer(data=material)
                    
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()

                        id_list.append(serializer.data['id'])
            
            except ValidationError:
                return Response(data=serializer.errors, status=HTTP_500_INTERNAL_SERVER_ERROR)

            
            main_entry = Entertainment.objects.get(id=main_serializer.data['id'])
            data = main_serializer.data


            main_serializer = EntertainmentSerializer(instance=main_entry, data=data)
            if main_serializer.is_valid():
                main_serializer.save()

                id_list.append(main_serializer.data['id'])

                for id_ in id_list:
                    material = Entertainment.objects.get(id=id_)
                    material.relatives.set(list(filter(lambda x: x!= id_, id_list)))
                    material.save()

                return Response(data=main_serializer.data, status=HTTP_201_CREATED)
            
            return Response(data=main_serializer.errors, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(data=main_serializer.errors, status=HTTP_400_BAD_REQUEST)


    return Response(data={'data': 'data required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_material_manually(request):
    data = request.data
    data['user'] = request.user.id
    main_serializer = EntertainmentSerializer(data=data)
    
    if main_serializer.is_valid():
        main_serializer.save()
        
        id_ = main_serializer.data['id']
        ids_list = []
         
        if 'relatives' in data:
            try:
                for entry in data:
                    serializer = EntertainmentSerializer(data=entry)
                    
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        ids_list.append(serializer.data['id'])
    
            except ValidationError:
                return Response(data={'data': 'relatives'}, status=HTTP_400_BAD_REQUEST)
    
            main_serializer = EntertainmentSerializer(
                instance=Entertainment.objects.get(id=id_), data={'relatives': ids_list}, partial=True)
    
            if main_serializer.is_valid():
                main_serializer.save()
        
        return Response(data=main_serializer.data, status=HTTP_201_CREATED)
    
    return Response(data=main_serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_materials(request):
    data = {
        'current': {},
        'done': {},
        'future': {}
    }

    for type_ in TYPE_CHOICES:
        params = {
            'model': Entertainment,
            'modelSerializer': EntertainmentSerializer,
            'user': request.user.id,
            'order_by': '-update_date'
        }
        
        current = orm.get_objs_filter(**params, conditions={'type': type_[0], 'status': 'current'})
        done = orm.get_objs_filter(**params, conditions={'type': type_[0], 'status': 'done'})
        future = orm.get_objs_filter(**params, conditions={'type': type_[0], 'status': 'future'})

        data['current'][type_[0]] = current 
        data['done'][type_[0]] = done
        data['future'][type_[0]] = future

    return Response(data=data, status=HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_special_materials(request):
    data = {}

    for type_ in TYPE_CHOICES:
        materials = orm.get_objs_filter(
            model=Entertainment,
            modelSerializer=EntertainmentSerializer,
            user=request.user.id,
            order_by='-update_date',
            conditions={'special': True, 'type': type_[0]}
        )

        data[type_[0]] = materials

    return Response(data=data, status=HTTP_200_OK)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def material_operations(request, pk):
    try:
        material = Entertainment.objects.get(user=request.user.id, id=pk)

        if request.method == 'GET':
            serializer = EntertainmentSerializer(instance=material)

            relatives = Entertainment.objects.filter(id__in=serializer.data['relatives'])
            relatives_serializer = EntertainmentSerializer(instance=relatives, many=True)

            data = serializer.data
            data['relatives'] = relatives_serializer.data

            return Response(data=data, status=HTTP_200_OK)

        if request.method == 'PATCH':
            serializer = EntertainmentSerializer(instance=material, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=HTTP_202_ACCEPTED)
            
            return Response(status=HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            material.delete()

            return Response(status=HTTP_204_NO_CONTENT)
    except Entertainment.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_materials(request):
    user = request.user.id
    search_query = request.query_params.dict()
    keys = search_query.keys()

    allowed_keys = {'title', 'type', 'subtype', 'status', 'special', 'rate', 'user_rate', 'genres'}
    not_allowed_keys = []
    genres_query = Q()
    rate_query = Q()
    title_query = Q()
    query = Q()


    for key in keys:
        try:
            if key not in allowed_keys or search_query[key] == '':
                not_allowed_keys.append(key)
                continue

            if key == 'title':
                title_query = Q(title__contains=search_query[key]) | Q(title__iexact=search_query[key])
                query |= title_query

                not_allowed_keys.append(key)

            if key == 'genres':
                genres = set(g.upper() if g == 'cgdct' else g.capitalize() 
                    for g in search_query[key].split(','))
                
                materials_with_genres = Entertainment.objects.filter(user=user)
                materials_with_genres = [
                    material for material in materials_with_genres 
                    if all(genre in material.genres for genre in genres)
                ]

                valid_ids = [material.id for material in materials_with_genres]
                genres_query = Q(id__in=valid_ids)
                
                query = (query) & genres_query

                not_allowed_keys.append(key)

            if key == 'rate' or key == 'user_rate':
                if key == 'rate':
                    rate_query &= Q(rate__gte=search_query[key])

                if key == 'user_rate':
                    rate_query &= (Q(user_rate__gte=search_query[key]))
                
                query = (query) & rate_query

                not_allowed_keys.append(key)

            if key == 'special':
                if search_query['special'] == 'true': search_query['special'] = True
                else: not_allowed_keys.append('special')

        except KeyError:
            pass

    try:
        for key in not_allowed_keys:
            del search_query[key]
    except KeyError:
        return Response(data=[], status=HTTP_200_OK)

    materials = Entertainment.objects.filter(query, user=user, **search_query).order_by('-update_date')
    serializer = EntertainmentSerializer(instance=materials, many=True)

    return Response(data=serializer.data, status=HTTP_200_OK)