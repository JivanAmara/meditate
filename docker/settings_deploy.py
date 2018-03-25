from meditate.settings import *

DATABASES['default']['NAME'] = '/opt/meditate/database/db.sqlite3'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']
ALLOW_HOST = os.environ.get('DJANGO_ALLOW_HOST', None)
if ALLOW_HOST is not None:
    ALLOWED_HOSTS.append(ALLOW_HOST)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', None)
