.. _settings:

========
Settings
========

Below is a comprehensive list of all the settings for
Django Helcim.

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
``django-helcim`` to make transactions via the Helcim Commerce API.

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

``HELCIM_JS_CONFIG``
====================

**Required:** ``False``

**Default (dictionary):** ``{}``

A dictionary that allows you to declare your Helcim.js configuration details
within your Django settings. This dictionary is validated and made available
in your view context via the ``HelcimJSMixin`` mixin. The dictionary requires
the following format:

.. code-block:: python

   {
     'identifier': {
       'url': 'url-to-your-helcim-js-script',
       'token' 'your-helcim-js-token',
       'test': True,
     }
   }

Once configured, you can add the ``HelcimJSMixin`` to the required views and
access the details in your templates. Below is summary of the keys and mixin
funtionality:

+----------------+-----------------------+------------------------------------+
| Settings Key   | Description           | Mixin Usage                        |
+================+=======================+====================================+
| ``identifier`` | An identifier used in | ``helcim_js.identifier``           |
|                | templates to          |                                    |
|                | reference these       |                                    |
|                | configuration         |                                    |
|                | details.              |                                    |
+----------------+-----------------------+------------------------------------+
| ``url``        | URL to the Helcim.js  | ``helcim_js.identifier.url``       |
|                | file. Can be an empty |                                    |
|                | string if you will    |                                    |
|                | serve the JS file     |                                    |
|                | yourself.             |                                    |
+----------------+-----------------------+------------------------------------+
| ``token``      | The Helcim.js token   | ``helcim_js.identifier.token``     |
+----------------+-----------------------+------------------------------------+
| ``test``       | Optional value; add   | ``helcim_js.identifier.test_input` |
|                | key with a ``truthy`` |                                    |
|                | value to enable. If   |                                    |
|                | enabled, will output  |                                    |
|                | the HTML input to     |                                    |
|                | trigger the Helcim.js |                                    |
|                | test mode. Otherwise  |                                    |
|                | will be empty string. |                                    |
+----------------+-----------------------+------------------------------------+

-----------------------------
Private data storage settings
-----------------------------

These are settings that control what kind of private data is stored in
your database. ``django-helcim`` does not record the Primary Account
Number (PAN), but does give you the option to save select data that
could be used to identify a specify customer and their account. **You
should only store the minimum amount of data you need to reduce the
risk and severity of a data breach.**

``HELCIM_REDACT_ALL``
=====================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, all references to sensitive cardholder information
will be redacted. **This setting applies to and overrides any of the
individual settings below.**

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

``HELCIM_REDACT_CC_CVV``
========================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card CVV.

``HELCIM_REDACT_CC_TYPE``
=========================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card type.

``HELCIM_REDACT_CC_MAGNETIC``
=============================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card magnetic
strip data.

``HELCIM_REDACT_CC_MAGNETIC_ENCRYPTED``
=======================================

**Required:** ``False``

**Default (boolean):** ``True``

If set to ``True``, redacts all reference to the credit card magnetic
strip data and the terminal serial number.

``HELCIM_REDACT_TOKEN``
=======================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, redacts all reference to the Helcim Commerce credit
card token and the 'first four last four' digits of the credit card
number.

.. note::

    This setting will not override the **Helcim Token Vault**. If you
    to turn off the vault, use the ``HELCIM_ENABLE_TOKEN_VAULT``
    setting.

-------------------------------
Helcim Transaction Functionality
-------------------------------

These settings allow you to enable or disable additional functionality
with the HelcimTransaction model.


``HELCIM_ENABLE_TRANSACTION_CAPTURE``
=====================================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, will allow you to capture transactions from the
``HelcimTransactionDetailView``.

``HELCIM_ENABLE_TRANSACTION_REFUND``
=====================================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, will allow you to refund transactions from the
``HelcimTransactionDetailView``.

--------------------------------
Helcim Token Vault Functionality
--------------------------------

``HELCIM_ENABLE_TOKEN_VAULT``
=============================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, enables the Helcim card token vault. This stores
the card token returned from the Helcim Commerce API, along with the
customer code. The token will also be associated to the logged in user.

-------------------
Admin Functionality
-------------------

A read-only admin view is available to assist with viewing data or
debugging.

``HELCIM_ENABLE_ADMIN``
=======================

**Required:** ``False``

**Default (boolean):** ``False``

If set to ``True``, will register the read-only admin views.

--------------
Other Settings
--------------

``HELCIM_ASSOCIATE_USER``
=========================

**Required:** ``False``

**Default (boolean):** ``True``

Specifies whether a django user model should be associated to
``HelcimTransaction`` and ``HelcimToken`` model instances. By default,
the logged in user is added to all transactions and tokens. This
can be turned off by setting this to ``False``.
