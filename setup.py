#!/usr/bin/env python
# -*- codig: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='blackbird-php-fpm',
    version='0.1.1',
    description=(
        'get php-fpm stats by using status.'
    ),
    long_description=read('PROJECT.txt'),
    author='makocchi',
    author_email='makocchi@gmail.com',
    url='https://github.com/Vagrants/blackbird-php-fpm',
    data_files=[
        ('/opt/blackbird/plugins', ['php-fpm.py']),
        ('/etc/blackbird/conf.d', ['php-fpm.cfg'])
    ],
    test_suite='tests',
)
