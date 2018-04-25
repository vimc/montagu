# Annex machine
annex.montagu.dide.ic.ac.uk

Host key fingerprint (ECDSA): `SHA256:lYJUME+1ATyTvzcFvs8K+aSOBfX/Xv3mpz3kKeYdzM4`

## Services
* Annex database (in docker container)

## Upgrading and rebooting
```
sudo apt update
sudo apt upgrade
sudo reboot now
```

We couldn't upgrade because VirtualBox was running. If so, you may find this
untested script that should hibernate all VirtualBox VMs that are running. You
could replace "savestate" with "poweroff" if you're sure none of the running VMs
are important.

```
vboxmanage list runningvms \
    | sed -r 's/.*\{(.*)\}/\1/' \
    | xargs -L1 -I {} VBoxManage controlvm {} savestate
```

The annex will restart automatically.
