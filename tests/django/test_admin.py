"""Test for the Django admin models."""
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
