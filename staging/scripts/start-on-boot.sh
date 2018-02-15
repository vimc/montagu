#!/usr/bin/env bash
set -ex
here=$(dirname $(dirname $(realpath $0)))
target=/etc/systemd/system/montagu-staging.service
read -p "What user should vagrant run as? " user

set -ex
cp $here/scripts/montagu-staging.service $target
sed -i "s:__PATH__:$here:g" $target
sed -i "s:__USER__:$user:g" $target
systemctl enable montagu-staging

set +x
echo ""
echo "Montagu staging VMs are installed as a service as user $user" 
echo "and will automatically resume after a system boot. To start the VMs now," 
echo "run:"
echo ""
echo "systemctl start montagu-staging"
echo ""
