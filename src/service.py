from time import sleep

import docker

import compose

# These values must line up with the docker-compose file
components = {
    "containers": {
        # logical name: container name in docker compose
        "api": "api",
        "reporting_api": "reporting_api",
        "db": "db",
        "contrib_portal": "contrib",
        "admin_portal": "admin",
        "reporting_portal": "report",
        "proxy": "proxy",
        "orderly": "orderly"
    },
    "volumes": {
        "db": "db_volume",
        "orderly": "orderly_volume"
    },
    "network": "default"
}

# These are not always present so will be added above as needed
db_annex_container_name = "db_annex"
db_annex_volume_name = "db_annex_volume"

class MontaguService:
    def __init__(self, settings):
        self.client = docker.from_env()
        self.settings = settings
        self.prefix = settings["docker_prefix"]
        self.use_fake_db_annex = settings["db_annex_type"] == "fake"
        # Our components:
        self.containers = components['containers'].copy()
        self.volumes = components['volumes'].copy()
        self.network = components['network']
        if self.use_fake_db_annex:
            self.containers["annex"] = db_annex_container_name
            self.volumes["annex"] = db_annex_volume_name

    @property
    def container_names(self):
        return set([self.container_name(x) for x in self.containers.keys()])

    @property
    def status(self):
        expected = self.container_names
        actual = dict((c.name, c) for c in self.client.containers.list(all=True))
        unexpected = list(x for x in actual.keys() - expected
                          if x.startswith(self.prefix + "_"))
        if any(unexpected):
            raise Exception("There are unexpected Montagu-related containers running: {}".format(unexpected))

        services = list(c for c in actual.values() if c.name in expected)
        statuses = set(c.status for c in services)

        if len(statuses) == 1:
            return statuses.pop()
        elif len(statuses) == 0:
            return None
        else:
            status_map = dict((c.name, c.status) for c in services)
            raise Exception("Montagu service is in a indeterminate state. "
                            "Manual intervention is required.\nStatus: {}".format(status_map))

    def container_name(self, name):
        return "{}_{}_1".format(self.prefix, self.containers[name])

    def volume_name(self, name):
        return "{}_{}".format(self.prefix, self.volumes[name])

    @property
    def api(self):
        return self._get("api")

    @property
    def reporting_api(self):
        return self._get("reporting_api")

    @property
    def db(self):
        return self._get("db")

    @property
    def db_annex(self):
        return self._get("db_annex")

    @property
    def contrib_portal(self):
        return self._get("contrib_portal")

    @property
    def admin_portal(self):
        return self._get("admin_portal")

    @property
    def proxy(self):
        return self._get("proxy")

    @property
    def orderly(self):
        return self._get("orderly")

    @property
    def db_volume_present(self):
        try:
            self.client.volumes.get(self.volume_name("db"))
            return True
        except docker.errors.NotFound:
            return False

    @property
    def network_name(self):
        return "{}_{}".format(self.prefix, self.network)

    def _get(self, name):
        try:
            return self.client.containers.get(self.container_name(name))
        except docker.errors.NotFound:
            return None

    def stop(self):
        # As documented in VIMC-805, the orderly container will
        # respond quickly to an interrupt, but not to whatever docker
        # stop (via docker-compose stop) is sending. This is
        # (presumably) a limitation of httpuv and not something I can
        # see how to work around at the R level. So instead we send an
        # interrupt signal (SIGINT) just before the stop, and that
        # seems to bring things down much more quicky.
        print("Stopping Montagu...({}: {})".format(
            self.settings["instance_name"], self.settings["docker_prefix"]),
            flush=True)
        if self.orderly:
            try:
                self.orderly.kill("SIGINT")
            except:
                print("Killing orderly container failed - continuing")
                pass
        compose.stop(self.settings)

    def start(self):
        print("Starting Montagu...", flush=True)
        compose.pull(self.settings)
        compose.start(self.settings)
        print("- Checking Montagu has started successfully")
        sleep(2)
        if self.status != "running":
            raise Exception("Failed to start Montagu. Service status is {}".format(self.status))

__all__ = ["MontaguService"]
