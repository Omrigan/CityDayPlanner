FROM tiangolo/uwsgi-nginx-flask:python3.7
#COPY . /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt