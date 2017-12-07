from time import sleep

import docker

import compose

# These values must line up with the docker-compose file

# Containers
api_name = "api"
reporting_api_name = "reporting_api"
db_name = "db"
contrib_name = "contrib"
admin_portal_name = "admin"
report_portal_name = "report"
proxy_portal_name = "proxy"
orderly_name = "orderly"

# Not always present
db_annex_name = "db_annex"

# Volumes
db_volume_name = "db_volume"
orderly_volume_name = "orderly_volume"

# Network
network_name = "default"

class MontaguService:
    def __init__(self, settings):
        self.client = docker.from_env()
        self.settings = settings
        self.prefix = settings["docker_prefix"]
        self.containers = [api_name, reporting_api_name, db_name,
                           contrib_name, admin_portal_name,
                           report_portal_name, proxy_portal_name,
                           orderly_name]
        self.use_fake_db_annex = settings["db_annex_type"] == "fake"
        if self.use_fake_db_annex:
            self.containers.append(db_annex_name)

    @property
    def container_names(self):
        return set([self._container_name(x) for x in self.containers])

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

    def _container_name(self, name):
        return '{}_{}_1'.format(self.prefix, name)

    @property
    def api(self):
        return self._get(api_name)

    @property
    def reporting_api(self):
        return self._get(reporting_api_name)

    @property
    def db(self):
        return self._get(db_name)

    @property
    def db_annex(self):
        return self._get(db_annex_name)

    @property
    def contrib_portal(self):
        return self._get(contrib_name)

    @property
    def admin_portal(self):
        return self._get(admin_portal_name)

    @property
    def proxy(self):
        return self._get(proxy_portal_name)

    @property
    def orderly(self):
        return self._get(orderly_name)


    @property
    def volume_present(self):
        present = [v.name for v in self.client.volumes.list()]
        return self.db_volume_name() in present

    @property
    def network_name(self):
        return "{}_{}".format(self.prefix, _network_name)

    @property
    def orderly_volume_name(self):
        return "{}_{}".format(self.prefix, _orderly_volume_name)

    @property
    def db_volume_name(self):
        return "{}_{}".format(self.prefix, _db_volume_name)

    def _get(self, name):
        try:
            return self.client.containers.get(self._container_name(name))
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
        print("Stopping Montagu...", flush=True)
        if self.orderly:
            self.orderly.kill("SIGINT")
        compose.stop(self.settings["port"], self.settings["hostname"],
                     persist_volumes=self.settings["persist_data"],
                     use_fake_db_annex=self.use_fake_db_annex,
                     docker_prefix=self.prefix)

    def start(self):
        print("Starting Montagu...", flush=True)
        compose.pull(self.settings["port"], self.settings["hostname"],
                     self.prefix)
        compose.start(self.settings["port"], self.settings["hostname"],
                      self.use_fake_db_annex, self.prefix)
        print("- Checking Montagu has started successfully")
        sleep(2)
        if service.status != "running":
            raise Exception("Failed to start Montagu. Service status is {}".format(service.status))

__all__ = ["MontaguService"]
