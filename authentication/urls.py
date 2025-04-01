from django.urls import path
from .views import (
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