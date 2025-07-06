from pathlib import Path
import os
import environ
from datetime import timedelta

ENV = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


if DEBUG:
    ALLOWED_HOSTS = ['*']
    DOMAIN = '192.168.100.8'
else:
    ALLOWED_HOSTS = ['cms.saifchan.online']
    DOMAIN = '.cms.saifchan.online'

CSRF_COOKIE_DOMAIN = DOMAIN
SESSION_COOKIE_DOMAIN = DOMAIN

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:4173',
        'http://127.0.0.1:10000',
        'http://localhost:10000',
        'http://192.168.100.8:5173'
    ]
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:4173',
        'http://127.0.0.1:10000',
        'http://localhost:10000',
        'http://192.168.100.8:5173'
    ]
    CORS_ORIGIN_WHITELIST = [
        'http://localhost:5173',
        'http://192.168.100.8:5173'
    ]

else:
    CORS_ALLOWED_ORIGINS = [
        'https://cms.saifchan.online',
        'https://api.cms.saifchan.online',
        'https://saifchan.online',
        'null',
        'None'

    ]
    CSRF_TRUSTED_ORIGINS = [
        'https://cms.saifchan.online',
        'https://api.cms.saifchan.online',
        'https://saifchan.online',
        'null',
        'None'
    ]
    CORS_ORIGIN_WHITELIST = [
        'https://cms.saifchan.online',
        'https://api.cms.saifchan.online',
        'https://saifchan.online',
        'null',
        'None'
    ]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with'
]

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

# Application definition

INSTALLED_APPS = [
    'authentication',
    'whitenoise',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',

    # System Apps
    'Parent', # Global app which will contain parential things, like parent model
    'sessions_manager',
    'learning_tracker',
    'entertainment',
    'missions',
    'goals',
    'notes',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
]

if DEBUG:
    SITE_ID = 3
else:
    SITE_ID = 4

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'allauth.account.middleware.AccountMiddleware'
]

CLIENT_ID = ENV('GOOGLE_CLIENT_ID')
CLIENT_SECRET = ENV('GOOGLE_CLIENT_SECRET')
GITHUB_CLIENT_ID = ENV('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = ENV('GITHUB_CLIENT_SECRET')

ROOT_URLCONF = 'core.urls'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": ENV('JWT_ALGORITHM'),
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'Frontend/dist'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/home/db/db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'authentication.Account'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

if DEBUG:
    MEDIA_ROOT = BASE_DIR/'media'
    MEDIA_URL = '/media/'

else:

    MEDIA_ROOT = BASE_DIR/'media'
    MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR/'staticfiles'
STATIC_URL = '/assets/'
STATICFILES_DIRS = [
  BASE_DIR/'Frontend/dist/assets'
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
