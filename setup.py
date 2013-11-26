#!/usr/bin/env python

from distutils.core import setup

setup(
    name         = 'PyEnvy',
    version      = '0.0.1',
    description  = 'Virtualenv autoloader',
    author       = 'David Vogt',
    author_email = 'david.vogt@adfinis-sygroup.ch',
    url          = 'http://adfinis-sygroup.ch',
    packages     = ['pyenvy'],
    package_dir  = {'': 'src'},
)
