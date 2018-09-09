"""Tests for the exceptions module."""
# pylint: disable=missing-docstring

from unittest import mock
import importlib

def test_helcim_exception_with_oscar():
    import helcim.exceptions
    from oscar.apps.payment.exceptions import PaymentError

    assert isinstance(helcim.exceptions.HelcimError(), PaymentError)

def test_helcim_exception_without_oscar():
    mock_modules = {
        'oscar': {},
        'oscar.apps': {},
        'oscar.apps.payment': {},
        'oscar.apps.payment.exceptions': {},
    }

    with mock.patch.dict('sys.modules', mock_modules):
        # Need to load module then reload for patch to apply
        import helcim.exceptions
        importlib.reload(helcim.exceptions)

        assert isinstance(helcim.exceptions.HelcimError(), Exception)
