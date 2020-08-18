#!/usr/bin/env bash
set -ex

PROXY_CONTAINER=montagu_proxy_1
ORDERLY_CONTAINER=orderly_web_orderly
ORDERLY_REPORT=paper-first-public-app
ORDERLY_ID=20200115-105913-be6fcf5b

ORDERLY_PATH="/orderly/archive/$ORDERLY_REPORT/$ORDERLY_ID"
WWW_ROOT=/usr/share/nginx/html

docker exec -it $PROXY_CONTAINER mkdir -p $WWW_ROOT/visualisation

mkdir -p visualisation
docker cp $ORDERLY_CONTAINER:$ORDERLY_PATH visualisation/2020
docker cp visualisation/2020 $PROXY_CONTAINER:$WWW_ROOT/2020/visualisation
