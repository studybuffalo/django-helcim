.. _getting-started:

===============
Getting Started
===============

.. note::

    These instructions make a distinction between making direct
    calls to the Helcim Commerce API versus using Helcim.js.
    Within this documentation, "Helcim API" refers to direct calls,
    where as "Helcim.js" will refere to calls via Helcim.js.

------------------------------------------------
Install django-helcim and its Dependencies
------------------------------------------------

Install ``django-helcim`` from PyPI. It is strongly recommended you use
a virtual environment for your projects. For example, you can do this
easily with Pipenv_::

    $ pipenv install django-helcim

.. _Pipenv: https://pipenv.readthedocs.io/en/latest/

If you are integrating this package with `Django Oscar`_, you will need
to install this package as well::

    $ pipenv install django-oscar

.. _Django Oscar: https://github.com/django-oscar/django-oscar

.. attention::

    If using Django Oscar, it is assumed you will manage the proper
    configuration. If needed, you can follow the
    `setup instructions for Django Oscar`_.

    .. _setup instructions for Django Oscar: https://django-oscar.readthedocs.io/en/latest/internals/getting_started.html

Make sure to add ``django-helcim`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
       ...
       'helcim',
       ...
    ]

-------------------------
Edit your Django Settings
-------------------------

Once ``django-helcim`` has been installed, you will need to update
your Django settings. You will need to specify the required settings
depending on the workflow you are using.

For the Helcim API, you will need to specify the following settings
(at a minimum): ``HELCIM_API_URL``, ``HELCIM_ACCOUNT_ID``,
``HELCIM_API_TOKEN``, and ``HELCIM_TERMINAL_ID``.

For Helcim.js, you will need to specify the ``HELCIM_JS_CONFIG``
setting (at a minimum).

There are several other settings available to configure
``django-helcim``. In most cases, defaults are applied automatically
when a setting is not specified. Where possible, the package defaults
to the most restrictive value possible (given the security requirements
of financial data). A full list of settings you can configure is
available on the :ref:`Settings page <settings>`.

--------
Add URLs
--------

There are a couple views you can use to review and manage various
aspects of the ``django-helcim`` models. You can enable these by
updating the :ref:`required settings <settings>` and adding the
package URLs:

.. code-block:: python

    from django.urls import path

    urlpatterns = [
        path('helcim', include('helcim.urls')),
    ]

-------------
Final Details
-------------

Django Helcim also supplies some credit card logos to display with
saved credit cards. To make use of these you will need to run
``collectstatic``::

    $ pipenv run python manage.py collectstatic

----------
Next Steps
----------

Once ``django-helcim`` is installed, you will need to integrate it into
your payment workflow. This process will vary significantly between
applications, but this application provides some standard objects and
methods to streamline the process.

Working examples of integrations can be found in
`GitHub repo sandbox directory`_. You will find two working Django
applications. The ``oscar`` sandbox is a working example of integration
with Django Oscar. The ``scratch`` sandbox shows a minimal example of
integration with a generic service requiring payment processing and
demonstrates both the Helcim API and Helcim.js workflows.

See the :ref:`Sandbox page <sandbox>` for additional details on setting up
and configuring the sandbox sites.

.. _GitHub repo sandbox directory: https://github.com/studybuffalo/django-helcim/tree/master/sandbox
