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
1. `./src/deploy.py`

If you user the 'test_data' data set then it comes with a default username 
("test.user@imperial.ac.uk") and password ("password")

## Disaster recovery
See [here](docs/DisasterRecovery.md)

## Passwords
To generate a password for a database user with username USERNAME and store it 
in the Vault:

```
sudo apt-get install pwgen
vault write secret/database/users/USERNAME password=$(pwgen -n1 80)
```

## Development
To update `src/versions.py` to the latest master of each sub repo, use 
`src/update_versions_to_latest_master.py`.