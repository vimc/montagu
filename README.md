# Montagu
## Prerequisites
* [Docker Community Edition](https://docs.docker.com/engine/installation/) (including Docker Compose)
* A way of running Bash scripts (e.g. on Windows install [Cygwin](https://www.cygwin.com/), Git Bash, or similar). Note: Apparently there is now something called [Windows 10 Bash Scripts](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/) that may be worth looking into.
* Your machine needs to trust our Docker Registry. See ["Configuring docker clients to use the registry"](https://github.com/vimc/montagu-ci#configuring-docker-clients-to-use-the-registry)

## Deploy
To deploy Montagu run `./run.sh`

This will deploy the database, the API, and the Modelling groups Contribution Portal.

Open `http://localhost:8081` in a browser to view the portal.

## Stop
To stop Montagu, pressing Ctrl+C may be enough, but if not: run `docker-compose down`

## Demo
Prerequisites: psql (Postgres) available on the command line.

For demonstration purposes, you can then run (in another terminal) `./insert-test-data.sh` to put a couple of fake touchstones with some fake responsibilities in. The password is "changeme".

On Windows, you can run `./insert-test-data.ps1` instead.
