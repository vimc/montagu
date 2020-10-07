from subprocess import Popen
from docker_helpers import montagu_registry

import shutil

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
    staging_file =  "-f ../docker-compose.staging.yml" if settings["fake_smtp"] else ""
    exe = shutil.which("docker-compose")
    if not exe:
        raise Exception("Did not find docker-compose on path")
    prefix = '{} -f ../docker-compose.yml {} --project-name {} '.format(
        exe, staging_file, docker_prefix)
    cmd = prefix + args
    print(cmd)
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
        'VIMC_REGISTRY': "vimc",

        'MONTAGU_PORT': str(port),
        'MONTAGU_HOSTNAME': hostname,

        'MONTAGU_API_VERSION': versions.api,

        'MONTAGU_DB_VERSION': versions.db,
        'MONTAGU_DB_CONF': "/etc/montagu/" + db_config_file,

        'MONTAGU_CONTRIB_PORTAL_VERSION': versions.contrib_portal,
        'MONTAGU_ADMIN_PORTAL_VERSION': versions.admin_portal,

        'MONTAGU_PROXY_VERSION': versions.proxy,

        'MONTAGU_STATIC_VERSION': versions.static,

        'MONTAGU_TASK_QUEUE_VERSION': versions.task_queue
    }
