#!/usr/bin/env bash
set -ex

vault_zip=vault_0.7.3_linux_amd64.zip
wget https://releases.hashicorp.com/vault/0.7.3/$vault_zip
unzip $vault_zip
chmod 744 vault
cp vault /usr/bin/vault