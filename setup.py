#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='namesdb',
    version='1.0.0',
    description="Tools for importing FAR and WRA records.",
    long_description=readme + '\n\n' + history,
    author="Geoffrey Jost",
    author_email='geoffrey.jost@densho.org',
    url='https://github.com/densho/namesdb',
    packages=[
        'namesdb',
    ],
    package_dir={
        'namesdb': 'namesdb'
    },
    include_package_data=True,
    scripts = [
        'bin/namesdb',
    ],
    install_requires=requirements,
    license="TBD",
    zip_safe=False,
    keywords='namesdb',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: TBD',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
