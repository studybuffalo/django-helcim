===================
django-oscar-helcim
===================

|GithubRelease|_ |BuildStatus|_ |Coverage|_ |License|_

.. |GithubRelease| image:: https://img.shields.io/github/release/studybuffalo/django-oscar-helcim/all.svg
   :alt: GitHub release version

.. _GithubRelease: https://github.com/studybuffalo/django-oscar-helcim/releases

.. |BuildStatus| image:: https://img.shields.io/jenkins/s/https/ci.studybuffalo.com/job/django-oscar-helcim/job/master.svg
   :alt: Jenkins build status

.. _BuildStatus: https://ci.studybuffalo.com/blue/organizations/jenkins/django-oscar-helcim/

.. |Coverage| image:: https://badges.ci.studybuffalo.com/coverage/django-oscar-helcim/job/master
   :alt: Code coverage

.. _Coverage: https://ci.studybuffalo.com/job/django-oscar-helcim/job/master/lastBuild/cobertura/

.. |License| image:: https://img.shields.io/github/license/studybuffalo/django-oscar-helcim.svg
   :alt: License

.. _License: https://github.com/studybuffalo/django-oscar-helcim/blob/master/LICENSE

This package provides integration of the Helcim Payment API with
`Django Oscar`_. Django-oscar-helcim can also be easily extended for use used
with other python-based commerce solutions, as all base modules are platform
agnostic.

.. _Django Oscar: https://github.com/django-oscar/django-oscar

---------------
Getting Started
---------------

Instructions on installing and configuration can be found on `Read The Docs`_.

.. _Read The Docs: https://django-oscar-helcim.readthedocs.io/en/latest/

-------
Support
-------

The docs provide examples for setup and common issues to be aware of. If the
issue involves connecting this package to Django Oscar, this repository
contains a `sandbox environment`_ you can review for a minimal working
example. For any other issues, you can submit a `GitHub Issue`_.

.. _docs: https://django-oscar-helcim.readthedocs.io/en/latest/installation.html

.. _sandbox environment: https://django-oscar-helcim.readthedocs.io/en/latest/contributing.html#sandbox-website

.. _GitHub Issue: https://github.com/studybuffalo/django-oscar-helcim/issues

------------
Contributing
------------

Contributions are welcome, especially to address bugs and extend
functionality. Full details on contributing can be found in the docs.

.. _docs: https://django-oscar-helcim.readthedocs.io/en/latest/contributing.html

----------
Versioning
----------

This package uses a MAJOR.MINOR.PATCH versioning, as outlined at `Semantic Versioning 2.0.0`_.

.. _Semantic Versioning 2.0.0: https://semver.org/

-------
Authors
-------

Joshua Robert Torrance (StudyBuffalo_)

.. _StudyBuffalo: https://github.com/studybuffalo

-------
License
-------

This project is licensed under the GPLv3. Please see the LICENSE_ file for details.

.. _LICENSE: https://github.com/studybuffalo/django-oscar-helcim/blob/master/LICENSE

----------------
Acknowledgements
----------------

Thanks to the `django-oscar-paypal`_ developers, from which many of this
packages design decisions are based.

.. _django-oscar-paypal: https://github.com/django-oscar/django-oscar-paypal
