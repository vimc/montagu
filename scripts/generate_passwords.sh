#!/usr/bin/env bash
set -e

USERS="api import orderly readonly schema_migrator"
MACHINES="production science"

for M in $MACHINES; do
    for U in $USERS; do
        KEY="secret/database/$M/users/$U"
        # When closing out VIMC-587, uncomment the next line, delete
        # the following, and rerun the script
        # PW=$(pwgen -s -y 80 1)
        PW=$(vault read -field=password "secret/database/users/$U")
        echo "Setting password $KEY"
        vault write "$KEY" password="$PW"
    done
done
