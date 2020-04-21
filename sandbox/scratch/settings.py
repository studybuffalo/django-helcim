"""Django settings file to get basic Django instance running."""
import environ


# SETTINGS FILE
# ----------------------------------------------------------------------------
# Add all secret setting variables to a config.env file in the
# test directory
ROOT_DIR = environ.Path(__file__) - 1
PACKAGE_DIR = environ.Path(__file__) - 2
ENV = environ.Env()
ENV.read_env(env_file=ROOT_DIR.file('config.env'))


# DEBUG SETTINGS
# ----------------------------------------------------------------------------
# Used for sandbox - DO NOT USE IN PRODUCTION
DEBUG = True
TEMPLATE_DEBUG = True
SQL_DEBUG = True


# BASE DJANGO SETTINGS
# ----------------------------------------------------------------------------
SECRET_KEY = ENV('DJANGO_SECRET_KEY', default='214dfsdf7ughfgdasd3446@FDF46#')
SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)
ROOT_URLCONF = 'urls'
APPEND_SLASH = True


# ADMIN SETTINGS
# ----------------------------------------------------------------------------
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS


# EMAIL SETTINGS
# ----------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# LOCALIZATION SETTINGS
# ----------------------------------------------------------------------------
USE_TZ = True
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-ca'
LANGUAGES = (
    ('en-ca', 'English'),
)
USE_I18N = True
USE_L10N = True


# DJANGO APPLICATIONS
# ----------------------------------------------------------------------------
INSTALLED_APPS = (
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    # External Apps
    'helcim',
    'debug_toolbar',
    # Project Apps
    'example_app.apps.ExampleAppConfig',
)

# DJANGO MIDDLEWARE
# ----------------------------------------------------------------------------
MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


# DATABASE SETTINGS
# ----------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            ROOT_DIR.path('templates'),
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
            ],
        }
    }
]


# MEDIA SETTINGS
# ----------------------------------------------------------------------------
MEDIA_ROOT = ROOT_DIR.path('media')
MEDIA_URL = '/media/'


# STATIC SETTINGS
# ----------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = ROOT_DIR.path('static')


# AUTHENTICATION SETTINGS
# ----------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_REDIRECT_URL = '/accounts/'


# DJANGO-HELCIM SETTINGS
# ----------------------------------------------------------------------------
HELCIM_API_TEST = ENV('HELCIM_API_TEST', default=True)
HELCIM_API_URL = ENV('HELCIM_API_URL', default='')
HELCIM_ACCOUNT_ID = ENV('HELCIM_ACCOUNT_ID', default='')
HELCIM_API_TOKEN = ENV('HELCIM_API_TOKEN', default='')
HELCIM_TERMINAL_ID = ENV('HELCIM_TERMINAL_ID', default='')
HELCIM_JS_CONFIG = {
    'purchase': {
        'url': ENV('HELCIM_JS_PURCHASE_URL', default=''),
        'token': ENV('HELCIM_JS_PURCHASE_TOKEN', default='1234567890'),
    },
}
HELCIM_ENABLE_TRANSACTION_CAPTURE = ENV(
    'HELCIM_ENABLE_TRANSACTION_CAPTURE', default=True
)
HELCIM_ENABLE_TRANSACTION_REFUND = ENV(
    'HELCIM_ENABLE_TRANSACTION_REFUND', default=True
)
HELCIM_ENABLE_TOKEN_VAULT = ENV('HELCIM_ENABLE_TOKEN_VAULT', default=True)
HELCIM_REDACT_ALL = ENV('HELCIM_REDACT_ALL', default=True)
