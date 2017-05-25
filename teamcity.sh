#!/usr/bin/env bash
set -e

source ./set-image-versions.sh
docker-compose pull
docker-compose -d up
docker-compose down