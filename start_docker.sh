#!/bin/sh

docker build --tag securenoteapp .
docker run --rm -p 5000:5000 --name securenoteapp securenoteapp
