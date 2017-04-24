#!/usr/bin/env bash
psql \
    -h localhost \
    -p 5432 \
    -U vimc \
    -d montagu \
    < test-data.sql