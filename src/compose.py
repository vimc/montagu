from subprocess import Popen
from docker_helpers import montagu_registry

import versions


def start(settings):
    run("up -d", settings)


def stop(settings):
    run("stop", settings)
    run("rm -f", settings)


def pull(settings):
    run("pull", settings)


def run(args, settings):
    docker_prefix = settings["docker_prefix"]
    prefix = 'docker-compose --project-name {} '.format(docker_prefix)
    cmd = prefix + args
    p = Popen(cmd, env=get_env(settings), shell=True)
    p.wait()
    if p.returncode != 0:
        raise Exception("An error occurred: docker-compose returned {}".format(p.returncode))


def get_env(settings):
    port = settings["port"]
    hostname = settings["hostname"]
    if settings["use_production_db_config"]:
        db_config_file = "postgresql.production.conf"
    else:
        db_config_file = "postgresql.conf"

    return {
        'MONTAGU_REGISTRY': montagu_registry,

        'MONTAGU_PORT': str(port),
        'MONTAGU_HOSTNAME': hostname,

        'MONTAGU_API_VERSION': versions.api,

        'MONTAGU_DB_VERSION': versions.db,
        'MONTAGU_DB_CONF': "/etc/montagu/" + db_config_file,

        'MONTAGU_CONTRIB_PORTAL_VERSION': versions.contrib_portal,
        'MONTAGU_ADMIN_PORTAL_VERSION': versions.admin_portal,

        'MONTAGU_PROXY_VERSION': versions.proxy,

        'MONTAGU_STATIC_VERSION': versions.static

        'MONTAGU_TASK_QUEUE_VERSION': versions.task_queue
    }
