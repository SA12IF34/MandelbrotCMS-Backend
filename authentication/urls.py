from django.urls import path, include
from django.views.generic import TemplateView
from .views import (
    # Social
    GoogleLogin,
    GitHubLogin,
    get_github_access_token,

    # JWT
    TokenObtainPairViewChan,
    TokenRefreshAPI,
    SignUpJWTAPI,
    
    # Session Based
    RegisterAPI,
    AuthenticationAPI,
    
    # General
    SettingsAPI,
    LogoutAPI,
    CloseAccountAPI,
    account,
    check_auth
)

urlpatterns = [
    # Social Auth Paths
    path('apis/rest-auth/', include('dj_rest_auth.urls')),
    path('apis/rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('apis/rest-auth/google/', GoogleLogin.as_view()),
    path('apis/rest-auth/github/', GitHubLogin.as_view()),
    path('apis/rest-auth/access_token/github/', get_github_access_token),

    # JWT Paths
    path('apis/jwt/login/', TokenObtainPairViewChan.as_view()),
    path('apis/jwt/refresh-token/', TokenRefreshAPI.as_view()),
    path('apis/jwt/signup/', SignUpJWTAPI.as_view()),

    # Session Based Paths
    path('apis/login/', AuthenticationAPI.as_view()),
    path('apis/signup/', RegisterAPI.as_view()),

    # General Paths
    path('apis/logout/', LogoutAPI.as_view()),
    path('apis/close/', CloseAccountAPI.as_view()),
    path('apis/settings/', SettingsAPI.as_view()),
    path('apis/my-account/', account),
    path('apis/check-auth/', check_auth)

]