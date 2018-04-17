from meditate.settings import *

DEBUG=False

DATABASES['default']['NAME'] = '/opt/meditate/database/db.sqlite3'

STATIC_ROOT = '/opt/meditate/static/'
MEDIA_ROOT = '/opt/meditate/downloadable/'
VALID_DOWNLOAD_PERIOD = timedelta(days=7)

STATIC_GROUP = 'www-data'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']
ALLOW_HOST = os.environ.get('DJANGO_ALLOW_HOST', None)

if ALLOW_HOST is not None:
    ALLOWED_HOSTS.append(ALLOW_HOST)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', None)
