FROM python:2.7-alpine3.7

RUN apk add --update postgresql-dev build-base

COPY ./app /app
COPY ./server.py /
COPY ./test.py /
COPY ./requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

CMD python /server.py
