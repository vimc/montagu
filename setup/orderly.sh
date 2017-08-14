#!/bin/sh

# This all needs moving into the python scripts, but I don't have time today.

# The right thing to do here will depend entirely on how we are
# managing backups.  If we backup the entire reports directory then
# we'd just want to restore that.  If we are backing up the data/ and
# archive/ directories only then some variant of the below is
# reasonable.

# First, extract secrets out of the vault; this creates three files -
# the ssh keypair in .ssh/ and montagu's postgres credentials in
# .Renviron.  The permissions on the ssh private key are important!

DEST=orderly_tmp
rm -rf $DEST
mkdir -p $DEST/.ssh
vault read -field=value secret/vimc-robot/id_rsa > $DEST/.ssh/id_rsa
chmod 600 $DEST/.ssh/id_rsa
vault read -field=value secret/vimc-robot/id_rsa.pub > $DEST/.ssh/id_rsa.pub
PGPASS=$(vault read -field=password secret/database/users/orderly)
cat <<EOF > $DEST/.Renviron
MONTAGU_HOST=db
MONTAGU_PORT=5432
MONTAGU_USER=orderly
MONTAGU_PASSWORD=$PGPASS
EOF

# In order to be able to use git without prompting we need to check
# the known hosts.  Ideally this would be verified to avoid a MITM
# attack.
ssh-keyscan github.com > $DEST/.ssh/known_hosts

# In order to write to the orderly volume we need a new container.
# This runs "sleep 3600" as a daemon, which does actually work (I
# think I had this working with bash before, but this does not seem to
# work today and I don't understand why it did apparently work).  We
# need to close this down at the end of the script.
docker pull docker.montagu.dide.ic.ac.uk:5000/montagu-reports:master
docker run --rm -d \
       --entrypoint sleep \
       --name orderly_setup \
       -v montagu_orderly_volume:/orderly \
       docker.montagu.dide.ic.ac.uk:5000/montagu-reports:master \
       3600

# This command is useful to clear outp the orderly store entirely, but
# be careful
docker exec orderly_setup sh -c 'rm -rf /orderly/.??* /orderly/*'

# Copy the required files into the persistent data volume part of th
# container and remove the temporary directory that we used to store
# them
docker cp "$DEST/.ssh" orderly_setup:/orderly
docker cp "$DEST/.Renviron" orderly_setup:/orderly

## Then, in the container itself, clone down the montagu-reports repo
## and set up a blank index.  This will behave poorly if the directory
## is not empty.
docker exec -it orderly_setup /usr/bin/montagu-reports-clone
docker stop -t0 orderly_setup

rm -rf $DEST
