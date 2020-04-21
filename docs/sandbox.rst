===============
Sandbox Website
===============

The sandbox websites provide working examples of how to integrate
``django-helcim`` into a project. There are two sandboxes to
demonstrate two potential use cases: integration with Django Oscar and
integration into a generic service requiring payment processing.

.. attention::

    These instructions assume you have already setup a pipenv virtual
    environment with ``django-helcim`` installed. See the
    :ref:`Getting started <getting-started>` page if you need additional
    instructions.

---------------
Scratch Sandbox
---------------

The Scratch Sandbox website is a generic example service that collects
payment details for processing by Helcim. It includes two examples:
the Helcim API workflow and the Helcim.js workflow.

Deploying the site
==================

First You will need to create your own copy of the ``config.env`` file.
This file contains some basic ``django`` and ``django-helcim`` settings
to get the sandbox to work. A template config file can be found at
``sandbox/.config.env``. Copy and rename this file to ``config.env``
and update the relevant settings as needed for your sandbox (e.g. your
Helcim API and/or Helcim.js details).

Next, you will need to run the Django migrations::

    $ pipenv run python sandbox/manage.py migrate

You can now start your site through the standard Django commands and
access it at http://127.0.0.1:8000/::

    $ pipenv run python sandbox/manage.py runserver

If needed, you can create a superuser account with the standard management
command::

    $ pipenv run python sandbox/manage.py createsuperuser

You can create regular user accounts by running the sandbox sever and
creating it with the web form: http://127.0.0.1:8000/accounts/login/.

.. tip::

    If you need to restart your site from scratch, delete the
    ``db.sqlite3`` file and complete the above steps again.

-------------
Oscar Sandbox
-------------

The Oscar Sandbox website is a barebones Django Oscar store that
demonstrates how to use `django-helcim` with Django Oscar and
handle payments via the Helcim API.

Deploying the site
==================

You will need to create your own copy of the ``config.env`` file. This
file contains some basic ``django`` and ``django-helcim`` settings to
get the sandbox to work. A template config file can be found at
``sandbox/.config.env``. Copy and rename this file to ``config.env``
and update the relevant settings as needed for your sandbox (e.g. your
Helcim API details).

You should then be able to run the Django migrations::

    $ pipenv run python sandbox/manage.py migrate

Next you will need to load country data (see the `Django Oscar page for
more details`_)::

    $ pipenv run python sandbox/manage.py oscar_populate_countries

.. _Django Oscar page for more details: https://django-oscar.readthedocs.io/en/latest/internals/getting_started.html#initial-data

Next, import a basic catalogue of store items to test with::

    $ pipenv run python sandbox/manage.py oscar_import_catalogue sandbox/fixtures/catalogue.csv

Finally, collect all the static files for the site::

    $ pipenv run python sandbox/manage.py collectstatic

You can now start your site through the standard Django commands and
access it at http://127.0.0.1:8000/::

    $ pipenv run python sandbox/manage.py runserver

If needed, you can create a superuser account with the standard management
command::

    $ pipenv run python sandbox/manage.py createsuperuser

You can create regular user accounts by running the sandbox sever and
creating it with the web form: http://127.0.0.1:8000/accounts/login/.

.. tip::

    If you need to restart your site from scratch, delete the
    ``db.sqlite3`` file and complete the above steps again.
