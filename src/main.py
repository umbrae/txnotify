import settings
import sys
import shelve
import os
from datetime import datetime

from smtplib import SMTP
from email.mime.text import MIMEText

from cStringIO import StringIO

from dateutil.parser import parse as dup

sys.path.insert(0, 'fixofx/3rdparty')
sys.path.insert(0, 'fixofx/lib')

import ofx

cache = shelve.open(os.path.join(settings.TMP_DIR, 'txnotify.cache'))
def get_last_transaction_id():
    return cache.get('last_transaction_id')

def set_last_transaction_id(transaction_id):
    cache['last_transaction_id'] = transaction_id
    cache.sync()

def parse_line_item(line_item):
    date_posted = dup(line_item.get('DTPOSTED', '').replace('.000', ''))
    return {
        "name": line_item.get('NAME'),
        "date_posted": date_posted,
        "transaction_type": line_item.get('TRNTYPE'),
        "amount": line_item.get('TRNAMT'),
        "check_number": line_item.get('CHECKNUM'),
        "id": line_item.get('FITID')
    }

institution = ofx.Institution(ofx_org=settings.OFX_SETTINGS['org'],
                              ofx_url=settings.OFX_SETTINGS['url'],
                              ofx_fid=settings.OFX_SETTINGS['fid'])

account = ofx.Account(acct_type=settings.ACCOUNT_TYPE, 
                      acct_number=settings.ACCOUNT_NUMBER,
                      aba_number=settings.OFX_SETTINGS['code'], 
                      institution=institution)

client = ofx.Client(debug=settings.DEBUG)

last_transaction_id = get_last_transaction_id()
if not last_transaction_id:
    print "Last_transaction_id was null."

response = client.get_statement(account, settings.ACCOUNT_USERNAME, settings.ACCOUNT_PASSWORD)

line_items = response.get_statements()[0].as_dict()['STMTRS']['BANKTRANLIST']

email_body = StringIO()

first = True
for line_item in line_items:
    line_item_dict = line_item.asDict()
    if line_item_dict.has_key('NAME'):
        item = parse_line_item(line_item_dict)
        
        if first:
            set_last_transaction_id(item['id'])
            first = False

        if item['id'] == last_transaction_id:
            print "Item matched last transaction ID. Breaking."
            break
            
        email_body.write("[%s] %s %s\n" % (
            item['date_posted'].date().isoformat(),
            item['name'].ljust(20),
            item['amount']
        ))

    else:
        print "Skipping line item row: %s" % line_item

now = datetime.now().strftime('%Y-%m-%d %I:%M%p')
subject = "[%s] New Bank Transactions" % now
body = email_body.getvalue()

if len(body) > 0:
    print "Sending email with body: %s" % body

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.MAILGUN_FROM_EMAIL
    msg['To'] = settings.EMAIL_TO
    
    smtp = SMTP("smtp.mailgun.org", 587)
    smtp.login(settings.MAILGUN_SMTP_USERNAME, settings.MAILGUN_SMTP_PASSWORD)
    smtp.sendmail(settings.MAILGUN_API_EMAIL,
                  [settings.EMAIL_TO],
                  msg.as_string())
else:
    print "No records found, skipping sending email."
