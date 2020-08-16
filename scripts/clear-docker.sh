#!/usr/bin/env bash
docker kill $(docker ps -aq)
docker rm $(docker ps -aq)
docker network prune --force
docker volume prune --force
exit 0