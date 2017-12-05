#!/usr/bin/env bash
set -ex

NAME=$1
if [ ! "$#" -eq 1 ]; then
    echo "Expected one argument"
    exit 1
fi

if [ ! -f /vagrant/vault_config ]; then
    echo "Run restore-prepare.sh on host"
    exit 1
fi

MONTAGU_PATH=~/montagu

MONTAGU_SETTINGS="/vagrant/restore/$NAME/montagu-deploy.json"
MONTAGU_VERSION="/vagrant/restore/$NAME/version"

if [ ! -f $MONTAGU_SETTINGS ]; then
    echo "Settings not found at $MONTAGU_SETTINGS"
    exit 1
fi

if [ ! -f $MONTAGU_VERSION ]; then
    echo "Version not found at $MONTAGU_VERSION"
    exit 1
fi

MONTAGU_VERSION_STRING=$(cat $MONTAGU_VERSION)

. /vagrant/vault_config
export VAULT_ADDR VAULT_AUTH_GITHUB_TOKEN

vault auth -method=github
vault read -field=password /secret/registry/vimc | \
    docker login -u vimc --password-stdin docker.montagu.dide.ic.ac.uk:5000
vault read -field=password /secret/registry/vimc | \
    sudo -H docker login -u vimc --password-stdin docker.montagu.dide.ic.ac.uk:5000

if [ -f $MONTAGU_PATH ]; then
    (cd $MONTAGU_PATH && ./src/stop.py)
    rm -rf $MONTAGU_PATH
fi

git clone --recursive https://github.com/vimc/montagu $MONTAGU_PATH
git -C $MONTAGU_PATH checkout $MONTAGU_VERSION_STRING

cp $MONTAGU_SETTINGS $MONTAGU_PATH/src/montagu-deploy.json

sudo mkdir -p /etc/montagu/backup
pip3 install --user -r $MONTAGU_PATH/src/requirements.txt

(cd $MONTAGU_PATH && sudo -E ./src/deploy.py)
