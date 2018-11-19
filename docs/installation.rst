===============
Getting started
===============

------------------------------------------------
Install django-helcim and its dependencies
------------------------------------------------

Install ``django-helcim`` (which will install both Django as a
dependency). It is strongly recommended you use a virtual environment
for your projects. For example, you can do this easily with Pipenv_::

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

Django Helcim also supplies some credit card logos to display with
saved credit cards. To make use of these you will need to run
``collectstatic``::

    $ pipenv run python manage.py collectstatic

-------------------------
Edit your Django settings
-------------------------

Once ``django-helcim`` has been installed, you will need to update
your Django settings. At a bare minimum you will need to specify the
following settings: `HELCIM_API_URL`, `HELCIM_ACCOUNT_ID`,
`HELCIM_API_TOKEN`, and `HELCIM_TERMINAL_ID`. For example::

    HELCIM_API_URL = https://secure.myhelcim.com/api/
    HELCIM_ACCOUNT_ID = 123456
    HELCIM_API_TOKEN = 123456789abcdefg
    HELCIM_TERMINAL_ID = 123456

This package defaults where possible to the most restrictive settings
possible, given the secure nature of financial data. You will need to
manually enable functionality as your application requires. You can see
a summary of all settings in the `Settings page`_.

.. _Settings page: https://django-helcim.readthedocs.io/en/latest/settings.html
