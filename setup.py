"""Setup script for the django-oscar-helcim package."""

from setuptools import find_packages, setup

from helcim import VERSION


setup(
    name='django-oscar-helcim',
    version=VERSION,
    url='https://github.com/django-oscar/django-oscar-paypal',
    description=('Payment integration with Helcim for django-oscar.'),
    long_description=open('README.rst').read(),
    keywords='Django, Oscar, Helcim, Payment',
    license=open('LICENSE').read(),
    platforms=['linux', 'windows'],
    packages=['helcim'],
    include_package_data=True,
    install_requires=[],
    extras_require={
        'oscar': ['django-oscar>=1.5,<1.7']
    },
    tests_require=[
        'pytest==3.8.2'
        'pytest-cov==2.6.0',
    ],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Other/Nonlisted Topic'],
)