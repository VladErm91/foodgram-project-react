# flake8: noqa
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', 'default-value')

DEBUG = os.getenv('DEBUG', default=False)

ALLOWED_HOSTS = '*'

DJANGO = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

API_FOODGRAM = [
    'users.apps.UsersConfig',
    'recipes.apps.RecipesConfig',
    'api.apps.ApiConfig',
]

EXTRA = [
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "djoser",
    "drf_yasg",
    "colorfield",
]
INSTALLED_APPS = DJANGO + API_FOODGRAM + EXTRA

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'foodgram_backend.wsgi.application'

AUTH_USER_MODEL = 'users.User'

DATABASES = {
     'default': {
          'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
           'NAME': os.getenv('DB_NAME', default='postgres'),
           'USER': os.getenv('POSTGRES_USER', default='postgres'),
           'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
           'HOST': os.getenv('DB_HOST', default='localhost'),
           'PORT': os.getenv('DB_PORT', default='5432')
     }
}
  
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

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 6,
}

DJOSER = {
    "SERIALIZERS": {
        "user_create": "api.serializers.CustomUserCreateSerializer",
        "user": "api.serializers.CustomUserSerializer",
        "current_user": "api.serializers.UserSerializer",
    },

    "PERMISSIONS": {
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
        "user_list": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    },
    
    "HIDE_USERS": False,
}

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

##API Variables
LENGTH_FIELD_USER_1 = 150

LENGTH_FIELD_USER_2 = 254

LENGTH_RECIPES = 250

LENGTH_RECIPES_NAME = 75

LENGTH_MEASURE = 10

MAX_COOKING_TIME = 1441

MAX_INGREDIENT_AMOUNT = 32000
## DATA PATHS
INGREDIENTS_PATH = 'data/ingredients.json'

TAGS_PATH = 'data/tags.json'
 

