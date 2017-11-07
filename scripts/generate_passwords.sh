#!/usr/bin/env bash
set -e

USERS="api import orderly readonly schema_migrator"
MACHINES="production science"

for M in $MACHINES; do
    for U in $USERS; do
        KEY="secret/database/$M/users/$U"
        echo "Setting password $KEY"
        echo vault write "$KEY" password=$(pwgen -n1 80)
    done
done
