##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='RestrictedPython',
      version='3.6.0',
      url='http://pypi.python.org/pypi/RestrictedPython',
      license='ZPL 2.1',
      description='RestrictedPython provides a restricted execution '
      'environment for Python, e.g. for running untrusted code.',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=(read('src', 'RestrictedPython', 'README.txt')
                        + '\n' +
                        read('CHANGES.txt')),

      packages = find_packages('src'),
      package_dir = {'': 'src'},
      install_requires = ['setuptools'],
      include_package_data = True,
      zip_safe = False,
      )
