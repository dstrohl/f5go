def sanitize_config(self):
    """Validate and sanitize configuration values."""
    for item, value in self.config_data.items():
        item_meta = CONFIG_ITEMS.get(item)
        if not item_meta:
            log.warning(f"Unknown config item: {item}")
            continue

        if item_meta.val_type == 'bool' and not isinstance(value, bool):
            log.error(f"Invalid value for {item}: expected boolean, got {type(value).__name__}. Resetting to default.")
            self.config_data[item] = item_meta.default

        elif item_meta.val_type == 'int' and not isinstance(value, int):
            log.error(f"Invalid value for {item}: expected integer, got {type(value).__name__}. Resetting to default.")
            self.config_data[item] = item_meta.default

        elif item_meta.val_type == 'str' and not isinstance(value, str):
            log.error(f"Invalid value for {item}: expected string, got {type(value).__name__}. Resetting to default.")
            self.config_data[item] = item_meta.default


import configparser
import sys, os
from collections import namedtuple
from prog.exceptions import InsecureConfig
import logging

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

DEFAULT_CONFIG = dict(
    GO = dict(
        allowspecial = True,
        allowedits = True,
        log_file = 'go.log',
        log_level = 'info',
        log_file_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        default_replacement_error_string = '',
        default_replacement_error_handling = 'ERROR',
    ),
    NETWORK = dict(
        hostname = "localhost",
        port = 8080,
        sslenabled = False,
        sslcertificate = '',
        sslprivatekey = '',
    ),
    USERS = dict(
        urlsso = None,
        unknownuser = 'unknown',
        adminusers = 'admin',
        adminpasswordsclear ='password',
        adminpasswords =''
    ),
    UI = dict(
        urlfavicon ="https://www.f5.com/favicon.ico",
        contactemail ='',
        contactname ='',
        customdocs ='',
    ),
    DATABASE = dict(
        database_section = 'DATABASE',
        fndatabase ="godb.json",
        saveonchange = True,
        oldfndatabase ='godb.pickle',
        automigrate = True,
    ),
    MAXES = dict(
        max_last_x = 20,
        max_recent_days = 7,

    )
)

OLD_FIELDS = [
    "fndatabase",
    "urlfavicon",
    "hostname",
    "port",
    "urlsso",
    "sslenabled",
    "sslcertificate",
    "sslprivatekey",
    "contactemail",
    "contactname",
    "customdocs",
]

CONFIG_ITEM = namedtuple('CONFIG_ITEM', ['name','section', 'default', 'val_type', 'old_field'])
CONFIG_ITEMS = {}
for sect, items in DEFAULT_CONFIG.items():
    for item, val in items.items():
        if isinstance(val, bool):
            val_type = 'bool'
        elif isinstance(val, int):
            val_type = 'int'
        else:
            val_type = 'str'
        if item in CONFIG_ITEMS:
            raise ValueError('Error, duplicate config var setup: {} is in both {} and {}'.format(item, sect, CONFIG_ITEMS[item].section))
        if item in OLD_FIELDS:
            old_field = 'cfg_{}'.format(item)
        else:
            old_field = ''
        CONFIG_ITEMS[item] = CONFIG_ITEM(item, sect, val, val_type, old_field)


class Config():
    found_old_config = False
    found_new_config = False
    path_fields = ['filename', 'log_file', 'sslcertificate', 'sslprivatekey' , 'fndatabase', 'oldfndatabase']
    filename = DEFAULT_CONFIG_FILE

    log_file: str
    log_level: str
    log_file_format: str
    allowspecial: bool
    allowedits: bool
    hostname: str
    port: int
    sslenabled: bool
    sslcertificate: str
    sslprivatekey: str
    urlsso:str
    unknownuser: str
    adminuserss: str
    adminpasswords: str
    adminpasswordsclear: str
    urlfavicon: str
    contactemail: str
    contactname: str
    customdocs: str
    fndatabase: str
    saveonchange: bool
    oldfndatabase: str
    automigrate: bool
    max_last_x: int
    max_recent_days: int
    default_replacement_error_string: str
    default_replacement_error_handling: str

    insecure_system = False
    allow_insecure = False

    config_loaded = False
    auto_save_config = False
    kwargs_overrides = None
    log_setup = False

    def __init__(self, base_dir='', **kwargs):
        self.base_dir = base_dir
        self.kwargs_overrides = {}
        self.config_data = {}
        self.admin_users = {}
        self.set_overrides(**kwargs)

    def set_overrides(self, **kwargs):
        for k, v in kwargs.items():
            if k in CONFIG_ITEMS:
                self.kwargs_overrides[k] = v
            else:
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    raise ValueError('Invalid keyword argument: %s=%s' % (k, v))

    def load_config(self, **kwargs):

        tmp_kwargs = self.kwargs_overrides.copy()
        tmp_kwargs.update(kwargs)

        for k, v in CONFIG_ITEMS.items():
            val = v.default
            if k in tmp_kwargs:
                val = tmp_kwargs[k]
            self.config_data[k] = val

        if self.filename:
            self.read_config()

        self.config_data.update(tmp_kwargs)

        self.check_config()

        if self.filename and self.oldfndatabase and not self.found_new_config:
            log.info('Old config found and no new config entries, re-writing with new config.')
            self.save_config()


    def read_config(self):
        def get_item(cfg, fi, is_old=False):
            if is_old:
                n = fi.old_field
            else:
                n = fi.name
            if fi.val_type == 'bool':
                log.debug('reading BOOL item {}'.format(n))
                self.config_data[fi.name] = cfg.getboolean(n)
            elif fi.val_type == 'int':
                log.debug('reading INT item {}'.format(n))
                self.config_data[fi.name] = cfg.getint(n)
            else:
                log.debug('reading STR item {}'.format(n))
                self.config_data[fi.name] = cfg.get(n)

        fconfig = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=None)
        try:
            fconfig.read(self.filename)
        except configparser.Error:
            log.error('No Config File Found, using DEFAULTS')
            return

        if OLD_CONFIG_SECTION in fconfig:
            self.found_old_config = True
            for key in OLD_FIELDS:
                item_data = CONFIG_ITEMS[key]
                if item_data.old_field in fconfig[OLD_CONFIG_SECTION]:
                    log.debug('Config Section {} Item {} found in config file'.format(OLD_CONFIG_SECTION, item_data.old_field))
                    get_item(fconfig[OLD_CONFIG_SECTION], item_data, True)

        for item_rec in CONFIG_ITEMS.values():
            if item_rec.section in fconfig:
                self.found_new_config = True
                if item_rec.name in fconfig[item_rec.section]:
                    log.debug('Config Section {} Item {} found in config file'.format(item_rec.section, item_rec.name))
                    get_item(fconfig[item_rec.section], item_rec, False)

        self.config_loaded = True
        log.info('Config Loaded!')

    def check_config(self):
        self.sanitize_config()

    def check_config(self):
        self.sanitize_config()

        for k, v in self.kwargs_overrides.items():
            self.config_data[k] = v

    def check_config(self):
        self.sanitize_config()

        for k, v in self.kwargs_overrides.items():
            self.config_data[k] = v

        if self.config_data['sslcertificate'] and self.config_data['sslprivatekey']:
            self.config_data['sslenabled'] = True

        if self.config_data['sslenabled']:
            self.config_data['urleditbase'] = "https://" + self.config_data['hostname']
        else:
            self.config_data['urleditbase'] = "http://" + self.config_data['hostname']

        if not self.config_data['sslenabled']:
            log.error("SSL Not Enabled, system will be insecure if auth is needed.")
            self.insecure_system = True
        if not self.config_data['urlsso']:
            log.error("SSO not configured, system will be insecure if auth is neecded.")
            self.insecure_system = True

        if not self.allow_insecure:
            log.error('INSECURE CONFIG DETECTED')
            raise InsecureConfig()
        else:
            log.info('OPERATING IN INSECURE MODE')

        if self.base_dir:
            log.debug('combining base path "{}"'.format(self.base_dir))
            for field in self.path_fields:
                if field in self.config_data:
                    tmp_fn = self.config_data[field] or ''
                else:
                    tmp_fn = getattr(self, field) or ''
                if tmp_fn:
                    tmp_fn = os.path.join(self.base_dir, tmp_fn)
                log.debug('with field "{}": {}'.format(field, tmp_fn))
                if field in self.config_data:
                    self.config_data[field] = tmp_fn
                else:
                    setattr(self, field, tmp_fn)

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
            log.debug('    Saving item: {}'.format(item_data.name))
            fconfig[item_data.section][item_data.name] = str(self.config_data[item_data.name])

        with open(self.filename, 'w') as configfile:
            fconfig.write(configfile)
        log.info('Config Saved')


    def __getattr__(self, item):
        if not self.config_loaded:
            self.load_config()
        if item not in self.config_data:
            log.error('Config item not found: '+item)
            raise AttributeError('Config section "' + item + '" not found.')
        return self.config_data[item]


config = Config()


