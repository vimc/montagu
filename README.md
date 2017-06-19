# Montagu
## Prerequisites
* [Docker Community Edition](https://docs.docker.com/engine/installation/) 
  (including Docker Compose)
* Python 3.5 and pip
* Your machine needs to trust our Docker Registry. See 
  ["Configuring docker clients to use the registry"](https://github.com/vimc/montagu-ci#configuring-docker-clients-to-use-the-registry)

## Deploy
1. `pip -r install --user requirements.txt`
1. `./src/deploy.py`

If you user the 'test_data' data set then it comes with a default username 
("test.user@imperial.ac.uk") and password ("password")