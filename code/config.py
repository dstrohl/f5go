

import datetime
import configparser

"""
class UNSET():
    def __init__(self):
        self._unset_ = True

unset = UNSET()
"""
DEFAULT_CONFIG_FILE = 'go.cfg'
OLD_CONFIG_SECTION = 'goconfig'

DEFAULT_CONFIG = dict(
    GO = dict(
        allowSpecial = True,
        allowEdits = True,
    ),
    NETWORK = dict(        
        hostname = "localhost",
        port = 8080,
        sslEnabled = False,
        sslCertificate = '',
        sslPrivateKey = '',
    ),   
    USERS = dict(
        urlSSO = None,
        unknownUser = 'unknown',
        adminUser = 'admin',
        adminPassword = 'password',
    ),
    UI = dict(
        urlFavicon = "https://www.f5.com/favicon.ico",
        contactEmail = '',
        contactName = '',
        customDocs = '',
    ),
    DATABASE = dict(
        database_section = 'DATABASE',
        fnDatabase = "godb.json",
        saveOnChange = True,
        oldFnDatabase = 'godb.pickle',
        autoMigrate = True,
    ),
    MAXES = dict(
        max_last_x = 25,
        max_recent_days = 7,

    )
)

class Config():
    found_old_config = False
    filename = DEFAULT_CONFIG_FILE
    allowSpecial=True
    allowEdits=True
    hostname="localhost"
    port=8080
    sslEnabled=False
    sslCertificate=''
    sslPrivateKey=''
    urlSSO=None
    unknownUser='unknown'
    adminUser='admin'
    adminPassword='password'
    urlFavicon="https://www.f5.com/favicon.ico"
    contactEmail=''
    contactName=''
    customDocs=''
    database_section='DATABASE'
    fnDatabase="godb.json"
    saveOnChange=True
    oldFnDatabase='godb.pickle'
    autoMigrate=True
    max_last_x=25
    max_recent_days=7


    # TODO: I think the default dict load isn't quite right.


    def __init__(self, filename=DEFAULT_CONFIG_FILE, skip_load=False, overwrite_old=False, **kwargs):
        self.filename = filename
        if not skip_load:
            cfg = self.read_config()
        if kwargs:
            cfg.update(kwargs)

        self.load_config(kwargs)
        if self.found_old_config and overwrite_old:
            self.save_config()

    def load_config(self, cfg:dict):

        for s, i in DEFAULT_CONFIG.items():
            for k, d in i.items():
                v = self.get_config_val(cfg, s, k, d)
                setattr(self, k, v)

        if self.sslEnabled:
            self.urlEditBase = "https://" + self.hostname
        else:
            self.urlEditBase = "http://" + self.hostname

    def read_config(self):
        fconfig = configparser.ConfigParser()
        fconfig.read(self.filename)
        if OLD_CONFIG_SECTION in fconfig:
            self.found_old_config = True
        return fconfig

    def save_config(self):
        fconfig = configparser.ConfigParser()
        for section, sdata in DEFAULT_CONFIG.items():
            fconfig.add_section(section)
            for item in sdata:
                fconfig[section] = getattr(self, item)

        with open(self.filename, 'w') as configfile:
            fconfig.write(configfile)

    def get_config_val(self, cfg, section, name, default):
        def get_item(c, n, d):
            if isinstance(d, int):
                return c.getint(n)
            if isinstance(d, bool):
                return c.getboolean(n)
            return c[n]
        if section in cfg and name in cfg[section]:
            return get_item(cfg[section], name, default)
        name = 'cfg_'+name
        if OLD_CONFIG_SECTION in cfg and name in cfg[OLD_CONFIG_SECTION]:
            return get_item(cfg[OLD_CONFIG_SECTION], name, default)
        return default

config = Config(fconfig)
