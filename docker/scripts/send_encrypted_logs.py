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

encrypt_django_log = 'cat /var/log/meditate.log | gpg -a -e --always-trust -r 0x05B29E8D'
encrypt_gunicorn_log = 'cat /var/log/gunicorn_meditate.log | gpg -a -e --always-trust -r 0x05B29E8D'
encrypt_nginx_error_log = 'cat /var/log/nginx/error.log | gpg -a -e --always-trust -r 0x05B29E8D'
encrypt_nginx_access_log = 'cat /var/log/nginx/access.log | gpg -a -e --always-trust -r 0x05B29E8D'

django_log = subprocess.check_output(['/bin/bash', '-c', encrypt_django_log]).decode('utf-8')
gunicorn_log = subprocess.check_output(['/bin/bash', '-c', encrypt_gunicorn_log]).decode('utf-8')
nginx_error_log = subprocess.check_output(['/bin/bash', '-c', encrypt_nginx_error_log]).decode('utf-8')
nginx_access_log = subprocess.check_output(['/bin/bash', '-c', encrypt_nginx_access_log]).decode('utf-8')

send_alert(django_log, subject='Django Log', user=MAIL_USER, password=MAIL_PASSWORD)
send_alert(gunicorn_log, subject='Gunicorn Log', user=MAIL_USER, password=MAIL_PASSWORD)
send_alert(nginx_error_log, subject='Nginx Error Log', user=MAIL_USER, password=MAIL_PASSWORD)
send_alert(nginx_access_log, subject='Nginx Access Log', user=MAIL_USER, password=MAIL_PASSWORD)
