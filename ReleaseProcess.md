# Release process
(Work in progress)

1. Update the versions of the subprojects you are using to the latest versions
   of master using `update_versions_to_latest_master.py` (or manually update
   versions.py to specific versions) and commit your change.
2. Tag the release and build the release log by running 
   `./scripts/release/make-release.py`
   This script will warn you if any tickets are merged in that are not "Ready 
   to Deploy". It will automatically push the tag and commit.
3. Check build has passed in Teamcity
4. Connect to the UAT machine and deploy there (see below)
5. You may go through multiple rounds of steps 1-3 until you have a release
   you are happy to deploy to production.
6. Deploy to live:
   1. `ssh -p 10022 production.montagu.dide.ic.ac.uk`
   1. `sudo su`
   1. `cd /montagu/deploy`
   1. `./deploy.py --docker-hub`
7. Use `RELEASE_LOG.md` to know which tickets to update to the 'Deployed' status

## Deploying to UAT

1. `ssh support.montagu`
2. Become the vagrant user and cd into their home directory `sudo su vagrant && cd`
3. Run `./uat.sh` which will give you a shell inside the virtual machine.
4. `cd montagu`
5.  2 options here:

    i) To deploy the latest tagged release, run `sudo -E ./deploy.py`

    ii) To run a specific branch, for example to run the latest master branch:
    ```
    sudo git checkout master && git pull && git submodule update --recursive
    sudo -E ./src/deploy.py
    ```
    
    Note the different deploy scripts in i) and i) : `./src/deploy.py` deploys the 
    contents of the current directory, whereas the top level `./deploy.py` first updates 
    things to the latest tag. Unfortunately we need to be `sudo` to deploy, because the 
    tool installs `bb8` as part of the process.
