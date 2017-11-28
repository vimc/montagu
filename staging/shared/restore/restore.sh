#!/usr/bin/env bash
set -ex
if [ ! -f /vagrant/vault_config ]; then
    echo "Run restore-prepare.sh on host"
    exit 1
fi
. /vagrant/vault_config

vault auth -method=github
vault read -field=password /secret/registry/vimc | \
    docker login -u vimc --password-stdin docker.montagu.dide.ic.ac.uk:5000
vault read -field=password /secret/registry/vimc | \
    sudo -H docker login -u vimc --password-stdin docker.montagu.dide.ic.ac.uk:5000

MONTAGU_PATH=/montagu

if [ -f $MONTAGU_PATH ]; then
    (cd $MONTAGU_PATH && ./src/stop.py)
    rm -rf $MONTAGU_PATH
fi

git clone --recursive https://github.com/vimc/montagu $MONTAGU_PATH
git -C $MONTAGU_PATH checkout i1067
git -C $MONTAGU_PATH submodule update

cp /vagrant/restore-settings.json $MONTAGU_PATH/src/montagu-deploy.json

sudo mkdir -p /etc/montagu/backup
pip3 install --user -r $MONTAGU_PATH/src/requirements.txt

(cd $MONTAGU_PATH && sudo -E ./src/deploy.py)
