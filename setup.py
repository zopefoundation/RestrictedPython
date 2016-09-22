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
"""Setup for RestrictedPython package"""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='RestrictedPython',
      version='4.0.0.dev0',
      url='http://pypi.python.org/pypi/RestrictedPython',
      license='ZPL 2.1',
      description='RestrictedPython provides a restricted execution '
                  'environment for Python, e.g. for running untrusted code.',
      long_description=(read('src', 'RestrictedPython', 'README.txt') + '\n' +
                        read('CHANGES.txt')),
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
          'setuptools',
          'zope.deprecation',
          'ipython',
          'ipdb',
      ],
      extras_require={
          'docs': [
              'Sphinx',
          ],
          'release': [
              'zest.releaser',
          ],
          'develop': [
              'ipython',
              'ipdb',
          ],
      },
      include_package_data=True,
      zip_safe=False,
      )
