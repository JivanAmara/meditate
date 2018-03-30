#!/opt/meditate/virtualenv/bin/python

# --- Django setup
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meditate.settings_deploy")
django.setup()

# ---
import subprocess
from meditate.orders import send_alert

MAIL_USER = os.environ.get('MAIL_USER', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

encrypt_gunicorn_log = 'cat /var/log/gunicorn_meditate.log | gpg -a -e --default-recipient 0x05B29E8D'
encrypt_nginx_log = 'cat /var/log/nginx/error.log | gpg -a -e --default-recipient 0x05B29E8D'
gunicorn_log = subprocess.check_output(['/bin/bash', '-c', encrypt_gunicorn_log]).decode('utf-8')
nginx_log = subprocess.check_output(['/bin/bash', '-c', encrypt_nginx_log]).decode('utf-8')

send_alert(gunicorn_log, subject='Gunicorn Log', user=MAIL_USER, password=MAIL_PASSWORD)
send_alert(nginx_log, subject='Nginx Log', user=MAIL_USER, password=MAIL_PASSWORD)
