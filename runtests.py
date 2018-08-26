"""To Review:
    https://www.b-list.org/weblog/2018/apr/02/testing-django/
    Using tox to test in multiple environments (py36 for Django 1.11, 2.0, 2.1)
    Using the runtests script to handle a minimal django environment
"""
# import os, sys
# from django.conf import settings

# DIRNAME = os.path.dirname(__file__)
# settings.configure(DEBUG = True,
#                    DATABASE_ENGINE = 'sqlite3',
#                    DATABASE_NAME = os.path.join(DIRNAME, 'database.db'),
#                    INSTALLED_APPS = ('django.contrib.auth',
#                                      'django.contrib.contenttypes',
#                                      'django.contrib.sessions',
#                                      'django.contrib.admin',
#                                      'myapp',
#                                      'myapp.tests',))


# from django.test.simple import run_tests

# failures = run_tests(['myapp',], verbosity=1)
# if failures:
#     sys.exit(failures)

# AND/OR

# # Now we instantiate a test runner...
# from django.test.utils import get_runner
# TestRunner = get_runner(settings)

# # And then we run tests and return the results.
# test_runner = TestRunner(verbosity=2, interactive=True)
# failures = test_runner.run_tests(['pwned_passwords_django.tests'])
# sys.exit(failures)

"""SETTINGS THAT MAY BE NEEDED"""
# from oscar import OSCAR_MAIN_TEMPLATE_DIR, get_core_apps
# from oscar.defaults import * # pylint: disable=unused-wildcard-import

# To specify integration settings (which include passwords, hence why they
# are not committed), create an integration.py module.
# try:
#     from integration import *
# except ImportError:
#     PAYPAL_API_USERNAME = ''
#     PAYPAL_API_PASSWORD = ''
#     PAYPAL_API_SIGNATURE = ''
#     PAYPAL_PAYFLOW_VENDOR_ID = ''
#     PAYPAL_PAYFLOW_PASSWORD = ''

# SECRET_KEY = '9%d9&5!^+hcq!pin#0lfz(qj8j2h7y$p*rr-o#cy+)9%dyvwkn'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#     }
# }
# INSTALLED_APPS = [
#     'django.contrib.auth',
#     'django.contrib.admin',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.sites',
#     'django.contrib.flatpages',
#     'django.contrib.staticfiles',
#     'paypal',
# ] + get_core_apps([
#     'tests.shipping',
# ])

# MIDDLEWARE = (
#     'django.middleware.common.CommonMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'oscar.apps.basket.middleware.BasketMiddleware',
# )

# DEBUG = False
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
#     },
# }

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [
#             OSCAR_MAIN_TEMPLATE_DIR,
#         ],
#         'OPTIONS': {
#             'loaders': [
#                 'django.template.loaders.filesystem.Loader',
#                 'django.template.loaders.app_directories.Loader',
#             ],
#             'context_processors': [
#                 'django.contrib.auth.context_processors.auth',
#                 'django.template.context_processors.request',
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.i18n',
#                 'django.template.context_processors.media',
#                 'django.template.context_processors.static',
#                 'django.contrib.messages.context_processors.messages',

#                 'oscar.apps.search.context_processors.search_form',
#                 'oscar.apps.promotions.context_processors.promotions',
#                 'oscar.apps.checkout.context_processors.checkout',
#                 'oscar.core.context_processors.metadata',
#             ],
#         }
#     }
# ]


# SITE_ID = 1
# ROOT_URLCONF = 'tests.urls'

# STATIC_URL = '/'
# STATIC_ROOT = '/static/'