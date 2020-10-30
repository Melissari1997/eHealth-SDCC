FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /healthChecker

COPY ./requirements.txt /healthChecker/requirements.txt

RUN pip3 install --default-timeout=100 -r requirements.txt
COPY . /healthChecker


CMD [ "gunicorn", "--config","gunicorn_config.py","healthChecker:healthChecker"]
