FROM python:2.7-slim

WORKDIR /sdk
COPY . /sdk

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["pytest"]
