from subprocess import run, PIPE

# The idea here is to prevent deploying into production a system that
# is untagged and/or has a dirty git status (the latter is most
# commonly triggered by a submodule being out of date - seen with the
# backup module).
#
# We only want this on production really.  We detect this by looking
# to see if 'backup' is selected (this will be false for all but
# production).
#
# It would be easy enough to add a check to ensure that the tag
# actually exists on the remote machine, but that requires
#
#   git ls-remote --tags {remote} refs/tags/{tag}
#
# and that *does* use the network which slows things down a little.
# This is only an issue if people are tagging on the production
# machine, so it would be good if that did not happen.
def git_check(settings):
    strict = settings["backup"]

    sha = git_sha()
    if not sha:
        # This happens on teamcity
        report("running outside of git tree")
        return

    is_clean = git_is_clean()

    def report(msg):
        if strict:
            raise Exception(msg)
        else:
            print("NOTE: " + msg)

    if not is_clean:
        report("git status reports directory is unclean")

    tag = git_get_tag(sha)
    if not tag:
        report("HEAD is not tagged")
        tag = "<<UNTAGGED>>"

    print("This is montagu {tag} ({sha})".format(tag = tag, sha = sha))

def git_is_clean():
    p = run(["git", "status", "-s"], stdout = PIPE, stderr = PIPE)
    return len(p.stdout) == 0

def git_get_tag(ref):
    args = ["git", "describe", "--tags", "--exact-match", ref]
    p = run(args, stdout = PIPE, stderr = PIPE)
    if p.returncode == 0:
        tag = p.stdout.decode("utf-8").strip()
    else:
        tag = None
    return tag

def git_sha():
    args = ["git", "rev-parse", "HEAD"]
    p = run(args, stdout = PIPE, stderr = PIPE)
    code = p.returncode
    if code == 128:
        return None
    elif code == 0:
        return p.stdout.decode("utf-8").strip()
    else:
        raise Exception(p.stderr.decode("utf-8").strip())
