from subprocess import run, Popen, check_output

import versions


def start():
    args = [
        "docker-compose",
        "--project-name", "montagu",
        "up",
        "-d"
    ]
    env = {
        'MONTAGU_API_VERSION': versions.api,
        'MONTAGU_DB_VERSION': versions.db,
        'MONTAGU_CONTRIB_VERSION': versions.contrib,
        'MONTAGU_ADMIN_VERSION': versions.admin,
    }
    return_code = Popen(args, env=env).wait()
    if return_code < 0:
        raise Exception("An error occurred starting Montagu (docker-compose returned {})".format(return_code))


def stop():
    check_output([
        "docker-compose",
        "--project-name", "montagu",
        "down"
    ])
