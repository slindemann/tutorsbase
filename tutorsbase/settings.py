"""
Django settings for tutorsbase project.

Generated by 'django-admin startproject' using Django 2.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
#import logging.config
#from django.utils.log import DEFAULT_LOGGING
#LOGGING_CONFIG = None
#LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$+-pdchscf-_t2(*uo&fn7fvv3ivs_%pugtnj+wz63#72l!#zj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','0.0.0.0','10.4.73.214','192.168.178.45']

# SESSION SETTING

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 5 * 60

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # For production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development only
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/home/sebastian/Computing/tutorsbase_ex1/tmp'
# Python has a little SMTP server built-in. You can start it in a second console with this command:
# python -m smtpd -n -c DebuggingServer localhost:1025
# This will simply print all the mails sent to localhost:1025 in the console.
# You have to configure Django to use this server in your settings.py:
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025


#######################
## CUSTOM STUFF HERE:
CURRENT_EVENT = 'Experimental Physics I'
BCC_MAILTO = ['laurel@har.dy', ]
SEND_CREDIT_UPDATES_TO_STUDENTS = True
##
#######################



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'student_crediting',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tutorsbase.urls'

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

WSGI_APPLICATION = 'tutorsbase.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tb_16Nov',
        'USER': 'sebastian',
#        'USER': 'postgres',
        'PASSWORD': 'sl1082',
        'HOST': 'localhost',
        'PORT': '5432',
    }

}

##LOGGING = {
#logging.config.dictConfig({
#    'version': 1,
#    'disable_existing_loggers': False,
#    'formatters': {
#        'default': {
#            # exact format is not important, this is the minimum information
#            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#        },
#        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
#    },
#    'handlers': {
#        'file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': os.path.join(BASE_DIR, 'logfiles/debug.log'), #'/path/to/django/debug.log',
#        },
#				'console': {
#						'level': 'DEBUG',
#            'class': 'logging.StreamHandler'
#        },
#        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
#    },
#    'loggers': {
#        # default for all undefined Python modules
#        '': {
#            'level': 'WARNING',
#            'handlers': ['console', 'file'],
#        },
#        # Our application code
#        'tutorsbase': {
#            'level': LOGLEVEL,
#            'handlers': ['console', 'file'],
#            # Avoid double logging because of root logger
#            'propagate': False,
#        },
#        # Prevent noisy modules from logging to Sentry
#        'noisy_module': {
#            'level': 'ERROR',
#            'handlers': ['console'],
#            'propagate': False,
#        },
##        'django': {
##            'handlers': ['file'],
##            'level': 'DEBUG',
##            'propagate': True,
##        },
#        # Default runserver request logging
#        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
#    },
#})

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
#    {
#        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#    },
#    {
#        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#    },
#    {
#        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#    },
#    {
#        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


LOGIN_URL = '/student_crediting/login/'
LOGIN_REDIRECT_URL = '/student_crediting/'
