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
4. [Connect to the UAT machine and deploy there](staging/README.md)
5. You may go through multiple rounds of steps 1-3 until you have a release
   you are happy to deploy to production.
6. Deploy to live:
   1. `ssh production.montagu.dide.ic.ac.uk`
   1. `sudo su`
   1. `cd /montagu/deploy`
   1. `MONTAGU_USE_DOCKER_HUB=true ./deploy.sh`
7. Use RELEASE_LOG.md to know which tickets to update to the 'Deployed' status
