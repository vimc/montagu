#!/usr/bin/env bash
source ./set-image-versions.sh

docker run -ti \
    --network montagu_default \
    montagu.dide.ic.ac.uk:5000/montagu-cli:$MONTAGU_API_VERSION "$@"
