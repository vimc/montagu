#!/usr/bin/env bash
set -ex
systemctl disable montagu-staging.service
rm /etc/systemd/system/montagu-staging.service
echo "Done"
