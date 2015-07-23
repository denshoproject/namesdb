# -*- coding: utf-8 -*-

import codecs
from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os
import sys

import unicodecsv as csv


CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'
CSV_QUOTING = csv.QUOTE_ALL


def normalize_text(text):
    """Strip text, convert line endings, etc.
    
    TODO make this work on lists, dict values
    TODO handle those ^M chars
    
    >>> normalize_text('  this is a test')
    'this is a test'
    >>> normalize_text('this is a test  ')
    'this is a test'
    >>> normalize_text('this\r\nis a test')
    'this\\nis a test'
    >>> normalize_text('this\ris a test')
    'this\\nis a test'
    >>> normalize_text('this\\nis a test')
    'this\\nis a test'
    >>> normalize_text(['this is a test'])
    ['this is a test']
    >>> normalize_text({'this': 'is a test'})
    {'this': 'is a test'}
    """
    def process(t):
        try:
            t = t.strip()
            t = t.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')
        except AttributeError:
            pass # doesn't work on ints and lists :P
        return t
    if isinstance(text, basestring):
        return process(text)
    return text

def csv_writer(csvfile):
    """Get a csv.writer object for the file.
    
    @param csvfile: A file object.
    """
    writer = csv.writer(
        csvfile,
        delimiter=CSV_DELIMITER,
        quoting=CSV_QUOTING,
        quotechar=CSV_QUOTECHAR,
    )
    return writer

def csv_reader(csvfile):
    """Get a csv.reader object for the file.
    
    @param csvfile: A file object.
    """
    reader = csv.reader(
        csvfile,
        delimiter=CSV_DELIMITER,
        quoting=CSV_QUOTING,
        quotechar=CSV_QUOTECHAR,
    )
    return reader

def write_csv(path, headers, rows):
    """Write header and list of rows to file.
    
    >>> path = '/tmp/data.csv'
    >>> headers = ['id', 'title', 'description']
    >>> rows = [
    ...     ['ddr-test-123', 'thing 1', 'nothing here'],
    ...     ['ddr-test-124', 'thing 2', 'still nothing'],
    ... ]
    >>> batch.write_csv(path, headers, rows)
    >>> with open(path, 'r') as f:
    ...    f.read()
    '"id","title","description"\r\n"ddr-test-123","thing 1","nothing here"\r\n"ddr-test-124","thing 2","still nothing"\r\n'
    
    @param path: Absolute path to CSV file
    @param headers: list of strings
    @param rows: list of lists
    """
    with codecs.open(path, 'wb', 'utf-8') as f:
        writer = csv_writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

def read_csv(path):
    """Read specified file, return list of rows.
    
    >>> path = '/tmp/data.csv'
    >>> csv_file = '"id","title","description"\r\n"ddr-test-123","thing 1","nothing here"\r\n"ddr-test-124","thing 2","still nothing"\r\n'
    >>> with open(path, 'w') as f:
    ...    f.write(csv_file)
    >>> batch.read_csv(path)
    [
        ['id', 'title', 'description'],
        ['ddr-test-123', 'thing 1', 'nothing here'],
        ['ddr-test-124', 'thing 2', 'still nothing']
    ]
    
    @param path: Absolute path to CSV file
    @returns list of rows
    """
    rows = []
    # the 'U' is for universal-newline mode
    with codecs.open(path, 'rU', 'utf-8', 'replace') as f:
        reader = csv_reader(f)
        for row in reader:
            rows.append(row)
    return rows


