FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN apt-get update
RUN apt-get install -y python3-numpy

ADD ../requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY .. /app
