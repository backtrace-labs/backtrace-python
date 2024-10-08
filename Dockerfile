FROM python:2.7-slim

WORKDIR /sdk
COPY ./requirements.txt /sdk

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /sdk
ENV PYTHONPATH=/sdk

CMD ["pytest"]
