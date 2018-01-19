# Support machine
support.montagu.dide.ic.ac.uk

## Services
* [TeamCity](https://github.com/vimc/montagu-ci) (via vagrant)
* [Staging](https://github.com/vimc/montagu/tree/master/staging) (via vagrant)
* [Docker registry](https://github.com/vimc/montagu-registry) 
  (as Docker container)
* [Vault](https://github.com/vimc/montagu-vault) (as Docker container)

## Upgrading and rebooting
### Graceful shutdown
This could be automated:

1. Stop TeamCity: [Instructions](https://github.com/vimc/montagu-ci/blob/master/README.md#stopping-teamcity)
1. Stop staging: [Instructions](https://github.com/vimc/montagu/blob/master/staging/README.md#to-stop-the-vms)

Docker will automatically stop containers on shutdown, and in any case we're
confident the Vault and the Registry will handle an unexpected termination.

### Upgrade
```
sudo apt-get update
sudo apt-get upgrade
sudo reboot now   # if needed
```

### Resume
Docker registry comes back automatically.

All except the Vault should be scriptable to start on boot.

1. Start Vault: [Instructions](https://github.com/vimc/montagu-vault#restarting-andor-restoring-the-vault)
1. Start TeamCity: [Instructions](https://github.com/vimc/montagu-ci/blob/master/README.md#restarting-teamcity-server)
1. Start stage VMs: [Instructions](https://github.com/vimc/montagu/blob/master/staging/README.md#to-run-the-vms)
1. Unseal the Vault: [Instructions](https://github.com/vimc/montagu-vault#unsealing-the-vault)
1. Redeploy to stage VMs: [Instructions](https://github.com/vimc/montagu/tree/master/staging#to-deploy-on-to-a-vm)
   This will stop being necessary if we implement [VIMC-1366](https://vimc.myjetbrains.com/youtrack/issue/VIMC-1366)

You can check things are working by:

1. TeamCity: Going to http://teamcity.montagu.dide.ic.ac.uk:8111 and checking 
   that the page loads and that 3 agents are connected.
1. Registry: Running `docker pull docker.montagu.dide.ic.ac.uk:5000/montagu-db:master`
1. Staging: Browsing to the instances: [URLs](https://github.com/vimc/montagu/blob/master/staging/README.md#access-the-stage-instances)
1. Vault: If you were able to unseal it, then it's up

