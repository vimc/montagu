#!/usr/bin/env bash
set -ex

PROXY_CONTAINER=montagu_proxy_1
ORDERLY_CONTAINER=orderly_web_orderly

ORDERLY_REPORT_2020=paper-first-public-app
ORDERLY_REPORT_2021=paper-second-public-app

ORDERLY_ID_2020=20210209-161556-ff9e2511
ORDERLY_ID_2021=20210209-161000-2e926cad

ORDERLY_PATH_2020="/orderly/archive/$ORDERLY_REPORT_2020/$ORDERLY_ID_2020"
ORDERLY_PATH_2021="/orderly/archive/$ORDERLY_REPORT_2021/$ORDERLY_ID_2021"
WWW_ROOT=/usr/share/nginx/html

docker exec -it $PROXY_CONTAINER mkdir -p $WWW_ROOT/2020/visualisation
docker exec -it $PROXY_CONTAINER mkdir -p $WWW_ROOT/2021/visualisation

mkdir -p 2020/visualisation
mkdir -p 2021/visualisation

docker cp $ORDERLY_CONTAINER:$ORDERLY_PATH_2020/. 2020/visualisation
docker cp $ORDERLY_CONTAINER:$ORDERLY_PATH_2021/. 2021/visualisation


docker cp 2020/visualisation/. $PROXY_CONTAINER:$WWW_ROOT/2020/visualisation
docker cp 2021/visualisation/. $PROXY_CONTAINER:$WWW_ROOT/2021/visualisation
