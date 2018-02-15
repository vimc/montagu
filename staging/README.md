# Montagu staging
First, SSH to the support machine
```
ssh support.montagu.dide.ic.ac.uk
```

## To set up the staging VMs to run as a systemd service
```
sudo ./scripts/start-on-boot.sh
```
The VMs will then start automatically on boot, and shutdown gracefully when the
host system shuts down.

### Managing the service
* To start `sudo systemctl start montagu-staging.service`
* To stop `sudo systemctl stop montagu-staging.service`
* To uninstall the service (and disable auto start on boot): 
  `sudo ./scripts/remove-start-on-boot.sh`

### Service logging
```
systemctl status montagu-staging         # short status, run as ordinary user
sudo journalctl --unit montagu-staging   # full log, needs root
```

## Managing the staging VMs without installing them as a service
### To start the VMs
```
sudo su vagrant
cd ~/staging/staging
vagrant up
```

This will bring up two VMs; one called `uat` and one called `science`.

### To stop the VMs
```
sudo su vagrant
cd ~/staging/staging
vagrant halt
```

## To deploy on to a VM
To deploy onto the stage VM of your choice:

```
vagrant ssh uat            # or vagrant ssh science
cd montagu
./deploy.py                # or sudo deploy.py on science
```

You will be asked a series of interactive configuration questions. It's 
important that the port you configure Montagu with matches the eventual port
that users will be navigating to. So the port that Vagrant exposes the outside
world must match.

## Access the stage instances
From within the VM you can browse to:

UAT: https://support.montagu.dide.ic.ac.uk:10443

Science: https://support.montagu.dide.ic.ac.uk:11443

## To rebuild a VM

```
vagrant ssh uat -c '/vagrant/record-montagu-configuration'
vagrant destroy uat
vboxmanage closemedium disk disk/uat.vdi --delete
./scripts/restore-prepare.sh
vagrant up uat
vagrant ssh uat -c '/vagrant/restore'
```

## To test the restore

```
vagrant destroy -f restore-test
vboxmanage closemedium disk disk/restore-test.vdi --delete
./scripts/restore-prepare.sh
vagrant up restore-test
vagrant ssh restore-test -c '/vagrant/restore'
```

Then go to https://support.montagu.dide.ic.ac.uk:20443 where things should be running

## Troubleshooting

### Bringing up vms

If you get a error message like this on bringing up a VM

```
vagrant@fi--didevimc02:~/staging/staging$ vagrant up uat
Bringing machine 'uat' up with 'virtualbox' provider...
==> uat: Checking if box 'bento/ubuntu-16.04' is up to date...
==> uat: A newer version of the box 'bento/ubuntu-16.04' is available! You currently
==> uat: have version '2.3.5'. The latest is version '201708.22.0'. Run
==> uat: `vagrant box update` to update.
==> uat: Fixed port collision for 22 => 2222. Now on port 2203.
==> uat: Clearing any previously set network interfaces...
There was an error while executing `VBoxManage`, a CLI used by Vagrant
for controlling VirtualBox. The command and stderr is shown below.

Command: ["hostonlyif", "create"]

Stderr: 0%...
Progress state: NS_ERROR_FAILURE
VBoxManage: error: Failed to create the host-only adapter
VBoxManage: error: VBoxNetAdpCtl: Error while adding new interface: failed to open /dev/vboxnetctl: No such file or directory
VBoxManage: error: Details: code NS_ERROR_FAILURE (0x80004005), component HostNetworkInterfaceWrap, interface IHostNetworkInterface
VBoxManage: error: Context: "RTEXITCODE handleCreate(HandlerArg*)" at line 94 of file VBoxManageHostonly.cpp
```

The solution is to load the virtualbox module

```
sudo modprobe vboxnetadp
```

## Requirements

Install in the host machine:

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* `vagrant plugin install vagrant-persistent-storage`
