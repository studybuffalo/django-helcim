========
Settings
========

Below is a comprehensive list of all the settings for
django-helcim.

------------
API settings
------------

These are settings that control interactions with the
Helcim Commerce API.

``HELCIM_API_URL``
==================

**Required:** ``False``

**Default (string):** ``https://secure.myhelcim.com/api/``

The URL to access the Helcim Commerce API. At this time there is only
access to the API through the default URL, but this setting is
available to handle any future situations where custom endpoints
become available or to allow users to quickly update their application
should the URL change before this package is updated.

``HELCIM_ACCOUNT_ID``
=====================

**Required:** ``True``

**Default (string):** ``''``

The account ID for your Helcim account.

``HELCIM_API_TOKEN``
====================

**Required:** ``True``

**Default (string):** ``''``

The API token generated on your Helcim Commerce API dashboard to allow
django-helcim to make transactions via the Helcim Commerce API.

``HELCIM_TERMINAL_ID``
======================

**Required:** ``False``

**Default (string):** ``''``

The Helcim terminal ID you are using. If not provided the Helcim
Commerce API will use the default terminal for the provided Account ID.

``HELCIM_API_TEST``
===================

**Required:** ``False``

**Default (boolean):** ``False``

A flag declaring whether transactions should be submitted in test mode
or not. When set to `True` all transactions will have ``test=true`` added
to the POST data. This prevents the Helcim Commerce API from attempting
to process the transaction.

-----------------------------
Private data storage settings
-----------------------------

These are settings that control what kind of private data is stored in
your database. Django-helcim does not record the Primary Account
Number (PAN), but does give you the option to save select data that
could be used to identify a specify customer and their account. **You
should only store the minimum amount of data you need to reduce the
risk and severity of a data breach.**

``HELCIM_REDACT_ALL``
=====================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, all references to the cardholder name, credit card
number, credit card expiry, credit card type, and Helcim Commerce
token will be redacted. **This setting overrides any of the individual
settings below.**

``HELCIM_REDACT_CC_NAME``
=========================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card cardholder
name.

``HELCIM_REDACT_CC_NUMBER``
===========================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card number.

``HELCIM_REDACT_CC_EXPIRY``
===========================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card expiry date.

``HELCIM_REDACT_CC_TYPE``
=========================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card type.

``HELCIM_REDACT_TOKEN``
=======================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, redacts all reference to the Helcim Commerce credit
card token and the 'first four last four' digits of the credit card
number.

------------------------
Additional Functionality
------------------------

These settings allow you to enable or disable additional functionality
with django-helcim.


``HELCIM_TRANSACTIONS_READ_ONLY``
=================================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``False``, will allow you to capture and refund transactions
from the ``HelcimTransactionDetailView``. Otherwise, this functionality
is turned off and the transaction detail view is read only.

``HELCIM_ENABLE_TOKEN_VAULT``
=============================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, enables the Helcim card token vault. This stores
the card token returned from the Helcim Commerce API, along with the
customer code. The token will also be associated to the logged in user.
