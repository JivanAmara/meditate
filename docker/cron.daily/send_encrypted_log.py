#!/opt/meditate/virtualenv/bin/python

import os
import subprocess
from meditate.orders import send_alert

MAIL_USER = os.environ.get('MAIL_USER', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

gunicorn_log := subprocess.check_output(['cat /var/log/gunicorn_meditate.log | gpg -a -e -r 0x05B29E8D'])
nginx_log := subprocess.check_output(['cat /var/log/nginx/error.log | gpg -a -e -r 0x05B29E8D'])

send_alert(gunicorn_log, user=MAIL_USER, password=MAIL_PASSWORD)
send_alert(nginx_log, user=MAIL_USER, password=MAIL_PASSWORD)
