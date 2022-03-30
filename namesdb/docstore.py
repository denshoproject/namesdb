import logging
logger = logging.getLogger(__name__)
from ssl import create_default_context

from elasticsearch import Elasticsearch, TransportError
import elasticsearch_dsl

from elastictools import docstore
from . import models

DOCSTORE_TIMEOUT = 5
INDEX_PREFIX = 'namesdb'

ELASTICSEARCH_CLASSES = {
    'all': [
        {'doctype': 'record', 'class': models.Record},
    ]
}

ELASTICSEARCH_CLASSES_BY_MODEL = {
    'record': models.Record,
}


class Docstore(docstore.DocstoreManager):

    def __init__(self, index_prefix, host, settings, connection=None):
        self.index_prefix = index_prefix
        self.host = host
        if connection:
            self.es = connection
        else:
            self.es = docstore.get_elasticsearch(settings)

    def create_indices(self):
        return super(Docstore,self).create_indices(ELASTICSEARCH_CLASSES['all'])

    def delete_indices(self):
        return super(Docstore,self).delete_indices(ELASTICSEARCH_CLASSES['all'])
