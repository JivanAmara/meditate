from meditate.settings import *

DEBUG=False

DATABASES['default']['NAME'] = '/opt/meditate/database/db.sqlite3'

STATIC_ROOT = '/opt/meditate/static/'
MEDIA_ROOT = '/opt/meditate/downloadable/'
VALID_DOWNLOAD_PERIOD = timedelta(days=7)

STATIC_GROUP = 'www-data'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']
ALLOW_HOST = os.environ.get('DJANGO_ALLOW_HOST', None)
ALLOW_HOST_IP = os.environ.get('DJANGO_ALLOW_HOST_IP', None)

if ALLOW_HOST is not None:
    ALLOWED_HOSTS.append(ALLOW_HOST)

if ALLOW_HOST_IP is not None:
    ALLOWED_HOSTS.append(ALLOW_HOST_IP)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', None)

LOGGING['handlers']['file']['level'] = 'DEBUG'
LOGGING['handlers']['file']['filename'] = '/var/log/meditate.log'
