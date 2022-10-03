#!/usr/bin/env bash
vault login -method=github > /dev/null
vault read -field=password /secret/vimc/database/users/$1
