#!/usr/bin/env bash
set -ex
SCRIPT=$0
MONTAGU_PATH=$(git -C $(dirname $SCRIPT) rev-parse --show-toplevel)

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
    vault auth -method=github
fi

SSH_PATH=`mktemp -d`
SSH_KEY="$SSH_PATH/id_rsa"

function cleanup {
    rm -rf $SSH_PATH
}
trap cleanup EXIT

vault read -field=value secret/vimc-robot/id_rsa > $SSH_KEY

export GIT_SSH_COMMAND="ssh -i $SSH_KEY"
git -C $MONTAGU_PATH push $*
