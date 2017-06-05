import docker
import compose

api_name = "montagu_api_1"
db_name = "montagu_db_1"

service_names = {
    api_name,
    db_name,
    "montagu_contrib_1"
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
            status_map = dict((c, c.status) for c in services)
            raise Exception("Montagu service is in a indeterminate state. "
                            "Manual intervention is required.\nStatus: {}".format(status_map))

    @property
    def api(self):
        return self._get(api_name)

    @property
    def db(self):
        return self._get(db_name)

    def _get(self, name):
        return next((x for x in self.client.containers.list() if x.name == name), None)

    def stop(self):
        print("Stopping Montagu...", flush=True)
        compose.stop()

    def start(self):
        print("Starting Montagu...", flush=True)
        compose.start()


service = MontaguService()
