#!/bin/sh
set -e

# This script does the one-time setup of vimc-robot ssh keys.  It will
# overwrite the existing keys without warning or checking that they
# are there.  You will have to set up the ssh key on github.

KEY_PATH=vimc_robot_ssh_key

mkdir -p $KEY_PATH
ssh-keygen -f $KEY_PATH/id_rsa -q -N ""
vault write secret/vimc/vimc-robot/id_rsa value=@$KEY_PATH/id_rsa

# NOTE: I am not sure about putting the public key in here rather than
# the filesystem but it seems like a reasonable spot
vault write secret/vimc/vimc-robot/id_rsa.pub value=@$KEY_PATH/id_rsa.pub

rm -r $KEY_PATH

echo "You must now add the key to the github account"
echo
echo "    https://github.com/settings/keys"
echo
echo "Ensure you are logged in as vimc-robot!"
echo
echo "Password is in"
echo
echo "    vault read -field=password secret/vimc/vimc-robot/password"
echo
echo "The public key is"
echo
echo "   vault read -field=value secret/vimc/vimc-robot/id_rsa.pub"
