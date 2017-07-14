#!/usr/bin/env bash
set -e

apt-get install gdebi -y
wget https://updates.duplicati.com/experimental/duplicati_2.0.1.61-1_all.deb -O duplicati_2.0.1.61-1_all.deb
gdebi --non-interactive duplicati_2.0.1.61-1_all.deb

apt-get install python3-pip
pip3 install -r requirements.txt

echo -n "Please provide your GitHub personal access token for the vault: "
read -s token
echo ""

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
export VAULT_AUTH_GITHUB_TOKEN=${token}
vault auth -method=github

./setup.py