#!/opt/meditate/virtualenv/bin/python3
# This script is for creating/migrating a sqlite3 database for the django project.
# If the database is created, it also loads initial data

import sys, os
import subprocess
from django.conf import settings

python_bin = '/opt/meditate/virtualenv/bin/python'
project_dir = '/opt/meditate/site/'

# If the database file doesn't exist, we'll need to create it.
db_filepath = settings.DATABASES['default']['NAME']
db_creation = not os.path.isfile(db_filepath)

print('migrating {}'.format(db_filepath))
rslt = subprocess.run([python_bin, 'manage.py', 'migrate'], cwd=project_dir)
exit_code = rslt.returncode
print('success') if exit_code == 0 else print('failure: {}'.format(exit_code))

if db_creation and exit_code == 0:
    fixture_file = 'fixtures/initial_data.json'
    print('loaddata {} -> {}'.format(fixture_file, db_filepath))
    rslt = subprocess.run([python_bin, 'manage.py', 'loaddata', fixture_file], cwd=project_dir)
    exit_code = rslt.returncode
    print('success') if exit_code == 0 else print('failure: {}'.format(exit_code))

sys.exit(exit_code)
