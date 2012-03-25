import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(PROJECT_ROOT, 'tmp')

# Doesn't do anything just yet.
DEBUG = True

# OFX is the protocol used to talk to your bank and get transaction
# information. To get the settings, visit:
# http://wiki.gnucash.org/wiki/OFX_Direct_Connect_Bank_Settings
OFX_SETTINGS = {
    "url": "",
    "fid": "",
    "org": "",
    "code": ""
}

ACCOUNT_NUMBER = ""       # The account number at your bank
ACCOUNT_TYPE = "CHECKING" # Either CHECKING or SAVINGS

# HUGE NOTE: This is obviously massively insecure on anything but the
# most secure of boxes. Please ensure that file permissions are set properly
# and that this is on a machine that you trust completely.
# 
# As a good test: Would you run install Quicken with passwordless access on
# this machine?
ACCOUNT_USERNAME = "" # The username at your bank for online banking
ACCOUNT_PASSWORD = "" # The password at your bank for online banking

# Sign up for a free mailgun account at mailgun.net
MAILGUN_SMTP_USERNAME = ''
MAILGUN_SMTP_PASSWORD = ''
MAILGUN_FROM_EMAIL = ''

# Where you want the transaction notifications to be sent
EMAIL_TO = ''