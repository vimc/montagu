# Troubleshooting

Some possible issues you may come across in trying to get Montagu running, especially on a local dev environment, 
and how to get around them. 

Please add to this doc if you find and fix any similar issues. 


## Docker Issues

**'No basic auth credentials' error when fetching image from docker**

You need to make sure you're logged in to docker as the montagu user, not as yourself, and for this you'll need to have 
vault set up. See here for some clues: https://github.com/vimc/montagu-registry/tree/master#login

If you've been running montagu applications at all this *should* all be set up, but it went snafu for me somehow.


**I've got a load of docker containers hanging around, how do I get rid of them all?**

Run:
```
docker stop $(docker ps -aq)
docker system prune --force
```

This script is present in some repos as `clear-docker.sh`.

To get rid of old volumes, you can run
```docker volume prune --force```

To remove (but not stop) containers and volumes in one line, use ```docker system prune --force --volumes```. 


**A container isn't starting or seems otherwise broken. How do I see its logs?**

```
docker logs [CONTAINER NAME]
```

## Vagrant / VM issues

**How can I run a support VM locally?**

From montagu-machine, run  `vagrant up <machine name>`

You'll probably want to use the machine name `dev`, whose configuration provides a minimal data set-up (similar to that 
used by BuildKite) in order to test code.

The other machine names you can use are `uat`, `science` and `latest` which are the configurations for the main support
VMs. Be careful with these, as these configurations may cause sizable data transfers - you can check the settings 
values for each in /montagu/settings. 

Run `vagrant ssh <machine name>` to log into the VM.

You can modify the montagu settings for deployment once you've logged in by editing `~/montagu/src/montagu-deploy.json`,
e.g. change `initial_data_source` to `minimal`. (The values in this file have been copied from the relevant file in 
/montagu/settings during VM provisioning.)


**And how do I tear it down again?**

If you want to destroy the machine entirely, so that it is rebuilt next time you run it, use e.g.:

```
vagrant destroy uat
```

You should also destroy the machine's disk by running `/staging/scripts/destroy-disk <machine name>`

If you just want to stop the machine so that it reboots as it is next time, use `halt` instead of `destroy`. 


**I'm trying to deploy a VM locally, and it's complaining about the api server name when setting up orderly.**

The  `instance_name` setting needs to match an api server defined in orderly's `orderly_config.yml`. 
Try changing the instance_name setting in montagu-deploy.json on the VM to 'buildkite' to bypass this step.


## Other issues

**Argh, it's killed my machine with a data avalanche!** 

Data is pulled from production if the 'update_on_deploy' flag in montagu/src/montagu-deploy.json is set to true. 
So you need to make sure that's false whether locally or in the VM (depending on where you're installing montagu) 
or it will absolutely murder your puny machine (~1TB I think).
