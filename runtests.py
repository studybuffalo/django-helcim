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