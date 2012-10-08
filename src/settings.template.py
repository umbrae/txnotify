import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(PROJECT_ROOT, 'tmp')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

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

ACCOUNT_NAME = "Bank"     # You can change this to a nice label for emails.
ACCOUNT_NUMBER = ""       # The account number at your bank
ACCOUNT_TYPE = "CHECKING" # Either CHECKING or SAVINGS

# HUGE NOTE: This is obviously massively insecure on anything but the
# most secure of boxes. Please ensure that file permissions are set properly
# and that this is on a machine that you trust completely.
# 
# ANYONE WHO SEES THIS FILE HAS FULL ACCESS TO YOUR ONLINE BANK.
# 
ACCOUNT_USERNAME = "" # The username at your bank for online banking
ACCOUNT_PASSWORD = "" # The password at your bank for online banking

# You can sign up for a free mailgun account at mailgun.net to use here, or
# use some other SMTP host you're already familiar with.
SMTP_HOST = 'smtp.mailgun.org'
SMTP_PORT = 587
SMTP_USERNAME = ''
SMTP_PASSWORD = ''
FROM_EMAIL = ''

# Where you want the transaction notifications to be sent
EMAIL_TO = ''
EMAIL_CC = None
