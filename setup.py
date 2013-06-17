# -*- coding: utf-8 -
#
# This file is part of sendsms released under the MIT license. 
# See the NOTICE for more information.

from setuptools import setup, find_packages

reqs = ['django',
        'django-sendsms']
try:
    import importlib
except ImportError:
    reqs.append('importlib')

setup(
    name='django-sendsmsru',
    version=__import__('sendsmsru').VERSION,
    description='Russian backends for django-sendsms',
    long_description=open('README.md').read(),
    author='Victor Safronovich',
    author_email='vsafronovich@gmail.com',
    license='MIT',
    url='http://github.com/suvit/django-sendsmsru',
    zip_safe=False,
    packages=find_packages(exclude=['docs', 'examples', 'tests']),
    install_requires=reqs,
    include_package_data=True,
)
