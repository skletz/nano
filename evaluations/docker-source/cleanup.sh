#!/usr/bin/env bash
# remove exited/not running containers, dangling images, etc.
docker system prune -f
# remove nano image
docker rmi -f nano
