# Montagu
## Prerequisites
* [Docker Community Edition](https://docs.docker.com/engine/installation/) 
* [Docker Compose](https://docs.docker.com/compose/install/)
* Python 3 and pip (Python 3 is included with Ubunti. For pip, use `apt install python3-pip`)
* [Vault](https://www.vaultproject.io/downloads.html) available on the command line as `vault`, with the address set via `export VAULT_ADDR=https://support.montagu.dide.ic.ac.uk:8200`
* Your machine needs to trust our Docker Registry. See 
  ["Configuring docker clients to use the registry"](https://github.com/vimc/montagu-ci#configuring-docker-clients-to-use-the-registry)

## Deploy
As root:

1. `(cd src && pip3 install --user -r requirements.txt)`
2. `./src/deploy.py`

### Settings
The deploy tool will ask you a series of questions interactively, suggesting
defaults along the way. These settings are saved to `./src/montagu-deploy.json`
and on the next deploy those questions will not be asked. If new settings are
added to the deploy tool, you will just be asked the new questions on your next
deploy.

If you change your mind, you can directly change the values in the json file,
delete the setting in question from the json file (prompting the tool to ask
you just that question again next time you deploy) or delete the whole json file
and go through the full interactive setup again.

#### Test users
If you use the 'test_data' data set then it comes with a default username 
("test.user@imperial.ac.uk") and password ("password")

When deploying to a testing environment using real data restored from live, 
setting the `add_test_user` option to true adds the above user with permissions 
to all modelling groups and reports.

### Root privileges
When deploying to the live server, make sure to first become the root user by 
running `sudo su`. This is neccessary to have the correct environment variables 
for the backup to run.

### Backup
If you set the initial data source to "restore", or you enable backups, the 
deploy tool will automatically configure our 
[backup tool](https://github.com/vimc/montagu-backup). To do so, it needs to
obtain an encryption key from the Vault. Once this has run once, the encryption
key and backup settings are saved to `/etc/montagu/backup`. Upon future runs of
the deploy tool, backup configuration will be skipped (using 
`backup/needs-setup.sh` as the test). If you know something has changed and you
want to force a rerun, delete the existing configuration 
(`sudo rm -r /etc/montagu/backup`).

## Disaster recovery
See [here](docs/DisasterRecovery.md)

## Passwords
### Retrieve
To get a database password for use with postgres, there is a helper script that
can be used like so:

```
export PGPASSWORD=$(./scripts/get_db_password.sh readonly)
psql -h support.montagu.dide.ic.ac.uk -U readonly -d montagu
```

This gets the password for the `readonly` user. To see all users, use
`vault list secret/database/users`

### Generate
To generate a password for a database user with username USERNAME and store it 
in the Vault:

```
sudo apt-get install pwgen
vault write secret/database/users/USERNAME password=$(pwgen -n1 80)
```

## Development
To update `src/versions.py` to the latest master of each sub repo, use 
`src/update_versions_to_latest_master.py`.
