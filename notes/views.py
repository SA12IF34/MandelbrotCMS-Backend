from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from Parent.utils import get_all_objs, get_obj_by, patch_update_obj, delete_obj
from .models import Note
from .serializers import NoteSerializer


class NotesAPIs(APIView):
    """
    API view for handling notes-related operations.
    """
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        search_param = request.query_params.get('search', None)
        if search_param is not None:
            if search_param == '':
                return Response(data=[], status=200)
            # Filter notes based on the search parameter
            notes = Note.objects.filter(
                Q(title__contains=search_param) 
                | Q(title__iexact=search_param) 
                | Q(content__contains=search_param) 
                | Q(content__iexact=search_param), 
                user=request.user.id)
            
            serializer = NoteSerializer(instance=notes, many=True)
            return Response(data=serializer.data, status=200)

        data = get_all_objs(Note, NoteSerializer, request.user.id, '-create_date')

        return Response(data=data, status=200)

    def post(self, request):

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = NoteSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(data=serializer.data, status=201)
        
        except serializers.ValidationError:
            return Response(data=serializer.errors, status=400)
        
        except:
            return Response(status=500)


class NoteAPIs(APIView):
    """
    API view for handling operations on a single note.
    """
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            note, data = get_obj_by(Note, NoteSerializer, request.user.id, {'id': pk})

            return Response(data=data, status=200)
        
        except Note.DoesNotExist:
            return Response(status=404)


    def patch(self, request, pk):

        try:
            data = request.data.dict()
            if 'uploaded_file' not in request.data:
                data['uploaded_file'] = None

            if 'drawn_content' not in request.data:
                data['drawn_content'] = None
            
            data = patch_update_obj(Note, NoteSerializer, request.user.id, {'id': pk}, data)
            return Response(data=data, status=202)
        
        except Note.DoesNotExist:
            return Response(status=404)
        
        except serializers.ValidationError:
            return Response(status=400)        
        
        # except:
        #     return Response(status=500)
        
    
    def delete(self, request, pk):
        try:
            delete_obj(Note, request.user.id, {'id': pk})
            return Response(status=204)
        
        except Note.DoesNotExist:
            return Response(status=404)
        
        except:
            return Response(status=500)
        
