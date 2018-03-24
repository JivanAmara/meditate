FROM phusion/baseimage

# --- Get necessary system packages & set up directories
RUN apt-get update
RUN apt-get install -y python3 nginx virtualenv
RUN rm /etc/nginx/sites-enabled/default
RUN mkdir -p /opt/meditate/site
RUN mkdir -p /opt/meditate/static
RUN touch /var/log/gunicorn_meditate.log
RUN chmod a+rw /var/log/gunicorn_meditate.log

# --- Set up python code
RUN virtualenv -p python3 /opt/meditate/virtualenv
# Problem w/ pip==9.0.2
RUN /opt/meditate/virtualenv/bin/pip install pip==9.0.1
RUN /opt/meditate/virtualenv/bin/pip install gunicorn
COPY . /opt/meditate/site
WORKDIR /opt/meditate/site
RUN /opt/meditate/virtualenv/bin/pip3 install -r requirements.txt
RUN STRIPE_SECRET_KEY=not_really STRIPE_PUBLIC_KEY=not_really /opt/meditate/virtualenv/bin/python3 manage.py collectstatic
RUN STRIPE_SECRET_KEY=not_really STRIPE_PUBLIC_KEY=not_really /opt/meditate/virtualenv/bin/python3 manage.py migrate
RUN STRIPE_SECRET_KEY=not_really STRIPE_PUBLIC_KEY=not_really /opt/meditate/virtualenv/bin/python3 manage.py loaddata fixtures/initial_data.json

# --- Prepare services to start on container start
RUN cp docker/nginx/meditate.nginx /etc/nginx/sites-enabled/
RUN cp -r docker/service/* /etc/service/

# --- Run With:
# docker run --name <> -e DJANGO_SECRET_KEY=<> -e STRIPE_SECRET_KEY=<> -e STRIPE_PUBLIC_KEY=<> -e PAYPAL_MODE=<sandbox|production> -p <host_port>:80 -v </host/path/to/db/dir/>:/opt/meditate/database/ <image>
