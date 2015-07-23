SHELL = /bin/bash
DEBIAN_CODENAME := $(shell lsb_release -sc)

PIP_CACHE_DIR=/usr/local/src/pip-cache
VIRTUALENV=/usr/local/src/env/namesdb
INSTALLDIR=/usr/local/src/namesdb


.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
# 	@echo "release - package and upload a release"
# 	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 namesdb tests

test:
	source $(VIRTUALENV)/bin/activate; \
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source namesdb setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/namesdb.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ namesdb
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

#release: clean
# 	python setup.py sdist upload
# 	python setup.py bdist_wheel upload

#dist: clean
# 	python setup.py sdist
# 	python setup.py bdist_wheel
# 	ls -l dist

install: clean
# virtualenv
	test -d $(VIRTUALENV) || virtualenv $(VIRTUALENV)
	source $(VIRTUALENV)/bin/activate; \
	pip install -U --download-cache=$(PIP_CACHE_DIR) bpython setuptools
	source $(VIRTUALENV)/bin/activate; \
	pip install -U --download-cache=$(PIP_CACHE_DIR) -r $(INSTALLDIR)/requirements.txt
	source $(VIRTUALENV)/bin/activate; \
	python setup.py install
