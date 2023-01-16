# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir -p securenoteapp/static/uploads

COPY . .

ENV FLASK_APP=securenoteapp
ENV FLASK_DEBUG=0

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--cert=adhoc" ]