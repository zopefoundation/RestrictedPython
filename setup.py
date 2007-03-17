##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for RestrictedPython package

$Id$
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'RestrictedPython'
setup(name=name,
      version='3.4dev',
      url='http://svn.zope.org/'+name,
      license='ZPL 2.1',
      description='Restricted Python executiion handlers',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description=(
        read('README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      tests_require = ['zope.testing'],
      install_requires = ['setuptools'],
      include_package_data = True,

      zip_safe = False,
      )
