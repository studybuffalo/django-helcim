============
Contributing
============

Contributions or forking of the project is always welcome. Below will
provide a quick outline of how to get setup and things to be aware of
when contributing.

----------------
Reporting issues
----------------

If you simply want to report an issue, you can use the
`GitHub Issue page`_.

.. _GitHub Issue page: https://github.com/studybuffalo/django-helcim/issues

--------------------------------------
Setting up the development environment
--------------------------------------

This package is built using Pipenv_, which will take care of both
your virtual environment and package management. If needed, you can
install Pipenv through pip::

    $ pip install pipenv

.. _Pipenv: https://pipenv.readthedocs.io/en/latest/

To download the repository from GitHub via git::

    $ git clone git://github.com/studybuffalo/django-helcim.git

You can then install all the required dependencies by changing to the
package directory and installing from Pipfile.lock::

    $ cd django-helcim
    $ pipenv install --ignore-pipfile --dev

Finally, you will need to build the package::

    $ pipenv run python setup.py develop

You should now have a working environment that you can use to run tests
and setup the sandbox demo.

-------
Testing
-------

All pull requests must have unit tests built and must maintain
or increase code coverage. The ultimate goal is to achieve a code
coverage of 100%. While this may result in some superfluous tests,
it sets a good minimum baseline for test construction.

Testing format
==============

All tests are built with the `pytest framework`_
(and `pytest-django`_ for Django-specific components). There are no
specific requirements on number or scope of tests, but at a bare
minimum there should be tests to cover all common use cases. Wherever
possible, try to test the smallest component possible.

.. _pytest framework: https://docs.pytest.org/en/latest/

.. _pytest-django: https://pytest-django.readthedocs.io/en/latest/

Running Tests
=============

You can run all tests with the standard pytest command::

    $ pipenv run py.test

To check test coverage, you can use the following::

    $ pipenv run py.test --cov=helcim --cov-report=html

You may specify the output of the coverage report by changing the
``--cov-report`` option to ``html`` or ``xml``.

Testing with tox
================

To ensure compatability with as wide variety of Python and Django
versions, this package uses tox_. You can tests via tox with the
following command::

    $ pipenv run tox

.. _tox: https://tox.readthedocs.io/en/latest/

You will need to have all versions of Python installed locally for
tox to run tests. Any versions you are missing will be skipped. The
Continuous Integration (CI) server will run tests against all versions
on any pull requests or commits.

---------------
Sandbox Website
---------------

The Sandbox website is a barebones Django Oscar store that demonstrates
how to use django-helcim with Django Oscar and provides a way to
test any of your changes. You will need to setup your development
environment (see above) to proceed.

.. attention::

    These instructions assume you have already setup a pipenv virtual
    environment with django-helcim installed. See `Getting started`_ if
    you need additional instructions.

    .. _Getting started: https://django-helcim.readthedocs.io/en/latest/installation.html#install-django-helcim-and-its-dependencies

Deploying the site
==================

First migrate the the Django database::

    $ pipenv run python sandbox/manage.py migrate

Next you will need to load country data (see the `Django Oscar page for
more details`_)::

    $ pipenv run python sandbox/manage.py oscar_populate_countries

.. _Django Oscar page for more details: https://django-oscar.readthedocs.io/en/latest/internals/getting_started.html#initial-data

Finally, import a basic catalogue of store items to test with::

    $ pipenv run python sandbox/manage.py oscar_import_catalogue sandbox/fixtures/catalogue.csv

You can now start your site through the standard Django commands and
access it at http://127.0.0.1:8000/::

    $ pipenv run python sandbox/manage.py runserver

If needed, you can create a superuser account with the standard manager
command::

    $ pipenv run python sandbox/manage.py createsuperuser

You can create regular user accounts by running the sandbox sever and
creating it with the web form:: http://127.0.0.1:8000/accounts/login/.

.. tip::

    If you need to restart your site from scratch, delete the
    ``db.sqlite3`` file and complete the above steps again.

----------------------
Updating documentation
----------------------

All documentation is hosted on `Read the Docs`_ and is built using
Sphinx_. All the module content is automatically built from the
docstrings and the `sphinx-apidoc`_ tool and the
`sphinxcontrib-napoleon`_ extension.

.. _Read the Docs: https://readthedocs.org/
.. _Sphinx: http://www.sphinx-doc.org/en/master/
.. _sphinx-apidoc: http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
.. _sphinxcontrib-napoleon: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/

Docstring Format
================

The docstrings of this package follow the `Google Python Style Guide`_
wherever possible. This ensures proper formatting of the documentation
generated automatically by Sphinx. Additional examples can be found on
the `Sphinx napoleon extension documentation`_.

.. _Google Python Style Guide: https://github.com/google/styleguide/blob/gh-pages/pyguide.md
.. _Sphinx napoleon extension documentation: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/

Building package reference documentation
========================================

The content for the Package reference is built using the
``sphinx-apidoc`` tool. If files in the ``helcim`` module are added or
deleted you will need to rebuild the file for the changes to populate
on Read the Docs. You can do this with the following command::

    $ pipenv run sphinx-apidoc -fTM -o docs helcim helcim/migrations helcim/urls.py helcim/apps.py helcim/admin.py
