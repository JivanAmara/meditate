This docker (phusion/baseimage) configuration provides the following:

1. Migrates & on creation loads initial data to django database (`init/99_migrate_django_database.py`)
1. Starts django project in gunicorn (`service/gunicorn/run`)
1. Starts nginx to serve static files and proxy to gunicorn (`nginx/meditate.nginx`)
1. Makes deployment variations on the project's settings file. (`settings_deploy.py`)
