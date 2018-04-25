# Support machine
support.montagu.dide.ic.ac.uk

Host key fingerprint: `SHA256:etgLOXa8brU/0SsfYfoFwsNW3ljbkLPd3okPJlICN6A root@fi--didevimc02 (ECDSA)`

## Services
* [TeamCity](https://github.com/vimc/montagu-ci) 
  (via vagrant, installed as a systemd service as `montagu-ci`)
* [Staging](https://github.com/vimc/montagu/tree/master/staging)
  (via vagrant, installed as a systemd service as `montagu-staging`)
* [Docker registry](https://github.com/vimc/montagu-registry) 
  (as Docker container)
* [Vault](https://github.com/vimc/montagu-vault) (as Docker container)

## Upgrading and rebooting
### Graceful shutdown
Everything will shutdown gracefully on host system shutdown. The Vagrant VMs
are installed as a service (once 
https://vimc.myjetbrains.com/youtrack/issue/VIMC-1477 is deployed) and Docker
will automatically stop containers on shutdown.

### Upgrade
```
sudo apt-get update
sudo apt-get upgrade
sudo reboot now   # if needed
```

### Resume
Docker registry, TeamCity, and staging VMs come back automatically.

All except the Vault should be scriptable to start on boot.

1. Unseal the Vault: [Instructions](https://github.com/vimc/montagu-vault#unsealing-the-vault)
1. Start Vault: [Instructions](https://github.com/vimc/montagu-vault#restarting-andor-restoring-the-vault)

You can check things are working by:

1. TeamCity: Going to http://teamcity.montagu.dide.ic.ac.uk:8111 and checking 
   that the page loads and that 3 agents are connected.
1. Registry: Running `docker pull docker.montagu.dide.ic.ac.uk:5000/montagu-db:master`
1. Staging: Browsing to the instances: [URLs](https://github.com/vimc/montagu/blob/master/staging/README.md#access-the-stage-instances)
1. Vault: If you were able to unseal it, then it's up

