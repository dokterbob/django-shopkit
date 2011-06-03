# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-shopkit.
#
# django-shopkit is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

try:
    README = open('README.rst').read()
except:
    README = None

try:
    REQUIREMENTS = open('requirements.txt').read()
except:
    REQUIREMENTS = None
    
SHORT_DESCRIPTION = \
""" A webshop application framework, similar to the way that
Django is a web application framework. It, essentially, is a toolkit for
building customized webshop applications using Django, for 'perfectionists
with deadlines'. """

setup(
    name = 'django-shopkit',
    version = "0.1",
    description = SHORT_DESCRIPTION,
    long_description = README,
    install_requires = REQUIREMENTS,
    author = 'Mathijs de Bruin',
    author_email = 'mathijs@mathijsfietst.nl',
    url = 'http://github.com/dokterbob/django-newsletter',
    packages = find_packages(),
    include_package_data = True,
    classifiers = ['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
