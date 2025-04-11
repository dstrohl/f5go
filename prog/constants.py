from collections import namedtuple


PRIORITY = 'PRIORITY'
RANDOM = 'RANDOM'
SELECT = 'SELECT'
LAST_EDIT = 'LAST_EDIT'

SELECT_LOOKUP = dict(
    PRIORITY = 'By Priority',
    RANDOM = 'Random selection',
    SELECT = 'Select from list',
    LAST_EDIT = 'Last Edited',
)

REPLACE_ERROR_RAISE = 'ERROR'
REPLACE_ERROR_REPLACE = 'REPLACE'

LOAD_TYPE_NEW = 'NEW'
LOAD_TYPE_UPDATE = 'REPLACE'
LOAD_TYPE_IMPORT = 'SELECT'


DEFAULT_CONFIG_FILE = 'go.cfg'
OLD_CONFIG_SECTION = 'goconfig'

DEBUG_CONFIG = False

TF = {
    'Yes': True,
    'No': False,
    'yes': True,
    'no': False,
    'On': True,
    'Off': False,
    'on':True,
    'off': False,
    'YES': True,
    'NO': False,
    'ON': True,
    'OFF': False,
    'True': True,
    'true': True,
    'False': False,
    'false': False,
    'TRUE': True,
    'FALSE': False,
    1: True,
    0: False,
}