#!/bin/sh

# This all needs moving into the python scripts, but I don't have time today.

# First, extract secrets out of the vault; this creates three files -
# the ssh keypair in .ssh/ and montagu's postgres credentials in
# .Renviron.  The permissions on the ssh private key are important!

DEST=orderly_tmp
rm -rf $DEST
mkdir -p $DEST/.ssh
vault read -field=value secret/vimc-robot/id_rsa > $DEST/.ssh/id_rsa
chmod 600 $DEST/.ssh/id_rsa
vault read -field=value secret/vimc-robot/id_rsa.pub > $DEST/.ssh/id_rsa.pub
PGPASS=$(vault read -field=password secret/database/users/import)
cat <<EOF > $DEST/.Renviron
MONTAGU_HOST=db
MONTAGU_PORT=5432
MONTAGU_PASSWORD=$PGPASS
EOF

# In order to be able to use git without prompting we need to check
# the known hosts.  Ideally this would be verified to avoid a MITM
# attack.
ssh-keyscan github.com > $DEST/.ssh/known_hosts

# In order to write to the orderly volume we need a new container.
# This runs "bash" as a daemon, which does actually work.  We need to
# close this down at the end of the script.
docker run --rm -d \
       --entrypoint bash \
       --name orderly_setup \
       -v montagu_orderly_volume:/orderly \
       docker.montagu.dide.ic.ac.uk:5000/montagu-reports:master

# This command is useful to clear outp the orderly store entirely, but
# be careful
#   docker exec orderly_setup sh -c 'rm -rf /orderly/.??* /orderly/*'

# Copy the required files into the persistent data volume part of th
# container and remove the temporary directory that we used to store
# them
docker cp "$DEST/.ssh" orderly_setup:/orderly
docker cp "$DEST/.Renviron" orderly_setup:/orderly
rm -rf $DEST

## Then, in the container itself, clone down the montagu-reports repo
## and set up a blank index.  This will behave poorly if the directory
## is not empty.
docker exec -it orderly_setup /usr/bin/montagu-reports-clone
docker stop orderly_setup
