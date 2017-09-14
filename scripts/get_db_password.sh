#!/usr/bin/env bash
vault auth -method=github > /dev/null
vault read -field=password /secret/database/users/$1
