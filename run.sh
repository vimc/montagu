#!/usr/bin/env bash
source ./set-image-versions.sh

docker-compose pull

docker-compose \
    --project-name montagu \
    up \
    --abort-on-container-exit