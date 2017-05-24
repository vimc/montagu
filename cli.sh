#!/usr/bin/env bash
docker run -ti \
    --network montagu_default \
    montagu.dide.ic.ac.uk:5000/montagu-cli:0f59cdb "$@"
