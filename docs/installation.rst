===============
Getting started
===============

------------------------------------------------
Install django-oscar-helcim and its dependencies
------------------------------------------------

Install django-oscar-helcim (which will install both Django and
django-oscar as dependencies). It is strongly recommended you use a
virtual environment for your projects. For example, you can do this
easily with Pipenv_::

    $ pipenv install django-oscar-helcim

.. _Pipenv: https://pipenv.readthedocs.io/en/latest/

-------------------------
Edit your Django settings
-------------------------

.. attention::

    It is assumed you will already be using Django Oscar. If you haven't
    done so already, follow the `setup instructions for Django Oscar`_.

    .. _setup instructions for Django Oscar: https://django-oscar.readthedocs.io/en/latest/internals/getting_started.html

Once django-oscar-helcim has been installed, you will need to update
your Django settings. At a bare minimum you will need to specify the
following settings: `HELCIM_API_URL`, `HELCIM_ACCOUNT_ID`,
`HELCIM_API_TOKEN`, and `HELCIM_TERMINAL_ID`. For example::

    HELCIM_API_URL = https://secure.myhelcim.com/api/
    HELCIM_ACCOUNT_ID = 123456
    HELCIM_API_TOKEN = 123456789abcdefg
    HELCIM_TERMINAL_ID = 123456

A summary of all settings can be found in the `Settings page`_.

.. _Settings page: https://django-oscar-helcim.readthedocs.io/en/latest/settings.html
