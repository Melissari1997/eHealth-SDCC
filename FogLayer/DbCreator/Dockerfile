FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /creator

COPY ./requirements.txt /creator/requirements.txt

RUN pip3 install --default-timeout=100 -r requirements.txt
COPY . /creator

ENTRYPOINT [ "python3" , "-u"]

CMD [ "creator.py" ]
