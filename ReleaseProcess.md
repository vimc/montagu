# Release process
(Work in progress)

1. Update the versions of the subprojects you are using to the latest versions
   of master using `update_versions_to_latest_master.py` (or manually update
   versions.py to specific versions).
2. Stage changes with `git add .` and commit and push these changes. At this point, `git status` may show some submodules as 
   having modified content, not staged for commit. (This will happen if submodules, e.g. models, have changed.) 
   Fix this by running `git submodule update --recursive` 
3. Tag the release and build the release log by running 
   `./scripts/release/make-release.py`
   This script will warn you if any tickets are merged in that are not "Ready 
   to Deploy". It will automatically push the tag and commit.
4. Check build has passed in Teamcity
5. Connect to the UAT machine and deploy there (see below)
6. You may go through multiple rounds of steps 1-3 until you have a release
   you are happy to deploy to production.
7. Deploy to live:
   1. `ssh -p 10022 montagu@production.montagu.dide.ic.ac.uk`
   1. `cd deploy`
   1. `./deploy.py --docker-hub`
8. Use `RELEASE_LOG.md` to know which tickets to update to the 'Deployed' status

## Deploying to UAT

1. Connect as the vagrant user: `ssh vagrant@support.montagu` (or `ssh support.montagu` and then `sudo su vagrant && cd`)
2. Run `./uat.sh` which will give you a shell inside the virtual machine.
3. `cd montagu`
4.  2 options here:

    i) To deploy the latest tagged release, run `./deploy.py`

    ii) To run a specific branch:
    ```
    git fetch && git checkout <branchname> && git merge && git submodule update --recursive
    ./src/deploy.py
    ```
    
    Note the different deploy scripts in i) and i) : `./src/deploy.py`
    deploys the contents of the current directory, whereas the top
    level `./deploy.py` first updates things to the latest tag.
