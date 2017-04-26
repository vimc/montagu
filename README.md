# Montagu
## Prerequisites
* [Docker Community Edition](https://docs.docker.com/engine/installation/) (including Docker Compose)
* A way of running Bash scripts (e.g. on Windows install [Cygwin](https://www.cygwin.com/), Git Bash, or similar). Note: Apparently there is now something called [Windows 10 Bash Scripts](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/) that may be worth looking into.

## Deploy
To deploy Montagu run `./run.sh`

This will deploy the database, the API, and the Modelling groups Contribution Portal.

Open `http://localhost:8081` in a browser to view the portal.

## Demo
For demonstration purposes, you can then run (in another terminal) `./insert-test-data.sh` to put a couple of fake touchstones with some fake responsibilities in. The password is "changeme".
