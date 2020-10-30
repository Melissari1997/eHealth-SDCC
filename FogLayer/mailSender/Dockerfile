FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /mailSender

COPY ./requirements.txt /mailSender/requirements.txt

RUN pip3 install --default-timeout=100 -r requirements.txt

COPY . /mailSender

CMD [ "gunicorn", "--config","gunicorn_config.py","mailSender:mailSender"]
