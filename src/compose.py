from subprocess import Popen, check_output

import versions


def start():
    args = "docker-compose --project-name montagu up -d"
    env = {
        'MONTAGU_API_VERSION': versions.api,
        'MONTAGU_DB_VERSION': versions.db,
        'MONTAGU_CONTRIB_VERSION': versions.contrib,
        'MONTAGU_ADMIN_VERSION': versions.admin,
        'MONTAGU_PROXY_VERSION': versions.proxy,
    }
    p = Popen(args, env=env, shell=True)
    p.wait()
    if p.returncode != 0:
        raise Exception("An error occurred starting Montagu (docker-compose returned {})".format(p.returncode))


def stop():
    check_output("docker-compose --project-name montagu down", shell=True)
