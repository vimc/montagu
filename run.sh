#!/usr/bin/env bash
export MONTAGU_API_VERSION=master
export MONTAGU_DB_VERSION=master
export MONTAGU_CONTRIB_VERSION=master
docker-compose pull
docker-compose up \
    --project-name montagu \
    --abort-on-container-exit