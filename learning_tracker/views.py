from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.status import *
from django.db.models import Q

from .models import Course, Section
from .serializers import CourseSerializer, SectionSerializer

from rest_framework.serializers import ValidationError

import Parent.utils as orm
from .utils import *



class CoursesAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request):
        try:
            search_query = request.query_params.get('search', None)
            if search_query is not None:
                courses = Course.objects.filter(Q(title__contains=search_query) | Q(title__iexact=search_query), user=request.user.id)
                serializer = CourseSerializer(instance=courses, many=True)

                return Response(data=serializer.data, status=HTTP_200_OK)


            params = {
                'model': Course,
                'modelSerializer': CourseSerializer,
                'user': request.user.id,
                'order_by': '-update_date',
            }

            current_courses = orm.get_objs_filter(**params, conditions={'status': 'current'})
            done_courses = orm.get_objs_filter(**params, conditions={'status': 'done'})
            later_courses = orm.get_objs_filter(**params, conditions={'status': 'later'})

            data = {
                'current': current_courses,
                'done': done_courses,
                'later': later_courses
            }

            return Response(data=data, status=HTTP_200_OK)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):

        if is_invalid(request.data):
            return Response(data={'data': 1}, status=HTTP_400_BAD_REQUEST)
        
        if 'status' not in request.data:
            return Response(data={'data': 2}, status=HTTP_400_BAD_REQUEST)
        

        if 'youtube' in request.data['link'] or 'youtu.be' in request.data['link']:
            data, sections = get_youtube(request.data['link'])
            data['source'] = 'youtube'

        if 'coursera' in request.data['link']:
            try:
                data, sections = get_coursera(request.data['link'])
                data['source'] = 'coursera'
            except ValueError:
                return Response(data={'data': 'only course'}, status=HTTP_400_BAD_REQUEST)

        data['status'] = request.data['status']
        data['link'] = request.data['link']
        data['user'] = request.user.id

        serializer = CourseSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            
            if serializer.data['list'] and len(sections) > 0:
                for section in sections:
                    section['course'] = serializer.data['id']
                    section_serializer = SectionSerializer(data=section)
                    
                    if section_serializer.is_valid():
                        section_serializer.save()

            return Response(data=serializer.data, status=HTTP_201_CREATED)
        
        return Response(data={'data': 0}, status=HTTP_400_BAD_REQUEST)


class CourseAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request, pk):
        try:
            params = {
                'model': Course,
                'modelSerializer': CourseSerializer,
                'user': request.user.id,
                'by': {'id': pk}
            }

            course, data = orm.get_obj_by(**params)
            serializer = SectionSerializer(instance=course.section_set.all(), many=True)

            data['sections'] = serializer.data

            return Response(data=data, status=HTTP_200_OK)
        
        except Course.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        

    def patch(self, request, pk):
        try:

            data = request.data

            if 'status' in data.keys() and 'done' == data['status']:
                data['progress'] = 100

            orm.patch_update_obj(
                model=Course,
                modelSerializer=CourseSerializer,
                user=request.user.id,
                by={'id': pk},
                new_data=request.data
            )

            return Response(status=HTTP_202_ACCEPTED)

        except ValidationError:
            return Response(status=HTTP_400_BAD_REQUEST)

        except Course.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def delete(self, request, pk):
        try:
            orm.delete_obj(
                model=Course,
                user=request.user.id,
                by={'id': pk}
            )

            return Response(status=HTTP_204_NO_CONTENT)

        except Course.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
def update_section(request, pk):
    try:
        section = Section.objects.get(id=pk)
        serializer = SectionSerializer(instance=section, data=request.data, partial=True)

        if section.course.status == 'done':
            return Response(status=HTTP_406_NOT_ACCEPTABLE)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            course = Course.objects.get(id=serializer.data['course'])
            all_sections = course.section_set.all().count()
            done_sections = course.section_set.filter(done=True).count()

            progress = int((done_sections / all_sections) * 100)

            params = {
                "model": Course,
                "modelSerializer": CourseSerializer,
                "user": request.user.id,
                "by": {"id": course.id},
                "new_data": {
                    "progress": progress
                }
            }

            if done_sections == all_sections:
                params['new_data']['status'] = 'done'
                orm.patch_update_obj(**params)

                return Response(status=HTTP_200_OK)

            orm.patch_update_obj(**params)

            return Response(status=HTTP_202_ACCEPTED)

    except ValidationError:
        return Response(status=HTTP_400_BAD_REQUEST)

    except Exception as err:
        return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def get_course_data(request):
    if is_invalid(request.data):
        return Response(status=HTTP_400_BAD_REQUEST)
    
    if 'coursera' in request.data['link']:
        try:
            data, sections = get_coursera(request.data['link'])
        except ValueError:
            return Response(data={'data': 'only course'}, status=HTTP_400_BAD_REQUEST)
    
    if 'youtube' in request.data['link'] or 'youtu.be' in request.data['link']:
        data, sections = get_youtube(request.data['link'])

    data['sections'] = sections

    return Response(data=data, status=HTTP_200_OK)