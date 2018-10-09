#!/usr/bin/env bash

apt-get install unattended-upgrades curl

echo '
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
' >/etc/apt/apt.conf.d/20auto-upgrades

sed -i.bak 's|//Unattended-Upgrade::Remove-Unused-Dependencies "false"|Unattended-Upgrade::Remove-Unused-Dependencies "true"|' /etc/apt/apt.conf.d/50unattended-upgrades

sed -i.bak 's|//Unattended-Upgrade::Automatic-Reboot "false"|Unattended-Upgrade::Automatic-Reboot "false"|' /etc/apt/apt.conf.d/50unattended-upgrades

rm /etc/apt/apt.conf.d/50unattended-upgrades.bak

echo '
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Verbose 2;
APT::Periodic::RandomSleep 1;
'> /etc/apt/apt.conf.d/10periodic

export VAULT_ADDR=https://support.montagu.dide.ic.ac.uk:8200
if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo -n "Please provide your GitHub personal access token for the vault: "
    read -s token
    echo ""
    export VAULT_AUTH_GITHUB_TOKEN=${token}
fi
vault login -method=github
SLACK_WEBHOOK=$(vault read -field=password secret/slack/autoupdate-webhook)

echo '#!/bin/sh

if [ -f /var/run/reboot-required ]; then

  hostname=$(uname -n)
  if [ $hostname = "fi--didevimc01" ]; then
    hostname="production"
  elif [ $hostname = "fi--didevimc02" ]; then
    hostname="support"
  elif [ $hostname = "wpia-didess1" ]; then
    hostname="annex"
  fi

  curl -X POST -H '"'"'Content-type: application/json'"'"' -d "{ \"text\":\"A reboot is required on "${hostname}".montagu.dide.ic.ac.uk following automatic updates.\"}" https://hooks.slack.com/services/'"$SLACK_WEBHOOK"'

fi

' > /usr/local/sbin/check_reboot_required.sh

chmod 744 /usr/local/sbin/check_reboot_required.sh

crontab -l | { cat; echo "00 00 * * * /usr/local/sbin/check_reboot_required.sh"; } | crontab -
