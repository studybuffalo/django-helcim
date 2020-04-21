"""Test sfor the __init__.py module."""
from importlib import reload
from unittest.mock import patch

import helcim

@patch('helcim.sys.version', '3.5.1')
@patch('helcim.django.__version__', '3.0.0')
def test_python_35_depreciation_warning(recwarn):
    """Tests that depreciation warning fires for Python 3.5.x"""
    reload(helcim)

    assert len(recwarn) == 1

    python_35_warning = recwarn.pop(DeprecationWarning)
    assert issubclass(python_35_warning.category, DeprecationWarning)

    warning_text = (
        'django-helcim will stop supporting Python 3.5 '
        'once it reaches end-of-life (approximately September 2020). '
        'Ensure you have updated your Python version by then.'
    )

    assert str(python_35_warning.message) == warning_text

@patch('helcim.sys.version', '3.6.0')
@patch('helcim.django.__version__', '3.0.0')
def test_other_python_versions_depreciation_warning(recwarn):
    """Tests that warning doesn't fire for other Python versions."""
    reload(helcim)

    assert len(recwarn) == 0

@patch('helcim.sys.version', '3.6.0')
@patch('helcim.django.__version__', '1.11.0')
def test_django_111_depreciation_warning(recwarn):
    """Tests that the depreciation warning fires for Django 1.11."""
    reload(helcim)

    assert len(recwarn) == 1

    django_111_warning = recwarn.pop(DeprecationWarning)
    assert issubclass(django_111_warning.category, DeprecationWarning)

    warning_text = (
        'django-helcim will stop supporting Django 1.11 LTS once '
        'it reaches end-of-life (approximately April 2020). '
        'Ensure you have updated your Django version by then.'
    )

    assert str(django_111_warning.message) == warning_text

@patch('helcim.sys.version', '3.6.0')
@patch('helcim.django.__version__', '2.0.0')
def test_other_django_versions_depreciation_warning(recwarn):
    """Tests that warning doesn't fire for other Django versions."""
    reload(helcim)

    assert len(recwarn) == 0
