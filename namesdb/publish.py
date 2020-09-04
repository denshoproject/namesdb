from datetime import datetime
import configparser
import json
import logging
import os
import sys

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.connections import connections

from . import sourcefile
from . import definitions
from . import docstore
from . import models

def set_logging(level, stream=sys.stdout):
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)-8s %(message)s',
        stream=stream,
    )

LOGGING_LEVEL = 'INFO'

set_logging(LOGGING_LEVEL, stream=sys.stdout)

CONFIG_FILES = ['/etc/ddr/names.cfg', '/etc/ddr/names-local.cfg']
config = configparser.ConfigParser()
configs_read = config.read(CONFIG_FILES)
#if not configs_read:
#    raise NoConfigError('No config file!')



def make_hosts( text ):
    hosts = []
    for host in text.split(','):
        h,p = host.split(':')
        hosts.append( {'host':h, 'port':p} )
    return hosts

def set_hosts_index(hosts, index):
    logging.debug('Connecting %s' % hosts)
    connections.create_connection(hosts=hosts)
    logging.debug('Index %s' % index)
    return Index(index)

def get_connection(hosts):
    return Elasticsearch(hosts)

def format_json(data):
    return json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)


# import records -------------------------------------------------------

def verify_headers(fieldnames, row):
    """Verify that all fields in headers, no extras
    """
    missing = [f for f in fieldnames if f not in row]
    extra = [f for f in row if f not in fieldnames]
    return missing,extra

def map_headers(row):
    """Map header field names to column numbers
    """
    headers_cols = {}
    for n,header in enumerate(row):
        headers_cols[header] = n
    return headers_cols
    
def make_rowd(headers, row, dataset=None):
    """Take list of column values and return a dict
    """
    rowd = {}
    for fieldname,index in headers.items():
        rowd[fieldname] = row[index]
    if dataset:
        rowd['dataset'] = dataset
    return rowd

def load_records(dataset, fields, headers, rows, record_ids=[]):
    """
    @returns: (records, defective_rows) where each defective_row = (n, err, row)
    """
    records = []
    defective_rows = []
    num_rows = len(rows)
    n = 0
    while rows:
        n += 1
        row = rows.pop(0)
        if dataset in ['wra-master', 'far-ancestry']:
            rowd = make_rowd(headers, row, dataset)
        else:
            rowd = make_rowd(headers, row)
        # decide
        if record_ids:
            if (rowd['m_pseudoid'] in record_ids):
                load_this = True
            else:
                load_this = False
        else:
            load_this = True
        # load and include
        if load_this:
            rowd['n'] = n
            try:
                record = models.Record.from_dict(
                    fields, dataset, rowd['m_pseudoid'], rowd
                )
                logging.info('Loading %s/%s %s' % (n, num_rows, record))
                records.append(record)
            except Exception as err:
                defective_rows.append((n,err,row))
    return records,defective_rows

def find_errors(records):
    return [r for r in records if r.errors]

def write_records(ds, indexname, records):
    num_rows = len(records)
    n = 0
    while records:
        n += 1
        record = records.pop(0)
        logging.info('Saving %s/%s %s' % (n, num_rows, record))
        result = record.save(index=indexname, using=ds.es)

def import_records(ds, dataset, stop, csvpath, record_ids=[]):
    doctype = 'record'
    ES_Class = docstore.ELASTICSEARCH_CLASSES_BY_MODEL[doctype]
    indexname = ds.index_name(doctype)
    
    # check args
    if not os.path.exists(csvpath):
        logging.error('ddr-import: CSV file does not exist.')
        sys.exit(1)
    
    if not dataset:
        path,filename = os.path.split(csvpath)
        dataset,ext = os.path.splitext(filename)
    logging.info('Dataset: %s' % dataset)
    if not dataset in definitions.DATASETS.keys():
        logging.error('ddr-import: unknown dataset: %s.' % dataset)
        sys.exit(1)
    
    start = datetime.now()
    
    fields = definitions.DATASETS[dataset]
    logging.info('Fields: %s' % fields)
    
    logging.info('Reading file: %s' % csvpath)
    rows = sourcefile.read_csv(csvpath)
    header_row = rows.pop(0)
    logging.info('ok (%s rows)' % str(len(rows)))
    
    logging.info('Verifying headers')
    missing_headers,extra_headers = verify_headers(fields, header_row)
    if missing_headers:
        logging.error('ddr-import: Missing header(s): %s' % missing_headers)
        logging.error('headers: %s' % header_row)
        sys.exit(1)
    if extra_headers:
        logging.error('ddr-import: Extra header(s): %s' % extra_headers)
        logging.error('headers: %s' % header_row)
        sys.exit(1)
    logging.info('ok')
    headers = map_headers(header_row)
    
    logging.info('Loading records')
    records,defective_rows = load_records(dataset, fields, headers, rows, record_ids)
    logging.info('Loaded %s records' % len(records))
    if defective_rows:
        logging.error('Defective rows: {}'.format(len(defective_rows)))
        for n,err,row in defective_rows:
            logging.error('| row:%s ERROR:"%s" ROW: %s' % (n, err, row))
    
    logging.info('Checking for errors')
    record_errors = find_errors(records)
    record_errors_msg = '%s records contain errors (%s%%):' % (
        len(record_errors),
        float(len(record_errors)) / len(records)
    )
    logging.error(record_errors_msg)
    if record_errors and args.stop:
        for record in record_errors:
            logging.error('| %s: %s' % (record, ', '.join(record.errors)))
        sys.exit(1)
    
    logging.info('Writing to Elasticsearch')
    write_records(ds, indexname, records)

    if defective_rows:
        logging.error('Defective rows: {}'.format(len(defective_rows)))
        for n,err,row in defective_rows:
            logging.error('| row:%s ERROR:"%s" ROW: %s' % (n, err, row))
    
    if record_errors:
        logging.error(record_errors_msg)
        for record in record_errors:
            logging.error('| %s: %s' % (record, ', '.join(record.errors)))
        logging.error(record_errors_msg)
    
    finish = datetime.now()
    elapsed = finish - start
    logging.info('DONE - %s elapsed' % elapsed)


# delete records -------------------------------------------------------

def delete_records(hosts):
    logging.error('NOT IMPLEMENTED YET')


# search ---------------------------------------------------------------

def search(hosts, query):
    logging.info('query: "%s"' % query)
    
    s = Search().doc_type(models.Record)
    s = s.fields(definitions.FIELDS_MASTER)
    s = s.sort('m_pseudoid')
    s = s.query(
        'multi_match', query=query, fields=definitions.FIELDS_MASTER
    )[0:10000]
    response = s.execute()
    records = [models.Record.from_hit(hit) for hit in response]

    logging.info('%s records' % len(records))
    for record in records:
        logging.info(record)
    # if only single result, display it
    if len(records) == 1:
        for field in definitions.FIELDS_MASTER:
            logging.info('%s: %s' % (field, getattr(record, field)))
