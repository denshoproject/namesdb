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


class Docstore(docstore.Docstore):

    def __init__(self, index_prefix, host, settings, connection=None):
        self.index_prefix = index_prefix
        self.host = host
        if connection:
            self.es = connection
        else:
            self.es = docstore.get_elasticsearch(settings)

    def create_indices(self):
        """Create indices for each model defined in namesdb/models.py
        
        See also ddr-defs/repo_models/elastic.py
        """
        statuses = []
        for i in ELASTICSEARCH_CLASSES['all']:
            status = self.create_index(
                self.index_name(i['doctype']),
                i['class']
            )
            statuses.append(status)
        return statuses
    
    def create_index(self, indexname, dsl_class):
        """Creates the specified index if it does not already exist.
        
        Uses elasticsearch-dsl classes defined in namesdb/models.py
        See also ddr-defs/repo_models/elastic.py
        
        @param indexname: str
        @param dsl_class: elasticsearch_dsl.Document class
        @returns: JSON dict with status codes and responses
        """
        logger.debug('creating index {}'.format(indexname))
        if self.index_exists(indexname):
            status = '{"status":400, "message":"Index exists"}'
            logger.debug('Index exists')
            #print('Index exists')
        else:
            index = elasticsearch_dsl.Index(indexname)
            #print('index {}'.format(index))
            index.aliases(default={})
            #print('registering')
            out = index.document(dsl_class).init(index=indexname, using=self.es)
            if out:
                status = out
            elif self.index_exists(indexname):
                status = {
                    "name": indexname,
                    "present": True,
                }
            #print(status)
            #print('creating index')
        return status
    
    def delete_indices(self):
        """Deletes indices for each model defined in namesdb/models.py
        
        See also ddr-defs/repo_models/elastic.py
        """
        statuses = []
        for i in ELASTICSEARCH_CLASSES['all']:
            status = self.delete_index(
                self.index_name(i['doctype'])
            )
            statuses.append(status)
        return statuses
    
    def delete_index(self, indexname):
        """Delete the specified index.
        
        @returns: JSON dict with status code and response
        """
        logger.debug('deleting index: %s' % indexname)
        if self.index_exists(indexname):
            status = self.es.indices.delete(index=indexname)
        else:
            status = {
                "name": indexname,
                "status": 500,
                "message": "Index does not exist",
            }
        logger.debug(status)
        return status
