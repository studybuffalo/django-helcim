=========
Changelog
=========

----------------
Version 0 (Beta)
----------------

0.2.0 (2018-Nov-12)
===================

Feature Updates
---------------

* Added the HelcimToken model (AKA the "Token Vault") - allows saving of
  Helcim Commerce card tokens to allow re-use in later transactions.

Bug Fixes
---------

* Fixed issues where the ``HELCIM_REDACT_ALL`` flag was not overriding
  properly.
* Updated redaction functions to accomodate all known fields containing
  cardholder information.

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
