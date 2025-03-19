from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from .models import Project, Partition
from .serializers import ProjectSerializer, PartitionSerializer

from Parent.utils import *

import datetime


class ProjectsAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request):
        user = request.user.id
        try:

            search_query = request.query_params.get('search', None)
            if search_query is not None:
                projects = Project.objects.filter(Q(title__contains=search_query) | Q(title__iexact=search_query), user=user)
                serializer = ProjectSerializer(instance=projects, many=True)

                return Response(data=serializer.data, status=HTTP_200_OK)

            all_projects = get_all_objs(Project, ProjectSerializer, user, '-update_date')

            return Response(data=all_projects, status=HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response(data=[], status=HTTP_200_OK)

        except:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            project_data = request.data['project']
            project_data['user'] = request.user.id

            partitions_data = request.data['partitions']

            serializer = ProjectSerializer(data=project_data)
            if serializer.is_valid():
                serializer.save()
                project = serializer.data['id']
                
                try:
                    if len(partitions_data) > 0:
                        for partition in partitions_data:
                            data = partition
                            data['project'] = project 
                            
                            serializer = PartitionSerializer(data=data)
                            if serializer.is_valid(raise_exception=True):
                                serializer.save()
                        
                        return Response(data={'id': project}, status=HTTP_201_CREATED)
                    
                    else:
                        raise ValidationError()
                
                except ValidationError:
                    return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
                


            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
        
        except KeyError:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

def get_projects_on_status(user, status):
    try:
        projects = Project.objects.filter(user=user, status=status).order_by('-update_date')
        serializer = ProjectSerializer(instance=projects, many=True)

        return serializer.data

    except Project.DoesNotExist:
        return []


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
def get_completed(request):
    try:
        data = get_objs_filter(Project, ProjectSerializer, request.user.id, '-update_date', {'status': 'completed'})

        return Response(data=data, status=HTTP_200_OK)
    except:
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
def get_in_progress(request):
    try:
        data = get_objs_filter(Project, ProjectSerializer, request.user.id, '-update_date', {'status': 'in progress'})

        return Response(data=data, status=HTTP_200_OK)
    
    except Exception as err:
        return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)



class ProjectAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request, id):
        try:
            project, project_data = get_obj_by(Project, ProjectSerializer, request.user.id, {'id': id})
            partitions = project.partition_set.all()


            partitions_serializer = PartitionSerializer(instance=partitions, many=True)

            project_data['partitions'] = partitions_serializer.data

            return Response(data=project_data, status=HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, id):
        try:
            patch_update_obj(Project, ProjectSerializer, request.user.id, {'id': id}, request.data) 
            
            return Response(status=HTTP_202_ACCEPTED)

        except ValidationError:
            return Response(status=HTTP_400_BAD_REQUEST)    

        except Project.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def delete(self, request, id):
        try:
            delete_obj(Project, request.user.id, {'id': id})

            return Response(status=HTTP_204_NO_CONTENT)

        except Project.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class PartitionAPIs(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def patch(self, request, id):
        try:
            data = dict(request.data).copy()
            partition = Partition.objects.get(id=id)
            
            serializer = PartitionSerializer(data=data, instance=partition, partial=True)
            if serializer.is_valid():
                serializer.save()

                project = Project.objects.get(id=serializer.data['project'])
                done_partitions = Partition.objects.filter(project=project.id, done=True).count()
                all_partitions = Partition.objects.filter(project=project.id).count()

                if done_partitions == all_partitions:
                    serializer = ProjectSerializer(instance=project, data={
                    'status':'completed',
                    'finish_date': datetime.date.today()
                    }, partial=True)
                
                    if serializer.is_valid():
                        serializer.save()

                        return Response(data={'data': 'done'}, status=HTTP_200_OK)

                    return Response(data={'error': 'project update error after partition update'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
                
                if done_partitions == 1:
                    serializer = ProjectSerializer(instance=project, data={
                    'start_date': datetime.date.today()
                    }, partial=True)
                
                    if serializer.is_valid():
                        serializer.save()

                        return Response(data={'data': 'started'}, status=HTTP_200_OK)

                    return Response(data={'error': 'project update error after partition update'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

                return Response(status=HTTP_202_ACCEPTED)
            
            return Response(status=HTTP_400_BAD_REQUEST)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, id):
        try:
            partition = Partition.objects.get(id=id)
            isOne = True if len(partition.project.partition_set.all()) == 1 else False

            partition.delete()

            if isOne:
                return Response(status=HTTP_204_NO_CONTENT)

            return Response(status=HTTP_202_ACCEPTED)
        
        except Exception as err:
            return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)




            


