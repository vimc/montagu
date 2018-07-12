#!/usr/bin/env bash
set -e

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
if [ ! -f ~/.vault-token ]; then
    if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
        echo -n "Please provide your GitHub token for the vault: "
        read -s token
        echo ""
        export VAULT_AUTH_GITHUB_TOKEN=${token}
    fi
    env | grep -E '^(VAULT_ADDR|VAULT_AUTH_GITHUB_TOKEN)' > shared/vault_config
    echo "Authenticating with vault"
    vault login -method=github
fi

mkdir -p ~/.ssh/
vault read -field=value secret/vimc-robot/id_rsa.pub > ~/.ssh/id_rsa.pub
vault read -field=value secret/vimc-robot/id_rsa > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
