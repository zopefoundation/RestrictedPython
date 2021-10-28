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
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


tests_require = [
    'pytest',
    'pytest-mock',
]


setup(
    name='RestrictedPython',
    version='5.2a1.dev0',
    url='https://github.com/zopefoundation/RestrictedPython',
    license='ZPL 2.1',
    description=(
        'RestrictedPython is a defined subset of the Python language which '
        'allows to provide a program input into a trusted environment.'
    ),
    long_description=read('README.rst') + '\n' + read('CHANGES.rst'),
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 6 - Mature',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Security',
    ],
    keywords='restricted execution security untrusted code',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    project_urls={
        "Documentation": "https://restrictedpython.readthedocs.io/",
        "Source": "https://github.com/zopefoundation/RestrictedPython",
        "Tracker": "https://github.com/zopefoundation/RestrictedPython/issues",
    },
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <3.11",  # NOQA: E501
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'docs': ['Sphinx', 'sphinx_rtd_theme'],
    },
    include_package_data=True,
    zip_safe=False
)
