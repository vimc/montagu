# Production machine
production.montagu.dide.ic.ac.uk (also montagu.vaccineimpact.org)

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
