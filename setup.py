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
      long_description=(read('src', 'RestrictedPython', 'README.rst') + '\n' +
                        read('CHANGES.rst')),
      classifiers=[
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Security',
      ],
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
          'setuptools',
      ],
      extras_require={
          'docs': [
              'Sphinx',
          ],
          'release': [
              'zest.releaser',
          ],
          'test': [
              'pytest',
          ],
          'develop': [
              'pdbpp',
              'isort',
          ],
      },
      include_package_data=True,
      zip_safe=False,
      )
