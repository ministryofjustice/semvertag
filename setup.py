#!/usr/bin/env python
"""
A SemVer Tagging tool for git repos.
"""
from setuptools import setup, find_packages

setup(
    name='semvertag',
    version='2.0.0',
    url='http://github.com/ministryofjustice/semvertag',
    license='MIT',
    author='',
    author_email='',
    description='',
    long_description=__doc__,
    platforms='any',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
    ],
    entry_points={
        'console_scripts': ['semvertag=semvertag:main'],
    }
)
