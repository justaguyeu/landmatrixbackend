from datetime import timedelta
import os
import dj_database_url
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# import environ 

# env = environ.Env()
# environ.Env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,edsalesbackend.onrender.com,edprinting.netlify.app,*').split(',')

CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:3000,https://edprinting.netlify.app,https://edsalesbackend.onrender.com').split(',')

CORS_ALLOW_ALL_ORIGINS = os.getenv('DJANGO_CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = [
    "Authorization",
    "Content-Type",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
    'gunicorn',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://localhost:3000,https://edprinting.netlify.app').split(',')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise for static file serving
]

ROOT_URLCONF = 'myproject.urls'

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

WSGI_APPLICATION = 'myproject.wsgi.application'
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
#         'NAME': os.getenv('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
#         'USER': os.getenv('DJANGO_DB_USER', ''),
#         'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
#         'HOST': os.getenv('DJANGO_DB_HOST', ''),
#         'PORT': os.getenv('DJANGO_DB_PORT', ''),
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.mysql'),
#         'NAME': os.getenv('DJANGO_DB_NAME', 'edprinting'),  # Your MySQL database name
#         'USER': os.getenv('DJANGO_DB_USER', 'root'),   # MySQL database user
#         'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'justaguyeu@gmail.com@1'),  # MySQL password
#         'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),  # Usually 'localhost' if running locally
#         'PORT': os.getenv('DJANGO_DB_PORT', '3306'),  # Default MySQL port
#     }
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'edprinting',
#         'USER': 'root',
#         'PASSWORD': 'justaguyeu@gmail.com@1',
#         'HOST': '127.0.0.1',
#         'PORT': '3306', 
#     }
# }



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME','edprintingdatabase'),
#         'USER': os.getenv('DB_USER','edprintingdatabase_user'),
#         'PASSWORD': os.getenv('DB_PASSWORD','PHqza1el34uTadezLyCJXM42BQJNK4s6'),
#         'HOST': os.getenv('DB_HOST','dpg-cre2fvrv2p9s73cp8aqg-a'),
#         'PORT': os.getenv('DB_PORT', '5432'),
#     }
# }

DATABASES ={
    'default': dj_database_url.parse('postgresql://landmatrixdatabase_user:IpuiA0BhEkcutRxxr8lfFaS2DNGBnOTS@dpg-csjjtve8ii6s73d4ug10-a.oregon-postgres.render.com/landmatrixdatabase')
}


# TWILIO_ACCOUNT_SID = 'your_account_sid'
# TWILIO_AUTH_TOKEN = 'your_auth_token'
# TWILIO_PHONE_NUMBER = '+1234567890'




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

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static file storage using WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
