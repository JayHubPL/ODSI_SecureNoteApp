# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /securenoteapp

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=securenoteapp
ENV FLASK_DEBUG=1

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=443", "--cert=adhoc" ]