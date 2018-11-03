===================
django-helcim
===================

|GithubRelease|_ |BuildStatus|_ |Coverage|_ |License|_

.. |GithubRelease| image:: https://img.shields.io/github/release/studybuffalo/django-helcim/all.svg
   :alt: GitHub release version

.. _GithubRelease: https://github.com/studybuffalo/django-helcim/releases

.. |BuildStatus| image:: https://img.shields.io/jenkins/s/https/ci.studybuffalo.com/job/django-helcim/job/master.svg
   :alt: Jenkins build status

.. _BuildStatus: https://ci.studybuffalo.com/blue/organizations/jenkins/django-helcim/

.. |Coverage| image:: https://badges.ci.studybuffalo.com/coverage/django-helcim/job/master
   :alt: Code coverage

.. _Coverage: https://ci.studybuffalo.com/job/django-helcim/job/master/lastBuild/cobertura/

.. |License| image:: https://img.shields.io/github/license/studybuffalo/django-helcim.svg
   :alt: License

.. _License: https://github.com/studybuffalo/django-helcim/blob/master/LICENSE

This package provides a `Django`_-based integration with the
`Helcim Commerce API`_. It is designed to be easily implemented
with existing Django-based commerce platforms and comes with an
optional module to connect with `Django Oscar`_.

.. _Django: https://www.djangoproject.com/

.. _Helcim Commerce API: https://www.helcim.com/support/article/625-helcim-commerce-api-api-overview/

.. _Django Oscar: https://github.com/django-oscar/django-oscar

---------------
Getting Started
---------------

Instructions on installing and configuration can be found on
`Read The Docs`_.

.. _Read The Docs: https://django-helcim.readthedocs.io/en/latest/

-------
Support
-------

The `docs provide examples for setup and common issues`_ to be aware
of. If the issue involves connecting this package to Django Oscar, this
repository contains a `sandbox environment`_ you can review for a
minimal working example. For any other issues, you can submit a
`GitHub Issue`_.

.. _docs provide examples for setup and common issues: https://django-helcim.readthedocs.io/en/latest/installation.html

.. _sandbox environment: https://django-helcim.readthedocs.io/en/latest/contributing.html#sandbox-website

.. _GitHub Issue: https://github.com/studybuffalo/django-helcim/issues

------------
Contributing
------------

Contributions are welcome, especially to address bugs and extend
functionality. Full `details on contributing can be found in the docs`_.

.. _details on contributing can be found in the docs: https://django-helcim.readthedocs.io/en/latest/contributing.html

----------
Versioning
----------

This package uses a MAJOR.MINOR.PATCH versioning, as outlined at
`Semantic Versioning 2.0.0`_.

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

.. _LICENSE: https://github.com/studybuffalo/django-helcim/blob/master/LICENSE

----------------
Acknowledgements
----------------

Thanks to the `django-oscar-paypal`_ developers, from which many of this
packages design decisions are based.

.. _django-oscar-paypal: https://github.com/django-oscar/django-oscar-paypal
