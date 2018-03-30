#!/opt/meditate/virtualenv/bin/python

import os
from meditate.orders import send_alert

MAIL_USER = os.environ.get('MAIL_USER', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

r := unprocessed_order_report()
send_alert(r, user=MAIL_USER, password=MAIL_PASSWORD)
