FROM tiangolo/uwsgi-nginx:python3.7

LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"


ENV NGINX_MAX_UPLOAD 0
ENV LISTEN_PORT 80
ENV UWSGI_INI /app/uwsgi.ini
ENV STATIC_URL /static
ENV STATIC_PATH /app/static
ENV STATIC_INDEX 0

# Make /app/* available to be imported by Python globally to better support several use cases like Alembic migrations.
ENV PYTHONPATH=/app

COPY start.sh /start.sh
RUN chmod +x /start.sh
#
#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh
#
#ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]

RUN apt-get update
RUN apt-get install -y python3-numpy

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
