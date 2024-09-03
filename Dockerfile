FROM python:2.7-slim

WORKDIR /sdk
COPY . /sdk

RUN pip install --upgrade pip \
    && pip install pytest -r requirements.txt

CMD ["pytest"]
