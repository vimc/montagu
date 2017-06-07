from subprocess import run, Popen

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
        'MONTAGU_CONTRIB_VERSION': versions.contrib
    }
    Popen(args, env=env).wait()


def stop():
    run([
        "docker-compose",
        "--project-name", "montagu",
        "down"
    ])
