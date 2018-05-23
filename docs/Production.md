# Production machine
production.montagu.dide.ic.ac.uk (also montagu.vaccineimpact.org)

Host fingerprint (ECDSA): `SHA256:Rq6floLvejnfcukkQKXbfcOqggg9/pnscwIBakY092s`

## SSH
SSH access is available on **port 10022**. We use this non-standard port to satisfy Imperial ICT as this port is (unlike on the other servers) intended to be available from outside the VPN.

So to access:

```
 ssh -p 10022 production.montagu.dide.ic.ac.uk
```

## Services
* [Montagu](https://github.com/vimc/montagu)

## Upgrading and rebooting
### Graceful shutdown
The machine should handle a sudden power loss without problems, so you can just
go ahead a reboot. However, before upgrading crucial infrastructure (like 
Docker) it may be a good idea to take a snapshot with:

```
sudo su
cd /montagu/deploy
./backup/backup.py
```

### Upgrade
```
sudo apt-get update
sudo apt-get upgrade
sudo reboot now   # if needed
```

### Resume
Montagu should resume automatically.
