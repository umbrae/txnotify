import settings
import sys
import shelve
import os

from cStringIO import StringIO
from datetime import datetime
from email.mime.text import MIMEText
from smtplib import SMTP

# Import fixofx, uses some trickery to put itself in the path.
# For more info see: https://github.com/wesabe/fixofx
sys.path.insert(0, os.path.join(settings.SRC_DIR, 'fixofx', '3rdparty'))
sys.path.insert(0, os.path.join(settings.SRC_DIR, 'fixofx', 'lib'))
import ofx

def dbg(s):
    if settings.DEBUG:
        print(s)

"""
 The cache is used to store the last transaction from the last time
 this script ran. We store it so we don't email duplicate information.
"""
cache = shelve.open(os.path.join(settings.TMP_DIR, 'txnotify.cache'))


def parse_line_item(line_item):
    """ Given an OFX line item, transform it into a friendlier dict of the
        data we need.

    """
    date_posted_str = line_item.get('DTPOSTED', '')
    try:
       date_posted = datetime.strptime(date_posted_str, "%Y%m%d%H%M%S.000")
    except ValueError:
       date_posted = datetime.strptime(date_posted_str, "%Y%m%d%H%M%S")
    return {
        "name": line_item.get('NAME'),
        "date_posted": date_posted,
        "transaction_type": line_item.get('TRNTYPE'),
        "amount": line_item.get('TRNAMT'),
        "check_number": line_item.get('CHECKNUM'),
        "id": line_item.get('FITID')
    }

def generate_email_body(line_items):
    """ Given a list of line items from OFX, parse the ones that have occurred
        since the last time we ran and generate an email body of the form:

        [YYYY-MM-DD] {Transaction-name-32-chr-spaced} {Amount}
        [YYYY-MM-DD] {Transaction-name-32-chr-spaced} {Amount}
        [YYYY-MM-DD] {Transaction-name-32-chr-spaced} {Amount}

    """
    email_body = StringIO()
    last_transaction_id = cache.get('last_transaction_id')

    first = True
    for line_item in line_items:
        line_item_dict = line_item.asDict()
        if line_item_dict.has_key('NAME'):
            item = parse_line_item(line_item_dict)

            if first:
                cache['last_transaction_id'] = item['id']
                cache.sync()
                first = False

            if item['id'] == last_transaction_id:
                dbg("Item matched last transaction ID. Breaking.")
                break

            email_body.write("[%s] %s %s\n" % (
                item['date_posted'].date().isoformat(),
                item['name'].ljust(32),
                item['amount']
            ))
        else:
            dbg("Skipping line item row: %s" % line_item)

    return email_body.getvalue()


def send_email(subject, body):
    if len(body) > 0:
        dbg("Sending email with email_body: %s" % body)

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = settings.EMAIL_TO
        if settings.EMAIL_CC is not None:
            msg['Cc'] = ', '.join(settings.EMAIL_CC)


        smtp = SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.sendmail(settings.FROM_EMAIL,
                      [settings.EMAIL_TO],
                      msg.as_string())
    else:
        dbg("Body was empty, no valid, new records found. Not emailing.")

def main():
    # Set up our OFX client
    institution = ofx.Institution(ofx_org=settings.OFX_SETTINGS['org'],
                                  ofx_url=settings.OFX_SETTINGS['url'],
                                  ofx_fid=settings.OFX_SETTINGS['fid'])
    account = ofx.Account(acct_type=settings.ACCOUNT_TYPE, 
                          acct_number=settings.ACCOUNT_NUMBER,
                          aba_number=settings.OFX_SETTINGS['code'], 
                          institution=institution)
    client = ofx.Client(debug=settings.DEBUG)

    # Get our current statement
    response = client.get_statement(account,
                                    settings.ACCOUNT_USERNAME,
                                    settings.ACCOUNT_PASSWORD)

    # This ugly bit of navigation gets us the list of the transactions that
    # have occured in this statement.
    statement_dict = response.get_statements()[0].as_dict()
    try:
        line_items = statement_dict['STMTRS']['BANKTRANLIST']
    except KeyError:
        line_items = statement_dict['CCSTMTRS']['BANKTRANLIST']

    email_body = generate_email_body(line_items)

    now = datetime.now().strftime('%Y-%m-%d %I:%M%p')
    subject = "[%s] New %s Transactions" % (now, settings.ACCOUNT_NAME)

    send_email(subject, email_body)

if __name__ == "__main__":
    main()

