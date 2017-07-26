from time import sleep

import docker

import compose

api_name = "montagu_api_1"
db_name = "montagu_db_1"
contrib_name = "montagu_contrib_1"
admin_name = "montagu_admin_1"
proxy_name = "montagu_proxy_1"

volume_name = "montagu_db_volume"

service_names = {
    api_name,
    db_name,
    contrib_name,
    admin_name,
    proxy_name
}


class MontaguService:
    def __init__(self):
        self.client = docker.from_env()

    @property
    def status(self):
        actual = dict((c.name, c) for c in self.client.containers.list(all=True))
        unexpected = list(x for x in actual.keys() - service_names if "montagu" in x.lower())
        if any(unexpected):
            raise Exception("There are unexpected Montagu-related containers running: {}".format(unexpected))

        services = list(c for c in actual.values() if c.name in service_names)
        statuses = set(c.status for c in services)

        if len(statuses) == 1:
            return statuses.pop()
        elif len(statuses) == 0:
            return None
        else:
            status_map = dict((c.name, c.status) for c in services)
            raise Exception("Montagu service is in a indeterminate state. "
                            "Manual intervention is required.\nStatus: {}".format(status_map))

    @property
    def api(self):
        return self._get(api_name)

    @property
    def db(self):
        return self._get(db_name)

    @property
    def contrib(self):
        return self._get(contrib_name)

    @property
    def admin(self):
        return self._get(admin_name)

    @property
    def proxy(self):
        return self._get(proxy_name)

    @property
    def volume_present(self):
        return volume_name in [v.name for v in self.client.volumes.list()]

    def _get(self, name):
        return next((x for x in self.client.containers.list() if x.name == name), None)

    def stop(self, port, hostname, persist_volumes):
        print("Stopping Montagu...", flush=True)
        compose.stop(port, hostname, persist_volumes)

    def start(self, port, hostname):
        print("Starting Montagu...", flush=True)
        compose.start(port, hostname)
        print("- Checking Montagu has started successfully")
        sleep(2)
        if service.status != "running":
            raise Exception("Failed to start Montagu. Service status is {}".format(service.status))


service = MontaguService()
