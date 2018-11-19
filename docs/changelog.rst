=========
Changelog
=========

----------------
Version 0 (Beta)
----------------

0.3.0 (2018-Nov-18)
===================

Feature Updates
---------------

* Added new function to the ``bridge_oscar`` module to retrieve a users
  saved Helcim tokens (from the Token Vault).
* Extended the ``bridge_oscar`` module to streamline validating a
  Helcim token for payment processing by Django Oscar.
* Updated sandbox site to demonstrate a workflow that allows a customer
  to use a saved credit card or enter a new one. Also allows customers
  to save a credit card for future use.
* Updated HelcimToken model to:
  * record credit card type;
  * display the "first 4 last 4" digits of the credit card number as a
    16 character string; and
  * retrieve and display an image for the corresponding credit card
    type.

0.2.2 (2018-Nov-17)
===================

Bug Fixes
---------

* Removing unnecessary ``app_name`` from urls which may cause namespace
  issues.

0.2.1 (2018-Nov-17)
===================

Bug Fixes
---------

* HTML template files are now included in package when installed via
  PyPI.

0.2.0 (2018-Nov-14)
===================

Feature Updates
---------------

* Added the HelcimToken model (AKA the "Token Vault") - allows saving of
  Helcim Commerce card tokens to allow re-use in later transactions.
* Made functions for HelcimTransaction views more configurable - can
  now choose exactly which features to enable and disable.
* Reworked settings to default to more conservative values. Thinks will
  generally be disabled or redacted by default, but can be enabled as
  needed.
* Added redaction settings for credit card CVV, credit card magnetic
  strip data, and encrypted credit card magnetic strip data.
* Improved sandbox functioning to make setting up a new demo site
  easier.

Bug Fixes
---------

* Fixed issues where the ``HELCIM_REDACT_ALL`` flag was not overriding
  properly.
* Updated redaction functions to accommodate  all known fields
  containing cardholder information.
* Fixed issue where POST requests were returning byte-data rather than
  string data.

0.1.2 (2018-Nov-08)
===================

Feature Updates
---------------

* Adding DepreciationWarning for Django 1.11 in anticipation of eventual end
  of support in 2020.
* Adding Tox test environments for all combinations of supported Python
  and Django versions.

0.1.1 (2018-Nov-07)
===================

Bug Fixes
---------

* Properly specifying dependencies for PyPI installation and updating
  Pipfile.

0.1.0 (2018-Nov-03)
===================

Feature Updates
---------------

* Initial package release
* Supports basic API functions: purchase (sale), pre-authorization, capture,
  refund
* Basic ``django-oscar`` support with the bridge module.
