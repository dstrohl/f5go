

import configparser
import sys, os
from collections import namedtuple
from prog.exceptions import InsecureConfig, log_error
import logging
from prog.constants import TF

__all__ = ['config', 'log', 'Config']
"""
class UNSET():
    def __init__(self):
        self._unset_ = True

unset = UNSET()
"""
log = logging.getLogger('go')

DEFAULT_CONFIG_FILE = 'go.cfg'
OLD_CONFIG_SECTION = 'goconfig'

# if DEBUG_CONFIG is True, the config file will not load, and allow insecure will be set to True
DEBUG_CONFIG = False


class ConfigItem():
    def __init__(self,
                 section,
                 attr_name,
                 default,
                 cfg_name=None,
                 old_name=None,
                 val_type=None,
                 description=None,
                 ):
        self.attr_name = attr_name
        self.section = section
        self.default = default
        self.cfg_name = cfg_name or attr_name
        self.old_name = old_name or self.cfg_name
        if val_type is None:
            self.val_type = default.__class__.__name__
        else:
            self.val_type = val_type
        self.description = description
CI = ConfigItem

DEFAULT_CONFIG_ITEMS = [
    CI('GO', 'allow_special', True),
    CI('GO', 'allow_edits', True),
    CI('GO', 'log_file', 'go.log', val_type='file'),
    CI('GO', 'log_level', 'info'),
    CI('GO', 'log_file_format', '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'),
    CI('GO', 'default_replacement_error_string', ''),
    CI('GO', 'default_replacement_error_handling', 'ERROR'),

    CI('NETWORK', 'hostname', "localhost", old_name='cfg_hostname'),
    CI('NETWORK', 'port', 8080, old_name='cfg_port'),
    CI('NETWORK', 'ssl_enabled', False, old_name='cfg_sslEnabled'),
    CI('NETWORK', 'ssl_certificate', '', old_name='cfg_sslCertificate', val_type='file'),
    CI('NETWORK', 'ssl_private_key', '', old_name='cfg_sslPrivateKey', val_type='file'),

    CI('USERS', 'url_sso', None, old_name='cfg_urlSso'),
    CI('USERS', 'unknown_user', 'unknown'),
    CI('USERS', 'admin_users', 'admin'),
    CI('USERS', 'admin_passwords_clear', 'password'),
    CI('USERS', 'admin_passwords', ''),

    CI('UI', 'urlfavicon', "https://www.f5.com/favicon.ico", old_name="cfg_urlFavicon"),
    CI('UI', 'contact_email', '', old_name='cfg_contactEmail'),
    CI('UI', 'contact_name', '', old_name='cfg_contactName'),
    CI('UI', 'custom_docs', '', old_name='cfg_customDocs'),

    CI('DATABASE', 'data_file', "godb.json", val_type='file'),
    CI('DATABASE', 'save_on_change', True),
    CI('DATABASE', 'old_fndatabase', 'godb.pickle', old_name='fnDatabase', val_type='file'),

    CI('MAXES', 'max_last_x', 20),
    CI('MAXES', 'max_recent_days', 7)
]


"""
DEFAULT_CONFIG = dict(
    GO = dict(
        allow_special = True,
        allow_edits = True,
        log_file = 'go.log',
        log_level = 'info',
        log_file_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        default_replacement_error_string = '',
        default_replacement_error_handling = 'ERROR',
        auto_save_config = True,
    ),
    NETWORK = dict(
        hostname = "localhost",
        port = 8080,
        ssl_enabled = False,
        ssl_certificate ='',
        ssl_private_key ='',
    ),
    USERS = dict(
        url_sso = None,
        unknown_user ='unknown',
        admin_users ='admin',
        admin_passwords_clear ='password',
        admin_passwords =''
    ),
    UI = dict(
        urlfavicon ="https://www.f5.com/favicon.ico",
        contact_email ='',
        contact_name ='',
        custom_docs ='',
    ),
    DATABASE = dict(
        data_file ="godb.json",
        save_on_change = True,
        old_fndatabase ='godb.pickle',
    ),
    MAXES = dict(
        max_last_x = 20,
        max_recent_days = 7,

    )
)

OLD_FIELDS = [
    ("cfg_fnDatabase","cfg_fnDatabase"),
    ("cfg_urlfavicon","cfg_urlfavicon"),
    ("cfg_hostname","cfg_hostname"),
    ("cfg_port","cfg_port"),
    ("cfg_urlSso","cfg_urlSso"),
    ("cfg_sslEnabled","cfg_sslEnabled"),
    ("cfg_sslCertificate","cfg_sslCertificate"),
    ("cfg_sslPrivateKey","cfg_sslPrivateKey"),
    ("cfg_contact_email","cfg_contact_email"),
    ("cfg_contact_name","cfg_contact_name"),
    ("cfg_custom_docs","cfg_custom_docs"),
]

PATH_FIELDS = ['filename', 'log_file', 'ssl_certificate', 'ssl_private_key', 'data_file', 'old_fndatabase']
"""

CONFIG_ITEMS = {}
OLD_CONFIG_ITEMS = {}

for item in DEFAULT_CONFIG_ITEMS:
    if item.attr_name in CONFIG_ITEMS:
        raise log_error(ValueError, 'Error, duplicate config var found during setup: {}'.format(item.attr_name))
    CONFIG_ITEMS[item.attr_name] = item
    if item.old_name:
        OLD_CONFIG_ITEMS[item.old_name] = item.attr_name



"""
for sect, items in DEFAULT_CONFIG.items():
    for item, val in items.items():
        if isinstance(val, bool):
            val_type = 'bool'
        elif isinstance(val, int):
            val_type = 'int'
        else:
            val_type = 'str'
        if item in CONFIG_ITEMS:
        if item in OLD_FIELDS:
            old_field = 'cfg_{}'.format(item)
        else:
            old_field = ''
        path_field = item in PATH_FIELDS

        CONFIG_ITEMS[item] = CONFIG_ITEM(item, sect, val, val_type, old_field, path_field)
"""

class Config():
    found_old_config = False
    found_new_config = False
    filename = DEFAULT_CONFIG_FILE

    # GO
    allow_special: bool
    allow_edits: bool
    log_file: str
    log_level: str
    log_file_format: str
    default_replacement_error_string: str
    default_replacement_error_handling: str


    # NETWORK
    hostname: str
    port: int
    ssl_enabled: bool
    ssl_certificate: str
    ssl_private_key: str

    # USERS
    url_sso:str
    unknown_user: str
    admin_users: list
    admin_passwords: list
    admin_passwords_clear: list

    # UI
    url_favicon: str
    contact_email: str
    contact_name: str
    custom_docs: str

    # DATABASE
    data_file: str
    save_on_change: bool
    old_fndatabase: str

    # MAXES
    max_last_x: int
    max_recent_days: int

    insecure_system = False
    allow_insecure = False

    config_loaded = False
    auto_save_config = False
    kwargs_overrides = None
    log_setup = False
    dirty_data = False


    def __init__(self, base_dir='', filename=DEFAULT_CONFIG_FILE, **kwargs):
        self.base_dir = base_dir
        self.kwargs_overrides = {}
        self.config_data = {}
        self.admin_users = {}

        self.filename = self.fix_path(filename)
        if self.filename:
            log.info('Config file set to: {}'.format(self.filename))
        else:
            log.info('No config file name set, will use defaults')
        self.set_overrides(**kwargs)

    def set_overrides(self, **kwargs):
        for k, v in kwargs.items():
            log.debug('Setting overried: %s -> %s ' % (k, v))
            if k in CONFIG_ITEMS:
                self.kwargs_overrides[k] = v
            else:
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    raise log_error(ValueError, 'Invalid keyword argument: %s=%s' % (k, v))

    def fix_path(self, path_item):
        if not self.base_dir or not path_item:
            return path_item
        return os.path.join(self.base_dir, path_item)


    def load_item(self, item, value=None):

        check_override = True

        if value is None and item not in self.kwargs_overrides:
            check_override = False
            value = CONFIG_ITEMS[item].default
            log.debug('%s using default value of %s', item, value)

        if item in self.kwargs_overrides:
            check_override = False
            value = self.kwargs_overrides[item]
            log.debug('%s using OVERRIDE value of %s', item, value)

        item_rec = CONFIG_ITEMS[item]

        if item_rec.val_type == 'bool':
            value = TF[value]
        elif item_rec.val_type == 'int':
            value = int(value)
        elif item_rec.val_type == 'file':
            value = self.fix_path(value)

        log.debug('Loading config var %s, value: %r' % (item, value))

        if check_override and value != self.config_data[item]:
            self.dirty_data = True

        self.config_data[item] = value


    def load_config(self, **kwargs):
        if kwargs:
            self.set_overrides(**kwargs)

        for k in CONFIG_ITEMS:
            self.load_item(k)

        if self.filename:
            self.read_config()

        self.check_config()

        if self.filename and self.found_old_config and not self.found_new_config:
            log.info('Old config found and no new config entries, re-writing with new config.')
            self.save_config()


    def read_config(self):
        if not self.filename:
            return

        fconfig = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=None)
        log.info('==============================================================')
        log.info('Reading Config File: {}'.format(self.filename))
        log.info('==============================================================')
        try:
            fconfig.read(self.filename)
        except configparser.Error:
            log.error('No Config File Found, using DEFAULTS')
            return
        log.info('Reading Config File: {}'.format(self.filename))

        if OLD_CONFIG_SECTION in fconfig:
            log.info('Old Config Section Found, loading first')
            self.found_old_config = True
            for key, attr_name in OLD_CONFIG_ITEMS.items():
                value = fconfig.get(OLD_CONFIG_SECTION, key)
                self.load_item(attr_name, value)

        for item_rec in CONFIG_ITEMS.values():
            if item_rec.section in fconfig and item_rec.cfg_name in fconfig[item_rec.section]:
                self.found_new_config = True
                self.load_item(item_rec.attr_name, fconfig[item_rec.section][item_rec.cfg_name])

        self.config_loaded = True
        log.info('Config Loaded!')

    def check_config(self):
        # self.sanitize_config()

        if self.config_data['ssl_certificate'] and self.config_data['ssl_private_key']:
            self.config_data['ssl_enabled'] = True

        if self.config_data['ssl_enabled']:
            self.config_data['url_edit_base'] = "https://" + self.config_data['hostname']
        else:
            self.config_data['url_edit_base'] = "http://" + self.config_data['hostname']

        if not self.config_data['ssl_enabled']:
            log.error("SSL Not Enabled, system will be insecure if auth is needed.")
            self.insecure_system = True

        if not self.config_data['url_sso']:
            log.error("SSO not configured, system will be insecure if auth is neecded.")
            self.insecure_system = True

        if not self.allow_insecure:
            log.error('INSECURE CONFIG DETECTED')
            raise InsecureConfig('configuration is insecure')
        else:
            log.warning('OPERATING IN INSECURE MODE')

        if not self.log_setup:
            log.setLevel(self.config_data['log_level'])
            formatter = logging.Formatter(self.config_data['log_file_format'])
            sh = logging.StreamHandler(stream=sys.stdout)
            sh.setFormatter(formatter)
            if self.config_data['log_file']:
                fh = logging.FileHandler(self.config_data['log_file'])
                fh.setFormatter(formatter)
                log.addHandler(fh)

            log.addHandler(sh)
            self.log_setup = True

    def save_config(self):
        log.info('Saving Config...')
        fconfig = configparser.ConfigParser(interpolation=None)
        for item_data in CONFIG_ITEMS.values():
            if item_data.section not in fconfig:
                log.debug('Saving section: {}'.format(item_data.section))
                fconfig[item_data.section] = {}
            log.debug('    Saving item: {}'.format(item_data.cfg_name))
            fconfig[item_data.section][item_data.cfg_name] = str(self.config_data[item_data.cfg_name])

        with open(self.filename, 'w') as configfile:
            fconfig.write(configfile)
        log.info('Config Saved')


    """
    def sanitize_config(self):
        for item, value in self.config_data.items():
            item_meta = CONFIG_ITEMS.get(item)
            if not item_meta:
                log.warning(f"Unknown config item: {item}")
                continue

            if item_meta.val_type == 'bool' and not isinstance(value, bool):
                log.error(
                    f"Invalid value for {item}: expected boolean, got {type(value).__name__}. Resetting to default.")
                self.config_data[item] = item_meta.default

            elif item_meta.val_type == 'int' and not isinstance(value, int):
                log.error(
                    f"Invalid value for {item}: expected integer, got {type(value).__name__}. Resetting to default.")
                self.config_data[item] = item_meta.default

            elif item_meta.val_type == 'str' and not isinstance(value, str):
                log.error(
                    f"Invalid value for {item}: expected string, got {type(value).__name__}. Resetting to default.")
                self.config_data[item] = item_meta.default
    """

    def __getattr__(self, item):
        if not self.config_loaded:
            self.load_config()
        if item not in self.config_data:
            log.error('Config item not found: '+item)
            raise AttributeError('Config section "' + item + '" not found.')
        return self.config_data[item]


config = Config()


