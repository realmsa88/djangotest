from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# settings.py
STRIPE_PUBLIC_KEY = 'pk_test_51PVtJrBRAMWTFzsQDjmWnal7CiUVKbmOf6ul022YMF1CvJxEgH0f6uFygnLjSx2zUf0cPO5dKiYAw5tbEyBOVbU000kRwEQzG3'
STRIPE_SECRET_KEY = 'sk_test_51PVtJrBRAMWTFzsQ7iCtui1YPpm0iITlHb8H6Vd9wQPB7cHU6poxyFYd3OZz6WO4UcAYmQbcQ67br5agiyUhCtcG00blSpKeNQ'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(" ")


SESSION_COOKIE_AGE = 6000  # 1 hour in seconds

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# AUTH_USER_MODEL = 'your_app.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'message': "Password can’t be too similar to your other personal information."
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
            'message': "Password must contain at least 8 characters."
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        'OPTIONS': {
            'message': "Password can’t be a commonly used password."
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        'OPTIONS': {
            'message': "Password can’t be entirely numeric."
        }
    },
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',
    'assistant',
    'administrator',
    'parent',
    'authentication',
    'teacher', 'tickets'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'chatbot.urls'

# settings.py

# CSRF_COOKIE_SECURE = False
# CSRF_COOKIE_SAMESITE = None


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
            # 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
]

WSGI_APPLICATION = 'chatbot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'newfinalyearproject',
        'USER': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


database_url = os.environ.get("DATABASE_URL")
DATABASES["default"] = dj_database_url.parse(database_url)


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# settings.py


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'productionfiles'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'mystaticfiles',
    BASE_DIR / 'administrator'
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.ap-southeast-2.amazonaws.com'  # SES SMTP endpoint
EMAIL_PORT = 587  # You can use 587 for STARTTLS
EMAIL_HOST_USER = 'AKIA4MTWNWBSXQPA4HNP'  # Your SES SMTP access key
EMAIL_HOST_PASSWORD = 'BIs4mFbTe3ApY/HTgLUdiymqglbJst07gWdaMqv2TOlJ'  # Your SES SMTP secret key
EMAIL_USE_TLS = True  # Use TLS encryption
