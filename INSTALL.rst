============
Installation
============

Basic Debian server netinstall; see `ddr-manual`.

Install SSH keys for root.
(see https://help.github.com/articles/generating-ssh-keys/)::

    # ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    # cat ~/.ssh/id_rsa.pub
    Cut and paste public key into GitHub.
    # ssh -T git@github.com

Prepare for install::

    # apt-get install make
    # git clone git@github.com:densho/namesdb.git /usr/local/src/namesdb
    # cd /usr/local/src/namesdb

If not running the master branch, switch to it now::

    # git checkout -b develop origin/develop

Install encyc-front software, dependencies, and configs::

    # make install

Activate virtualenv before using namesdb, generating docs, testing, etc.::

    $ source /usr/local/src/env/namesdb/bin/activate

Install Elasticsearch if desired::

    # make install-elasticsearch

Run the command with the `--help` flag for more usage info and examples::

    $ namesdb --help

Names Registry data is in https://github.com/denshoproject/namesdb-data.
