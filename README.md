# Montagu
## Prerequisites
* [Docker Community Edition](https://docs.docker.com/engine/installation/) 
  (including Docker Compose)
* Python 3 and pip (Python 3 is included with Ubunti. For pip, use `apt install python3-pip`)
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

```
vault write secret/database/users/import password=$(pwgen -n1 80)
```
