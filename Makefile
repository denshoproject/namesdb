SHELL = /bin/bash
DEBIAN_CODENAME := $(shell lsb_release -sc)

PACKAGE_SERVER=tank.densho.org

PIP_CACHE_DIR=/usr/local/src/pip-cache
INSTALLDIR=/usr/local/src/namesdb
VIRTUALENV=$(INSTALLDIR)/venv/namesdb

ELASTICSEARCH=elasticsearch-1.0.1.deb


.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - (v)check style with flake8"
	@echo "test - (v)run tests quickly with the default Python"
	@echo "test-all - (v)run tests on every Python version with tox"
	@echo "coverage - (v)check code coverage quickly with the default Python"
	@echo "docs - (v)generate Sphinx HTML documentation, including API docs"
# 	@echo "release - package and upload a release"
# 	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo "(v) indicates virtualenv required. Activate thusly:"
	@echo "    $$ source /usr/local/src/env/namesdb/bin/activate"
	@echo "More info: make howto-install"

howto-install:
	@echo "Installation"
	@echo "============"
	@echo ""
	@echo "Basic Debian server netinstall; see ddr-manual."
	@echo "Install SSH keys for root."
	@echo "(see https://help.github.com/articles/generating-ssh-keys/)::"
	@echo ""
	@echo "    # ssh-keygen -t rsa -b 4096 -C \"your_email@example.com\""
	@echo "    # cat ~/.ssh/id_rsa.pub"
	@echo "    Cut and paste public key into GitHub."
	@echo "    # ssh -T git@github.com"
	@echo ""
	@echo "Prepare for install::"
	@echo ""
	@echo "    # apt-get install make"
	@echo "    # git clone git@github.com:densho/namesdb.git /usr/local/src/namesdb"
	@echo "    # cd /usr/local/src/namesdb"
	@echo ""
	@echo "If not running the master branch, switch to it now::"
	@echo ""
	@echo "    # git checkout -b develop origin/develop"
	@echo ""
	@echo "Install encyc-front software, dependencies, and configs::"
	@echo ""
	@echo "    # make install"
	@echo ""
	@echo "Activate virtualenv before using namesdb, generating docs, testing, etc.::"
	@echo ""
	@echo "    $$ source /usr/local/src/env/namesdb/bin/activate"
	@echo ""
	@echo "Install Elasticsearch if desired::"
	@echo ""
	@echo "    # make install-elasticsearch"
	@echo ""

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
	pip install -U --download-cache=$(PIP_CACHE_DIR) bpython setuptools appdirs packaging pyparsing six
	source $(VIRTUALENV)/bin/activate; \
	pip install -U --download-cache=$(PIP_CACHE_DIR) -r $(INSTALLDIR)/requirements.txt
	source $(VIRTUALENV)/bin/activate; \
	python setup.py install

install-elasticsearch:
	@echo ""
	@echo "Elasticsearch ----------------------------------------------------------"
# Elasticsearch is configured/restarted here so it's online by the time script is done.
	apt-get --assume-yes install gdebi openjdk-7-jre
	wget -nc -P /tmp/downloads http://$(PACKAGE_SERVER)/$(ELASTICSEARCH)
	gdebi --non-interactive /tmp/downloads/$(ELASTICSEARCH)
	cp $(INSTALLDIR)/debian/conf/elasticsearch.yml /etc/elasticsearch/
	chown root.root /etc/elasticsearch/elasticsearch.yml
	chmod 644 /etc/elasticsearch/elasticsearch.yml
	@echo "${bldgrn}search engine (re)start${txtrst}"
	/etc/init.d/elasticsearch restart
