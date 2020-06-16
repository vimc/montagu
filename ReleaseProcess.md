# Release process
(Work in progress)

If this is first time release then clone this repo on your local machine and run `git submodule update --init --recursive` to initialise the submodules.

1. From your local machine update the versions of the subprojects you are using 
   to the latest versions of master using `./src/update_versions_to_latest_master.py` 
   (or manually update versions.py to specific versions). 
1. Stage changes with `git add .` and commit and push these changes. At this point, `git status` may show some submodules as 
   having modified content, not staged for commit. (This will happen if submodules of submodules, e.g. models, have changed.) 
   Fix this by running `git submodule update --recursive`. 
1. Build the release log by running 
   `./scripts/release/make-release.py`
   You will be prompted to set env variable YOUTRACK_TOKEN if not set. See
   [youtrack docs](https://www.jetbrains.com/help/youtrack/standalone/Manage-Permanent-Token.html#) for how to set this up.
   This script will prompt you for a tag, use the next verison number as the tag. It will also
   warn you if any tickets are merged in that are not "Ready to Deploy".
1. The script will prompt you to review changes and push tags via
   ```
    git push --follow-tags
    ./scripts/release/tag-images.py tag --publish latest
    ```
1. Check build has passed in Teamcity
1. Connect to the UAT machine and deploy there (see below)
1. You may go through multiple rounds of steps 1-3 until you have a release
   you are happy to deploy to production.
1. Deploy to science
1. Deploy to live:
   1. `ssh -p 10022 montagu@production.montagu.dide.ic.ac.uk`
   1. `cd montagu`
   1. `./deploy.py --docker-hub`
1. Use `RELEASE_LOG.md` to know which tickets to update to the 'Deployed' status

## Deploying to UAT & science

Note if you are deploying to science warn science team first that it will be going down for a period as they may be actively using it

1. Connect as the vagrant user: `ssh vagrant@support.montagu` (or `ssh support.montagu` and then `sudo su vagrant && cd`)
2. Run `./uat.sh` or `./science.sh` which will give you a shell inside the virtual machine.
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

    Note also when deploying science it updates the database from production
    which takes a long time. You can skip this by changing the configuration.
    Edit `src/montagu-deploy.json` and change `update_on_deploy` field to `false`.
    Deploy and then make sure to reset to `true` when deploy has completed.
5. If deploying science we want to make the data vis tool publicly accessible so run `./scripts/copy-vis-tool.sh` after the deploy has complete. This is temporary and we will run automatically once the public data vis tool is deployed on production.
