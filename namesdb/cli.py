DESCRIPTION = """"""

HELP = """
Sample usage:

    # Create and destroy indexes
    $ namesdb create -H localhost:9200
    $ namesdb destroy -H localhost:9200 --confirm
    
    # Check status
    $ namesdb status -H localhost:9200
    
    # Import records
    $ namesdb post -H localhost:9200 /tmp/namesdb-data/far-manzanar.csv
    
    # Delete records
    $ namesdb delete -H localhost:9200 /tmp/namesdb-data/far-manzanar.csv
    
    # Search for record
    $ namesdb search -H localhost:9200 yano
    $ namesdb search -H localhost:9200 "George Takei"
    $ namesdb search -H localhost:9200 7-manzanar_zoriki_1922_masayuki

Note: You can set environment variables for HOSTS and INDEX.:

    $ export ES_HOSTS=localhost:9200
    $ export ES_INDEX=namesdb-dev

"""

import os
import sys

import click

from . import docstore
from . import publish



@click.group()
@click.option('--debug','-d', is_flag=True, default=False)
def namesdb(debug):
    """namesdb - Uploads FAR and WRA records from CSV to Elasticsearch.
    
    \b
    See "namesdb help" for examples.
    """
    if debug:
        click.echo('Debug mode is on')


@namesdb.command()
def help():
    """Detailed help and usage examples
    """
    click.echo(HELP)


def hosts_index(hosts):
    if not hosts:
        click.echo('Set host using --host or the ES_HOST environment variable.')
        sys.exit(1)
    return publish.make_hosts(hosts)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
def create(hosts):
    """Create specified Elasticsearch index and upload mappings.
    """
    hosts = hosts_index(hosts)
    docstore.Docstore(hosts).create_indices()


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--confirm', is_flag=True,
              help='Yes I really want to delete this index.')
def destroy(hosts, confirm):
    """Destroy specified Elasticsearch index and all its records.
    
    Think twice before you do this, then think again.
    """
    """Delete indices (requires --confirm).
    
    \b
    It's meant to sound serious. Also to not clash with 'delete', which
    is for individual documents.
    """
    if confirm:
        hosts = hosts_index(hosts)
        docstore.Docstore(hosts).delete_indices()
    else:
        click.echo("Add '--confirm' if you're sure you want to do this.")


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
def status(hosts):
    """Print status info.
    
    More detail since you asked.
    """
    ds = docstore.Docstore(hosts)
    s = ds.status()
    
    print('------------------------------------------------------------------------',0)
    print('Elasticsearch')
    # config file
    print('DOCSTORE_HOST  (default): %s' % hosts)
    
    try:
        pingable = ds.es.ping()
        if not pingable:
            print("Can't ping the cluster!")
            return
    except elasticsearch.exceptions.ConnectionError:
        print("Connection error when trying to ping the cluster!")
        return
    print('ping ok')
    
    print('Indexes')
    index_names = ds.es.indices.stats()['indices'].keys()
    for i in index_names:
        print('- %s' % i)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--dataset','-d', help='Dataset name (if not in filename).')
@click.option('--stop','-s', is_flag=True, help='Stop if errors detected.')
@click.argument('csvpath') # Absolute path to CSV file (named ${dataset}.csv).
def post(hosts, dataset, stop, csvpath):
    """Read records from CSV file and push to Elasticsearch.
    
    In normal usage the filename should consist of dataset plus .csv:
        $ namesdb import -H localhost:9200 /tmp/namesdb-data/far-manzanar.csv
    
    If filename does not contain the dataset name, specify using -d/--dataset:
        $ namesdb import -H localhost:9200 -d far-manzanar /tmp/random-file.csv
    """
    hosts = hosts_index(hosts)
    ds = docstore.Docstore(hosts)
    publish.import_records(ds, dataset, stop, csvpath)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.argument('csvpath') # Absolute path to CSV file (named ${dataset}.csv).
def delete(hosts):
    """Delete records in CSV file from Elasticsearch.
    
    Use this function to delete all records for a given dataset by pointing
    the function at the CSV file.  To delete only certain records, make a CSV file
    containing a single column containing NamesDB pseudo IDs, having the column
    header "m_pseudoid".
    """
    hosts = hosts_index(hosts)
    publish.delete_records(hosts, args)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.argument('query') # Search query.
def search(hosts, query):
    """Perform search query, return results in raw JSON.
    
    Whatever text follows the HOST and INDEX args will be pasted directly into
    the body of an Elasticsearch "match" query.
    
    Examples:
        $ namesdb search -H localhost:9200 yano
        $ namesdb search -H localhost:9200 "George Takei"
        $ namesdb search -H localhost:9200 7-manzanar_zoriki_1922_masayuki
    """
    hosts = hosts_index(hosts)
    publish.search(hosts, query)


if __name__ == '__main__':
    cli(auto_envvar_prefix='NAMESDB')
