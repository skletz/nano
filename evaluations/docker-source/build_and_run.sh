#!/usr/bin/env bash
# remove nano image and container
docker rmi -f nano
# build image
docker build --tag=nano . --rm
# run container (map external port 4000 to internal port 80)
docker run --rm -p 4000:80 nano
