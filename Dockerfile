FROM python:2.7-slim

WORKDIR /sdk
COPY ./requirements.txt /sdk

RUN pip install --upgrade pip \
    && pip install  $(grep -ivE "black" requirements.txt) 
# black is not available in python2.7 container

COPY . /sdk
ENV PYTHONPATH=/sdk

CMD ["pytest"]
