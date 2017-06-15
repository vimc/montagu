#!/bin/sh

set -ex

REGISTRY_HOST=docker.montagu.dide.ic.ac.uk:5000
CERT_DEST=/etc/docker/certs.d/$REGISTRY_HOST
CERT_SRC=https://raw.githubusercontent.com/vimc/montagu-ci/master/registry/certs/domain.crt

curl -L $CERT_SRC > registry.crt
mkdir -p $CERT_DEST
mv registry.crt $CERT_DEST/domain.crt