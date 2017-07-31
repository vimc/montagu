from subprocess import Popen

import versions


def start(port, hostname):
    run("up -d", port, hostname)


def stop(port, hostname, persist_volumes):
    if persist_volumes:
        run("down", port, hostname)
    else:
        run("down --volumes", port, hostname)  # Also deletes volumes


def pull(port, hostname):
    run("pull", port, hostname)


def run(args, port, hostname):
    args = "docker-compose --project-name montagu " + args
    p = Popen(args, env=get_env(port, hostname), shell=True)
    p.wait()
    if p.returncode != 0:
        raise Exception("An error occurred: docker-compose returned {}".format(p.returncode))


def get_env(port, hostname):
    return {
        'MONTAGU_PORT': str(port),
        'MONTAGU_HOSTNAME': hostname,

        'MONTAGU_API_VERSION': versions.api,
        'MONTAGU_REPORTING_API_VERSION': versions.reporting_api,
        'MONTAGU_DB_VERSION': versions.db,

        'MONTAGU_CONTRIB_PORTAL_VERSION': versions.contrib_portal,
        'MONTAGU_ADMIN_PORTAL_VERSION': versions.admin_portal,
        'MONTAGU_REPORT_PORTAL_VERSION': versions.report_portal,

        'MONTAGU_PROXY_VERSION': versions.proxy
    }
