# Troubleshooting

Some possible issues you may come across in trying to get Montagu running, especially on a local dev environment, and how to get around them. 

Please add to this doc if you find and fix any similar issues. 


## Docker Issues

**'No basic auth credentials' error when fetching image from docker**

You need to make sure you're logged in to docker as the montagu user, not as yourself, and for this you'll need to have vault set up. See here for some clues: https://github.com/vimc/montagu-registry/tree/master#login

If you've been running montagu applications at all this *should* all be set up, but it went snafu for me somehow.


**I've got a load of docker containers hanging around, how do I get rid of them all?**

Run:
```
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker network prune --force
```

This script is present in some repos as `clear-docker.sh`.

You can also run
```
docker volume prune --force
```
to get rid of old volumes. 


**A container isn't starting or seems otherwise broken. How do I see its logs?**

```
docker logs [CONTAINER NAME]
```

## Vagrant / VM issues

**How can I run a support VM locally?**

From montagu-machine, run  `sudo vagrant up uat` or `sudo vagrant up science`

Run `sudo vagrant ssh uat` (or other machine name) to log into the VM.


**And how do I tear it down again?**

If you want to destroy the machine entirely, so that it is rebuilt next time you run it, use e.g.:

```
sudo vagrant destroy uat
```
If you just want to stop the machine so that it reboots as it is next time, use `halt` instead of `destroy`. 


**Vagrant is erroring with "Vagrant failed to initialize at a very early stage: The home directory you specified is not accessible..." etc**

Remember to run as sudo. 


**I'm trying to run montagu on UAT or Science locally, and it's failing to set up the database / clone reports / other data gremlins.**

Running UAT configuration locally is somewhat broken. Consider running from your VM with the montagu/src/montagu-deploy.json settings used by TeamCity:
https://github.com/vimc/montagu/blob/master/settings/teamcity.json


**I'm trying to run montagu on UAT or Science locally, and it's complaining about the api server name when setting up orderly.**

Try changing the instance_name setting in montagu-deploy.json on the VM to 'teamcity'.


## Other issues

**Argh, it's killed my machine with a data avalanche!** 

Data is pulled from production if the 'update_on_deploy' flag in montagu/src/montagu-deploy.json is set to true. So you need to make sure that's false whether locally or in the VM (depending on where you're installing montagu) or it will absolutely murder your puny machine (~1TB I think).


 
 





