#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the Go Redirector. It uses short mnemonics as redirects to otherwise
long URLs. Few remember how to write in cursive, most people don't remember
common phone numbers, and just about everyone needs a way around bookmarks.
"""

__author__ = "Saul Pwanson <saul@pwanson.com>"
__credits__ = "Bill Booth, Bryce Bockman, treebird, Sean Smith, layertwo"

__all__ = ['cfg_port', 'cfg_hostname', 'cfg_fnDatabase', 'cfg_customDocs', 'cfg_contactEmail',
           'cfg_urlFavicon', 'cfg_urlSSO', 'cfg_urlEditBase', 'cfg_sslCertificate', 'cfg_sslPrivateKey',
           'cfg_contactName', 'cfg_sslEnabled', 'InvalidKeyword']

GO_VERSION = 2.0

import configparser
import argparse


"""
Things to do:
- import from old version
- import from txt file (old)
- import from csv (new)
- import from json (new)
- export to csv (w/wo usage)
- export to json (w/wo usage)
- export to text (readable)


Command Line args:
    --import=filename
    --export=filename
    --no_usage
    --cfg=go.cfg
    --version  (display version information)
    --vvv  (1=warning/error, 2=info (default), 3=debug)
    --clear_all_data  (before import/after export)

    remainder of parameters passed:
        -cfg_xxx_field=value
        -IO_kwargs (passed to import/export function)
    
    * Import / Export files can be:
        just the path/filename with extension
        just the extension "including the "."
        just the path/filename without extension (which then defaults to "csv").
            
        extension options:
            .txt (for import) = import from old txt file type.
            .txt (for export) = exports to readable text file. (non-importable)
            .pickle (for import) = import from old database type.
            .csv import/export to csv filetype
            .json import/export to json filetype
"""

"""
Handle command line arguments
"""
parser = argparse.ArgumentParser(description='Go Redirector')

parser.add_argument('--import', help='Import from file')
parser.add_argument('--export', help='Export to file')
parser.add_argument('--no_usage', help='do not import/export usage data', action='store_false')
parser.add_argument('--cfg', help='Config file')
parser.add_argument('--version', help='Show Version and exit', action='version', version='Go Redirector version %s' % GO_VERSION)
parser.add_argument('--v', help='Verbosity (-v=warning/error, -vv=info (default), -vvv=debug)', action='count')
parser.add_argument('--clear_all_data', help='Clear database before import/after export', action='store_true')


parser.add_argument('--cfg_fnDatabase', help=argparse.SUPPRESS)
parser.add_argument('--cfg_urlFavicon', help=argparse.SUPPRESS)
parser.add_argument('--cfg_hostname', help=argparse.SUPPRESS)
parser.add_argument('--cfg_port', help=argparse.SUPPRESS, type=int)
parser.add_argument('--cfg_urlSSO', help=argparse.SUPPRESS)
parser.add_argument('--cfg_sslEnabled', help=argparse.SUPPRESS)
parser.add_argument('--cfg_sslCertificate', help=argparse.SUPPRESS)
parser.add_argument('--cfg_sslPrivateKey', help=argparse.SUPPRESS)
parser.add_argument('--cfg_contactEmail', help=argparse.SUPPRESS)
parser.add_argument('--cfg_contactName', help=argparse.SUPPRESS)
parser.add_argument('--cfg_customDocs', help=argparse.SUPPRESS)



"""
Handle config ini arguments
"""


class GoConfig(object):
    cfg_fnDatabase = "go_db.json"
    cfg_urlFavicon = "https://www.f5.com/favicon.ico"
    cfg_hostname = "localhost"
    cfg_port = 8080
    cfg_urlSSO = None
    cfg_sslEnabled = False
    cfg_sslCertificate = "go.crt"
    cfg_sslPrivateKey = "go.key"
    cfg_contactEmail = None
    cfg_contactName = None
    cfg_customDocs = None

    import_file = None
    export_file = None
    io_type = 'csv'
    export_usage = True
    verboseity = 2
    clear_all_data = False
    io_kwargs = None

    def get_args(self):
        args = parser.parse_args()



    def set_io_data(self, action, usage):


cfg = GoConfig()

config = configparser.ConfigParser()
config.read('../go.cfg')

cfg_fnDatabase = config.get('goconfig', 'cfg_fnDatabase')
cfg_urlFavicon = config.get('goconfig', 'cfg_urlFavicon')
cfg_hostname = config.get('goconfig', 'cfg_hostname')
cfg_port = config.getint('goconfig', 'cfg_port')
cfg_urlSSO = config.get('goconfig', 'cfg_urlSSO')
cfg_urlEditBase = "https://" + cfg_hostname
cfg_sslEnabled = False # default to False
try:
    cfg_sslEnabled = config.getboolean('goconfig', 'cfg_sslEnabled')
except:
    # just preventing from crashing if the cfg option doesn't exist since technically it's optional
    pass
cfg_sslCertificate = config.get('goconfig', 'cfg_sslCertificate')
cfg_sslPrivateKey = config.get('goconfig', 'cfg_sslPrivateKey')
cfg_contactEmail = config.get('goconfig', 'cfg_contactEmail')
cfg_contactName = config.get('goconfig', 'cfg_contactName')
cfg_customDocs = config.get('goconfig', 'cfg_customDocs')

"""
class MyGlobals(object):
    def __init__(self):
        self.db_hnd = None

    def __repr__(self):
        return '%s(hnd=%s)' % (self.__class__.__name__, self.db_hnd)


    def set_handle(self, hnd):
        self.db_hnd = hnd

MYGLOBALS = MyGlobals()
"""

class Error(Exception):
    """base error exception class for go, never raised"""
    pass


class InvalidKeyword(Error):
    """Error raised when a keyword fails the sanity check"""
    pass

