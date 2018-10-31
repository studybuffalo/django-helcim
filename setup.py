"""Setup script for the django-helcim package."""

from setuptools import find_packages, setup

from helcim import VERSION


setup(
    name='django-helcim',
    version=VERSION,
    url='https://github.com/studybuffalo/django-helcim.',
    description=('A Django-based integration with the Helcim Commerce API '),
    long_description=open('README.rst').read(),
    keywords='Django, Helcim, Oscar, Payment',
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
