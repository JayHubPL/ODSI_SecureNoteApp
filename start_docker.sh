#!/bin/sh

docker build --tag securenoteapp .
docker run --rm -p 443:443 --name securenoteapp securenoteapp
