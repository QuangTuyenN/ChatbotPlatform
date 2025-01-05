import os.path
from pathlib import Path
import os
from datetime import timedelta
from typing import List, Tuple

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE_DIR is", BASE_DIR)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(" ")

CSRF_TRUSTED_ORIGINS = [os.environ.get(
    "CSRF_TRUSTED_ORIGINS", "https://cbpapi.prod.dev")]

CORS_ALLOWED_ORIGINS = [
    "http://*",  # Cho phép tất cả các origin có scheme là http
    "https://*",  # Cho phép tất cả các origin có scheme là https
]
CORS_ALLOW_ALL_ORIGINS = True  # Tắt chế độ cho phép tất cả các origin

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    # 'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'storages',
    # 'accounts.apps.AccountsConfig',
    'account',
    'bot',
    'mymap',
    'django_crontab',
    'menu'
]

CRONJOBS = [
    ('0 8 * * *', 'core.cron.auto_delete_data'),
    ('0 5 * * 0', 'core.cron.auto_create_partition_event')
]

PSQLEXTRA_PARTITIONING_MANAGER = 'core.partitioning.manager'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 50,

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # IsAuthenticated
    # IsAuthenticated
    # IsAdminUser
    # IsAuthenticatedOrReadOnly
    # DjangoModelPermissions
    # DjangoModelPermissionsOrAnonReadOnly
    # DjangoObjectPermissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],

    'DEFAULT_THROTTLE_RATES': {
        'anon': None,
        'user': None
    },

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': os.environ.get("SWAGGER_UI_NAME", "Chatbot platform Django Backend API"),
    'DESCRIPTION': 'Copyright belongs to Quang Tuyen',
    'VERSION': 'v1',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    "SCHEMA_PATH_PREFIX": r"/api/*"
}

AUTH_USER_MODEL = 'account.Account'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# CORS_ALLOW_ALL_ORIGINS = True

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

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE", 'psqlextra.backend'),
        'NAME': os.environ.get("SQL_DATABASE", 'ai-rasa'),
        'USER': os.environ.get("SQL_USER", 'admin'),
        'PASSWORD': os.environ.get("SQL_PASSWORD", 'quangtuyennguyen'),
        # or the IP address of your PostgreSQL server
        'HOST': os.environ.get("SQL_HOST", '10.14.16.30'),
        # the default PostgreSQL port
        'PORT': os.environ.get("SQL_PORT", '30204'),
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_L10N = True

USE_TZ = True


SIMPLE_JWT = {
    # This setting is to custom the response body of Default JWT's token
    "TOKEN_OBTAIN_SERIALIZER": "account.serializers.MyTokenObtainPairSerializer",

    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # If True, users will be keep to not logout as long as they still open the web app
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,

    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'buithikieu16tclc3@gmail.com'
EMAIL_HOST_PASSWORD = 'gjky zfkr bmto llqx'
DEBUG = True


DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioacesskey")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "quangtuyennguyen")
MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "chatbotplatform")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://10.14.16.30:31003").strip().rstrip('/')
MINIO_CUSTOM_DOMAIN = os.environ.get("MINIO_CUSTOM_DOMAIN", 'minioupload.prod.dev/chatbotplatform')

if not MINIO_CUSTOM_DOMAIN.startswith('http://'):
    MINIO_CUSTOM_DOMAIN = f"http://{MINIO_CUSTOM_DOMAIN}"

AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
AWS_S3_ENDPOINT_URL = MINIO_ENDPOINT
AWS_S3_CUSTOM_DOMAIN = MINIO_CUSTOM_DOMAIN  # Sử dụng MINIO_ENDPOINT mà không có dấu gạch chéo
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False

STATIC_URL = f"{AWS_S3_CUSTOM_DOMAIN}/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'chatbotplatform')

MEDIA_URL = f"{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
