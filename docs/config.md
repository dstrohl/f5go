## [GO]
constants to be used within go.py
the below items can be un-commented to change the defaults

### allow regex (special) looks
allow Special: true

### Allow users to edit links
allowEdits: true

log_file = 'go.log',
log_level = 'info',
log_file_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
default_replacement_error_string = '',
default_replacement_error_handling = 'ERROR',
autoSaveConfig = True,    


## [NETWORK]
### FQDN where go.py will run
hostname: localhost

### Port to use for the web service
port: 8080

### (optional) Use SSL?  If enabled this will make cfg_sslCertificate and cfg_sslPrivateKey required
sslEnabled: false

### The path to the SSL certificate
sslCertificate: go.crt

### The path to the SSL private key
sslPrivateKey: go.key

## [USERS]
(optional) Auth URL for redirecting users when editing links
urlSSO: None

Username to use when no SSO is configured
unknownUser: Unknown

Admin users (comma seperated list of usernames)
adminUsers: admin

Admin passwords (IF SSO is not used, these are the passwords for the admins)
if sso IS used, users with these userid's will be be considered admins.
adminPasswordsClear: password

This will contain the hashed values of the admin passwords.
if this is empty AND the adminPasswordsClear is full, the config will hash the passwords and write them to the file.
if both password fields are blank, admin will only work via sso.
adminPasswords:

## [UI]
F5's favicon for use in client browsers
urlFavicon: https://www.f5.com/favicon.ico

The email address of a person to contact if there is a question/problem/etc. which will show up at the bottom of pages if set.
contactEmail: None

The name of a person to contact if there is a question/problem/etc. which will show up at the bottom of pages if set.
contactName: None

A URL to internal documentation written for your Go redirector instance which will show up at the bottom of pages if set
customDocs: None

## [DATABASE]
The name of the saved data file
fnDatabase: godb.json

Should we save the data file when a record is changed (not including read counts)
saveOnChange: true

The name of the old serialized data file (for migration)
fnDatabase: godb.pickle

Auto migrate on empty database and presence of pickle file
autoMigrate: true

## [MAXES]
The number of last x links to track
def_max_last_x = 25

the number of days for recent uses
def_max_recent_days = 7


# OLD CONFIG

The old approach still works, but the new approach (above) is simpler
## [goconfig]

The name of the serialized data file
cfg_fnDatabase: godb.pickle

F5's favicon for use in client browsers
cfg_urlFavicon: https://www.f5.com/favicon.ico

FQDN where go.py will run
cfg_hostname: localhost

Port to use for the web service
cfg_port: 8080

(optional) Auth URL for redirecting users when editing links
cfg_urlSSO: None

(optional) Use SSL?  If enabled this will make cfg_sslCertificate and cfg_sslPrivateKey required
cfg_sslEnabled: false

The path to the SSL certificate
cfg_sslCertificate: go.crt

The path to the SSL private key
cfg_sslPrivateKey: go.key

The email address of a person to contact if there is a question/problem/etc. which will show up at the bottom of pages if set.
cfg_contactEmail: None

The name of a person to contact if there is a question/problem/etc. which will show up at the bottom of pages if set.
cfg_contactName: None

A URL to internal documentation written for your Go redirector instance which will show up at the bottom of pages if set
cfg_customDocs: None
