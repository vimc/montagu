from subprocess import Popen

import versions


def start(port):
    run("up -d", port)


def stop(port):
    run("down", port)


def run(args, port):
    args = "docker-compose --project-name montagu " + args
    p = Popen(args, env=get_env(port), shell=True)
    p.wait()
    if p.returncode != 0:
        raise Exception("An error occurred: docker-compose returned {}".format(p.returncode))


def get_env(port):
    return {
        'MONTAGU_PORT': str(port),
        'MONTAGU_API_VERSION': versions.api,
        'MONTAGU_DB_VERSION': versions.db,
        'MONTAGU_CONTRIB_VERSION': versions.contrib,
        'MONTAGU_ADMIN_VERSION': versions.admin,
        'MONTAGU_PROXY_VERSION': versions.proxy
    }
