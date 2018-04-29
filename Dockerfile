FROM python:3.6-slim

WORKDIR /home
COPY . .

RUN pip install -r requirements-dev.txt --quiet

RUN flake8
RUN coverage run -m nose
RUN coverage report

FROM python:3.6-slim
RUN apt-get update && apt-get install -y gcc

WORKDIR /home
COPY . .

RUN pip install -r requirements-prod.txt --quiet

ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:3000", "--uid", "www-data", "--module", "app.routes:app"]
