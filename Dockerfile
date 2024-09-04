FROM python:2.7-slim

WORKDIR /sdk
COPY ./requirements.txt /sdk

RUN pip install --upgrade pip \
    && pip install pytest -r requirements.txt

COPY . /sdk

CMD ["PYTHONPATH=/sdk " "pytest"]
