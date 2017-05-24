#!/usr/bin/env bash
export MONTAGU_API_VERSION=0f59cdb
export MONTAGU_DB_VERSION=d5ab6ad
export MONTAGU_CONTRIB_VERSION=28ace6c
docker-compose pull
docker-compose up \
    --project-name montagu \
    --abort-on-container-exit