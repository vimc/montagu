#!/usr/bin/env bash
set -e

mkdir -p scratch
docker build --tag montagu-deploy .
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $pwd/scratch:/app/scratch \
    --network=host \
    montagu-deploy