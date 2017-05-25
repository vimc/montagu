#!/usr/bin/env bash
./set-image-versions.sh

docker-compose pull
docker-compose -d up
docker-compose down