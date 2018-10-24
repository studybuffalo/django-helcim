"""Django settings file to get basic Django instance running."""
# pylint: disable=unused-wildcard-import

from oscar import OSCAR_MAIN_TEMPLATE_DIR, get_core_apps
from oscar.defaults import * # pylint: disable=wildcard-import

# DJANGO-OSCAR-HELCIM SETTINGS
HELCIM_ACCOUNT_ID = '123456789'
HELCIM_API_URL = 'https://www.test.com/'
HELCIM_API_TOKEN = '123456789'
HELCIM_TERMINAL_ID = '12345'

# BASE DJANGO SETTINGS
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz123456789'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'helcim',
] + get_core_apps()

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
)

DEBUG = False
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
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

SITE_ID = 1
ROOT_URLCONF = 'tests.urls'

STATIC_URL = '/'
STATIC_ROOT = '/static/'