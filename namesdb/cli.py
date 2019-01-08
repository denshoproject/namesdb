DESCRIPTION = """"""

HELP = """
Sample usage:

    # Create and destroy indexes
    $ namesdb create -H localhost:9200 -i namesdb-stage
    $ namesdb destroy -H localhost:9200 -i namesdb-stage --confirm
    
    # Check status
    $ namesdb status -H localhost:9200 -i namesdb-stage
    
    # Import records
    $ namesdb post -H localhost:9200 -i namesdb-stage /tmp/namesdb-data/far-manzanar.csv
    
    # Delete records
    $ namesdb delete -H localhost:9200 -i namesdb-stage /tmp/namesdb-data/far-manzanar.csv
    
    # Search for record
    $ namesdb search -H localhost:9200 -i namesdb-stage yano
    $ namesdb search -H localhost:9200 -i namesdb-stage "George Takei"
    $ namesdb search -H localhost:9200 -i namesdb-stage 7-manzanar_zoriki_1922_masayuki

Note: You can set environment variables for HOSTS and INDEX.:

    $ export ES_HOSTS=localhost:9200
    $ export ES_INDEX=namesdb-dev

"""

import os
import sys

import click

from namesdb import publish



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


def hosts_index(hosts, index):
    if not hosts and index:
        click.echo('hosts and index are required fields.')
        sys.exit(1)
    hosts = publish.make_hosts(hosts)
    index = publish.set_hosts_index(hosts, index)
    return hosts,index


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--index','-i', envvar='ES_INDEX', help='Elasticsearch index.')
def create(hosts, index):
    """Create specified Elasticsearch index and upload mappings.
    """
    hosts,index = hosts_index(hosts, index)
    publish.create_index(hosts, index)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--index','-i', envvar='ES_INDEX', help='Elasticsearch index.')
def destroy(hosts, index):
    """Destroy specified Elasticsearch index and all its records.
    
    Think twice before you do this, then think again.
    """
    hosts,index = hosts_index(hosts, index)
    publish.dstroy_index(hosts, index)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--index','-i', envvar='ES_INDEX', help='Elasticsearch index.')
def status(hosts, index):
    """Check status of specified Elasticsearch index.
    
    Useful for checking whether or not specified index exits before destroying it.
    """
    hosts,index = hosts_index(hosts, index)
    publish.status(hosts, index)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--index','-i', envvar='ES_INDEX', help='Elasticsearch index.')
@click.option('--dataset','-d', help='Dataset name (if not in filename).')
@click.option('--stop','-s', is_flag=True, help='Stop if errors detected.')
@click.argument('csvpath') # Absolute path to CSV file (named ${dataset}.csv).
def post(hosts, index, dataset, stop, csvpath):
    """Read records from CSV file and push to Elasticsearch.
    
    In normal usage the filename should consist of dataset plus .csv:
        $ namesdb import -H localhost:9200 -i namesdb-stage /tmp/namesdb-data/far-manzanar.csv
    
    If filename does not contain the dataset name, specify using -d/--dataset:
        $ namesdb import -H localhost:9200 -i namesdb-stage -d far-manzanar /tmp/random-file.csv
    """
    hosts,index = hosts_index(hosts, index)
    publish.import_records(hosts, index, dataset, stop, csvpath)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--index','-i', envvar='ES_INDEX', help='Elasticsearch index.')
@click.argument('csvpath') # Absolute path to CSV file (named ${dataset}.csv).
def delete(hosts, index):
    """Delete records in CSV file from Elasticsearch.
    
    Use this function to delete all records for a given dataset by pointing
    the function at the CSV file.  To delete only certain records, make a CSV file
    containing a single column containing NamesDB pseudo IDs, having the column
    header "m_pseudoid".
    """
    hosts,index = hosts_index(hosts, index)
    publish.delete_records(hosts, index, args)


@namesdb.command()
@click.option('--hosts','-H', envvar='ES_HOST', help='Elasticsearch hosts.')
@click.option('--index','-i', envvar='ES_INDEX', help='Elasticsearch index.')
@click.argument('query') # Search query.
def search(hosts, index, query):
    """Perform search query, return results in raw JSON.
    
    Whatever text follows the HOST and INDEX args will be pasted directly into
    the body of an Elasticsearch "match" query.
    
    Examples:
        $ namesdb search -H localhost:9200 -i namesdb-stage yano
        $ namesdb search -H localhost:9200 -i namesdb-stage "George Takei"
        $ namesdb search -H localhost:9200 -i namesdb-stage 7-manzanar_zoriki_1922_masayuki
    """
    hosts,index = hosts_index(hosts, index)
    publish.search(hosts, index, query)


if __name__ == '__main__':
    cli(auto_envvar_prefix='NAMESDB')
