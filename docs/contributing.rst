============
Contributing
============

This is the contributing section.

-------
Testing
-------

All pull requests must have unit tests built and must maintain
or increase code coverage. The ultimate goal is to achieve a code
coverage of 100%. While this may result in some superfluous tests,
it sets a good minimum baseline for test construction.

Testing format
==============

All tests are built with the `pytest framework`_. Tests should be
constructed to test a single function or aspect wherever possible. It
may be appropriate at times to constructer larg tests approaching full
integration testing, but unit tests are still required.

.. _pytest framework: https://docs.pytest.org/en/latest/

Testing with pytest
===================

Tests can be run locally with the following command::

    pipenv run py.test

To check test coverage, you can use the following::

    pipenv run py.test --cov=helcim --cov-report=html

You may specify the output of the coverage report by changing the
`--cov-report` option to `html` or `xml`.

Testing with tox
================

To ensure compatability with as wide variety of Python and Django
versions, this package uses tox_. You can tests via tox with the
following command::

    pipenv run tox

.. _tox: https://tox.readthedocs.io/en/latest/

You will need to have all versions of Python installed locally for
tox to run tests. Any versions you are missing will be skipped. The
Continuous Integration (CI) server will run tests against all versions
on any pull requests or commits.
