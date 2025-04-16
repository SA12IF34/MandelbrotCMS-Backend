from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import *
from .models import Account, AccountSettings
from .serializers import AccountSerializer, SettingsSerializer
from django.contrib.auth import login, logout, authenticate
from rest_framework.authentication import SessionAuthentication

from django.conf import settings

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

import datetime
import requests

# Social Authentication

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter

@api_view(['POST'])
@permission_classes([AllowAny])
def get_github_access_token(request):
    try:
        response = requests.post('https://github.com/login/oauth/access_token', {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': request.data['code']
        })

        if (response.text.startswith('error')):
            return Response(status=HTTP_400_BAD_REQUEST)
        
        else:
            access_token = response.text.split('&')[0].split('=')[1]

            return Response(data={'access_token': access_token}, status=HTTP_200_OK)
        
    except:
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)




# JWT Authentication

class TokenObtainPairSerializerChan(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email

        return token
    
class TokenObtainPairViewChan(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerChan

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == HTTP_200_OK:
            refresh_token = response.data.get('refresh', None)
            access_token = response.data.get('access', None)

            if refresh_token and access_token:
                # Set cookies in the response
                response.set_cookie('refresh_token', refresh_token)  
                response.set_cookie('access_token', access_token)  

        return response

class TokenRefreshAPI(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == HTTP_200_OK:
            refresh_token = response.data.get('refresh', None)
            access_token = response.data.get('access', None)

            if refresh_token and access_token:
                # Set cookies in the original response
                response.set_cookie('refresh_token', refresh_token, max_age=datetime.timedelta(days=30), samesite=None, secure=True, httponly=True)  
                response.set_cookie('access_token', access_token, max_age=datetime.timedelta(days=90), samesite=None, secure=True, httponly=True)  

        return response

def authenticateJWT(user):
    refresh = RefreshToken.for_user(user)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class SignUpJWTAPI(APIView):

    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        if not Account.objects.filter(email=request.data['email']).exists():
            try:
                if data['username'] and data['email'] and data['password']:
                    data = request.data
                    user = Account.objects.create_user(email=data['email'], username=data['username'].lower(), password=data['password'])

                    auth_creds = authenticateJWT(user)

                    response = Response(data=auth_creds, status=HTTP_200_OK)
                    response.set_cookie('access_token', auth_creds['access'], max_age=datetime.timedelta(days=30), samesite=None, secure=True, httponly=True)
                    response.set_cookie('refresh_token', auth_creds['refresh'], max_age=datetime.timedelta(days=90), samesite=None, secure=True, httponly=True)

                    return response

                return Response(data={'data': 2}, status=HTTP_400_BAD_REQUEST)
            
            except KeyError:
                return Response(data={'data': 2}, status=HTTP_400_BAD_REQUEST)

            except Exception as err:
                return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(data={'data': 1}, status=HTTP_400_BAD_REQUEST)
    

# Session Based Authentication

class RegisterAPI(APIView): 

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    
    def post(self, request):
        data = request.data

        # Checks if user exists or not
        condition_1 = not Account.objects.filter(email=data['email']).exists()
        # Checks if all required fields are filled
        condition_2 = data['username'] and data['email'] and data['password']

        if condition_1:
            if not condition_2:
                return Response(data={'data': 2}, status=HTTP_400_BAD_REQUEST)
            
            user = Account.objects.create_user(email=data['email'], username=data['username'].lower(), password=data['password'])
            login(request, user)
                            
            return Response(status=HTTP_200_OK)
                    
        else :
            return Response(data={"data": 1}, status=HTTP_400_BAD_REQUEST)
    
class AuthenticationAPI(APIView):

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        data = dict(request.data).copy()

        if Account.objects.filter(email=data['email']).exists():
            user = authenticate(email=data['email'], password=data['password'])

            if user is not None:
                login(request, user)

                return Response(status=HTTP_200_OK)

        return Response(data={"response": "user not found"}, status=HTTP_404_NOT_FOUND)


class SettingsAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        user = request.user
        serializer = SettingsSerializer(instance=user.settings)

        return Response(data=serializer.data, status=HTTP_200_OK)

    def patch(self, request):
        user = request.user
        data = request.data

        serializer = SettingsSerializer(instance=user.settings, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(data=serializer.data, status=HTTP_202_ACCEPTED)
        
        return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)


# Logout & Close account APIs | Session Based & JWT

class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def post(self, request):
        logout(request=request)

        response = Response(status=HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
    

class CloseAccountAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def post(self, request):
        user = request.user
        
        logout(request=request)
        user.delete()

        response = Response(status=HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


# General APIs

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def account(request):
    if request.method == 'GET':
        user = request.user
        serializer = AccountSerializer(instance=user)
        settings_serializer = SettingsSerializer(instance=user.settings)

        data = serializer.data
        data['settings'] = settings_serializer.data

        return Response(data=data, status=HTTP_200_OK)

    if request.method == 'PATCH':
        user = request.user
        data = request.data

        if 'password' in data.keys():
            try:
                Account.objects.get(id=user.id).set_password(data['password'])
                Account.save()
                data.pop('password')

                if len(data) >= 1:
                    serializer = AccountSerializer(instance=user, data=data, partial=True)

                    if serializer.is_valid():
                        serializer.save()

                    else:
                        return Response(data={'data': 2}, status=HTTP_400_BAD_REQUEST)
                
                return Response(data=serializer.data, status=HTTP_202_ACCEPTED)
            
            except Exception as err:
                return Response(data={'error': err}, status=HTTP_500_INTERNAL_SERVER_ERROR)

        elif len(data) >= 1:
            if 'picture' in data.keys():
                user.picture.delete(save=True)
                
            serializer = AccountSerializer(instance=user, data=data, partial=True)
            
            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=HTTP_202_ACCEPTED)
            else:
                return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
                

        return Response(data={'data': 1}, status=HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([AllowAny])
def check_auth(request):
    
    if request.user.is_authenticated:
        return Response(status=HTTP_200_OK)
    
    return Response(status=HTTP_401_UNAUTHORIZED)


