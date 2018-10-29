"""Script to initiate Django test runner."""
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    """Setup minimally working Django application and run tests."""
    # Setup the Django settings
    django_settings = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    }

    settings.configure(**django_settings)

    # Initiate Django
    django.setup()

    # Specify which tests to run
    test_list = [
        'tests.django.test_models',
    ]

    # Call the test runner and run tests
    test_runner = get_runner(settings)
    test_runner_instance = test_runner(verbosity=2, interactive=True)
    failures = test_runner_instance.run_tests(test_list)
    sys.exit(failures)

run_tests()
