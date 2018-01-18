FROM postgres:9.6-alpine
RUN apk add --update python py-pip

RUN pip install requests


COPY ./main.py /main.py

RUN chmod 777 /main.py

ADD ./init.sql /docker-entrypoint-initdb.d/ 
RUN chmod 644 /docker-entrypoint-initdb.d/*

CMD python /main.py
