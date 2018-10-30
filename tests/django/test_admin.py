"""Test for the Django admin models."""
from importlib import reload

from django.contrib import admin
from django.test import override_settings

from helcim import admin as helcim_admin
from helcim.admin import HelcimTransactionAdmin
from helcim.models import HelcimTransaction


def test_admin_fields_match_model():
    """Tests that all fields in admin are present in model."""
    # Get a list of all the model fields
    model_fields = HelcimTransaction._meta.get_fields()
    field_names = [field.name for field in model_fields]

    # Remove UUID (not included in admin interface)
    field_names.remove('uuid')

    # Get the fields included in the admin
    admin_fields = HelcimTransactionAdmin.MODEL_FIELDS

    assert sorted(field_names) == sorted(admin_fields)

@override_settings(HELCIM_INCLUDE_ADMIN=True)
def test_admin_included_when_settings_specified():
    """Tests that admin is loaded when included in settings."""
    # pylint: disable=protected-access
    reload(helcim_admin)

    try:
        admin.site._registry[HelcimTransaction]
    except KeyError:
        assert False
    else:
        # Remove the registered model to prevent impacting other tests
        admin.site._registry.pop(HelcimTransaction)
        assert True

@override_settings(HELCIM_INCLUDE_ADMIN=False)
def test_admin_excluded_when_settings_implictly_exclude():
    """Tests that admin is not loaded when settings set to false."""
    # pylint: disable=protected-access
    reload(helcim_admin)

    try:
        admin.site._registry[HelcimTransaction]
    except KeyError:
        assert True
    else:
        assert False

def test_admin_excluded_when_settings_explictly_exclude():
    """Tests that admin is not loaded when settings absent."""
    # pylint: disable=protected-access
    reload(helcim_admin)

    try:
        admin.site._registry[HelcimTransaction]
    except KeyError:
        assert True
    else:
        assert False
