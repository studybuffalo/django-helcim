"""Django settings file to get basic Django instance running."""
# pylint: disable=unused-wildcard-import

import environ

from oscar import OSCAR_MAIN_TEMPLATE_DIR, get_core_apps
from oscar.defaults import * # pylint: disable=wildcard-import

# SETTINGS FILE
# Add all secret setting variables to a config.env file in the
# test directory
ROOT_DIR = environ.Path(__file__) - 1
PACKAGE_DIR = environ.Path(__file__) - 2
ENV = environ.Env()
ENV.read_env(env_file=ROOT_DIR.file("config.env"))

# DEBUG SETTINGS
# Used for sandbox - DO NOT USE IN PRODUCTION
DEBUG = True
TEMPLATE_DEBUG = True
SQL_DEBUG = True

# BASE DJANGO SETTINGS
SECRET_KEY = ENV('DJANGO_SECRET_KEY', default='214dfsdf7ughfgdasd3446@FDF46#')

SITE_ID = 1

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'urls'

APPEND_SLASH = True

# ADMIN SETTINGS
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# LOCALIZATION SETTINGS
USE_TZ = True
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-ca'
USE_I18N = True
USE_L10N = True

# DJANGO APPLICATIONS
INSTALLED_APPS = [
    # Django Apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    # External Apps
    'helcim',
    'debug_toolbar',
    'widget_tweaks',
] + get_core_apps([
    'applications.checkout',
])

# DJANGO MIDDLEWARE
MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# DATABASE SETTINGS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(ROOT_DIR.path('db.sqlite3')),
    }
}
ATOMIC_REQUESTS = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# TEMPLATE SETTINGS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            ROOT_DIR.path('templates'),
            OSCAR_MAIN_TEMPLATE_DIR,
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications', # pylint: disable=line-too-long
                'oscar.core.context_processors.metadata',
            ],
        }
    }
]

# MEDIA SETTINGS
MEDIA_ROOT = ROOT_DIR.path('media')
MEDIA_URL = '/media/'

# STATIC SETTINGS
STATIC_URL = '/static/'
STATIC_ROOT = ROOT_DIR.path('/static/')

# AUTHENTICATION SETTINGS
AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_REDIRECT_URL = '/accounts/'

# LOGGING CONFIGURATION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'oscar.checkout': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG',
        },
    }
}

# OSCAR SETTINGS
OSCAR_ALLOW_ANON_CHECKOUT = True
OSCAR_SHOP_TAGLINE = 'Helcim'

# DJANGO-HELCIM SETTINGS
HELCIM_API_TEST = ENV('HELCIM_API_TEST', default=True)
HELCIM_API_URL = ENV('HELCIM_API_URL', default='')
HELCIM_ACCOUNT_ID = ENV('HELCIM_ACCOUNT_ID', default='')
HELCIM_API_TOKEN = ENV('HELCIM_API_TOKEN', default='')
HELCIM_TERMINAL_ID = ENV('HELCIM_TERMINAL_ID', default='')
