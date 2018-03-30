#!/opt/meditate/virtualenv/bin/python
# coding: utf-8

# --- Django setup
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meditate.settings_deploy")
django.setup()

# ---
from meditate.orders import send_alert, unprocessed_order_report

MAIL_USER = os.environ.get('MAIL_USER', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

r = unprocessed_order_report()
send_alert(r, user=MAIL_USER, password=MAIL_PASSWORD)
