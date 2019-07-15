from time import sleep

import docker

import compose

# These values must line up with the docker-compose file
components = {
    "containers": {
        # logical name: container name in docker compose
        "api": "api",
        "db": "db",
        "contrib_portal": "contrib",
        "admin_portal": "admin",
        "proxy": "proxy",
        "metrics": "metrics",
        "static": "static"
    },
    "volumes": {
        "static_logs": "static_logs",
        "static": "static_volume",
        "db": "db_volume",
        # NOTE: even though we've dropped orderly from the deploy we
        # might depend on this volume for copying guidance reports
        # into the contrib portan and the static server.
        "orderly": "orderly_volume",
        "templates": "template_volume",
        "guidance": "guidance_volume"
    },
    "network": "default"
}

# These are not always present so will be added above as needed
db_annex_container_name = "db_annex"
db_annex_volume_name = "db_annex_volume"

class MontaguService:
    def __init__(self, settings):
        self.client = docker.from_env()
        self.settings = dict(settings)
        ## TODO: This will eventually be lifted up to be a setting
        self.docker_prefix = "montagu"
        self.settings['docker_prefix'] = self.docker_prefix
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
                          if x.startswith(self.docker_prefix + "_"))
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
        return "{}_{}_1".format(self.docker_prefix, self.containers[name])

    def volume_name(self, name):
        return "{}_{}".format(self.docker_prefix, self.volumes[name])

    def start_metrics(self):
        # Metrics container has to be started last, after proxy has its SSL cert and is able to serve basic_status
        self.client.containers.run('nginx/nginx-prometheus-exporter:0.4.1',
                                    restart_policy = {"Name": "always"},
                                    ports = {'9113/tcp': 9113},
                                    command = '-nginx.scrape-uri "http://montagu_proxy_1/basic_status"',
                                    network = 'montagu_default',
                                    name = self.container_name("metrics"),
                                    detach = True)

    def stop_metrics(self):
        # Since we now start the metrics container outside of compose, we need to tear it down separately too
        container_name = self.container_name("metrics")
        print ("Stopping Montagu metrics container {}".format(container_name))
        metrics_container = self.client.containers.get(container_name)
        metrics_container.remove(force=True)

    @property
    def api(self):
        return self._get("api")

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
    def static(self):
        return self._get("static")

    @property
    def db_volume_present(self):
        try:
            self.client.volumes.get(self.volume_name("db"))
            return True
        except docker.errors.NotFound:
            return False

    @property
    def network_name(self):
        return "{}_{}".format(self.docker_prefix, self.network)

    def _get(self, name):
        try:
            return self.client.containers.get(self.container_name(name))
        except docker.errors.NotFound:
            return None

    def stop(self):
        try:
            self.stop_metrics()
        except Exception as e:
            print("Error when stopping Metrics container: {}".format(str(e)))

        print("Stopping Montagu...({}: {})".format(
            self.settings["instance_name"], self.settings["docker_prefix"]),
              flush=True)
        # always remove the static container
        try:
            self.static.remove(force=True)
        except docker.errors.NotFound:
            pass
        compose.stop(self.settings)
        print("Wiping static file volume")
        try:
            static_volume = self.client.volumes.get(self.volume_name("static"))
            static_volume.remove(force=True)
        except docker.errors.NotFound:
            return None
        if not self.settings["persist_data"]:
            for v in self.volumes:
                name = self.volume_name(v)
                try:
                    self.client.volumes.get(name).remove(force=True)
                except docker.errors.NotFound:
                    pass

    def pull(self):
        print("Pulling images for Montagu", flush=True)
        compose.pull(self.settings)

    def start(self):
        print("Starting Montagu...", flush=True)
        compose.start(self.settings)
        print("- Checking Montagu has started successfully")
        sleep(2)
        if self.status != "running":
            raise Exception("Failed to start Montagu. Service status is {}".format(self.status))

__all__ = ["MontaguService"]
