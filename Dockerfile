FROM phusion/baseimage

# --- Get necessary system packages & set up directories
RUN apt-get update
RUN apt-get install -y python3 nginx virtualenv gnupg
RUN rm /etc/nginx/sites-enabled/default
RUN mkdir -p /opt/meditate/site
RUN mkdir -p /opt/meditate/database
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
COPY docker/settings_deploy.py /opt/meditate/site/meditate
ENV PYTHONPATH=/opt/meditate/site
ENV DJANGO_SETTINGS_MODULE=meditate.settings_deploy
ENV DJANGO_SECRET_KEY=JustForDockerBuild
RUN /opt/meditate/virtualenv/bin/pip3 install -r requirements.txt
RUN /opt/meditate/virtualenv/bin/python3 manage.py collectstatic

# --- Prepare initialization scripts to run & services to start on container start
RUN gpg --import docker/pubkey.gpg.ascii
RUN cp docker/cron.daily/* /etc/cron.daily/
RUN cp docker/nginx/meditate.nginx /etc/nginx/sites-enabled/
RUN cp docker/init/* /etc/my_init.d/
RUN cp -r docker/service/* /etc/service/

# --- Run With:
# docker run --name <> -e DJANGO_ALLOW_HOST=<> -e DJANGO_SECRET_KEY=<> -e STRIPE_SECRET_KEY=<> -e STRIPE_PUBLIC_KEY=<> -e PAYPAL_MODE=<sandbox|production> -e MAIL_USER=<> -e MAIL_PASSWORD=<> -p <host_port>:80 -v </host/path/to/db/dir/>:/opt/meditate/database/ <image>
