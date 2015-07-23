# -*- coding: utf-8 -*-

from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os
import sys

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Index
from elasticsearch_dsl import DocType, String, Date, Nested, Boolean, analysis
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

DOCSTORE_INDEX = 'namesdb-dev'


class Record(DocType):
    """FAR/WRA record model
    
    m_pseudoid = m_camp + lastname + birthyear + firstname
    """
    m_pseudoid = String(index='not_analyzed')
    m_dataset = String(index='not_analyzed')
    m_camp = String(index='not_analyzed')
    m_lastname = String()
    m_firstname = String()
    m_birthyear = String(index='not_analyzed')
    m_gender = String(index='not_analyzed')
    m_familyno = String(index='not_analyzed')
    m_individualno = String(index='not_analyzed')
    m_originalstate = String(index='not_analyzed')
    errors = String()
    
    f_originalcity = String(index='not_analyzed')
    f_othernames = String(index='not_analyzed')
    f_maritalstatus = String(index='not_analyzed')
    f_citizenship = String(index='not_analyzed')
    f_alienregistration = String(index='not_analyzed')
    f_entrytype = String(index='not_analyzed')
    f_entrydate = Date()
    f_departuretype = String(index='not_analyzed')
    f_departuredate = Date()
    f_destinationstate = String(index='not_analyzed')
    f_destinationcity = String(index='not_analyzed')
    f_campaddress = String(index='not_analyzed')
    f_farlineid = String(index='not_analyzed')
    
    w_assemblycenter = String(index='not_analyzed')
    w_originaladdress = String(index='not_analyzed')
    w_birthcountry = String(index='not_analyzed')
    w_fatheroccup = String(index='not_analyzed')
    w_fatheroccupcat = String(index='not_analyzed')
    w_yearsschooljapan = String(index='not_analyzed')
    w_gradejapan = String(index='not_analyzed')
    w_schooldegree = String(index='not_analyzed')
    w_yearofusarrival = String(index='not_analyzed')
    w_timeinjapan = String(index='not_analyzed')
    w_notimesinjapan = String(index='not_analyzed')
    w_ageinjapan = String(index='not_analyzed')
    w_militaryservice = String(index='not_analyzed')
    w_maritalstatus = String(index='not_analyzed')
    w_ethnicity = String(index='not_analyzed')
    w_birthplace = String(index='not_analyzed')
    w_citizenshipstatus = String(index='not_analyzed')
    w_highestgrade = String(index='not_analyzed')
    w_language = String(index='not_analyzed')
    w_religion = String(index='not_analyzed')
    w_occupqual1 = String(index='not_analyzed')
    w_occupqual2 = String(index='not_analyzed')
    w_occupqual3 = String(index='not_analyzed')
    w_occuppotn1 = String(index='not_analyzed')
    w_occuppotn2 = String(index='not_analyzed')
    w_filenumber = String(index='not_analyzed')
    
    class Meta:
        index = DOCSTORE_INDEX
        doc_type = 'names-record'
    
    def __repr__(self):
        return "<Record '%s'>" % self.m_pseudoid
