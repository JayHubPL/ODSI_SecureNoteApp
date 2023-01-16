#!/bin/sh

docker build --tag securenoteapp .
docker run --rm -p 443:5000 --name securenoteapp securenoteapp
