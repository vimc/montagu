import docker
import compose

api_name = "montagu_api_1"

service_names = {
    api_name,
    "montagu_db_1",
    "montagu_contrib_1"
}


class MontaguService:
    def __init__(self):
        self.client = docker.from_env()

    @property
    def is_running(self):
        running = set(c.name for c in self.client.containers.list())
        services = dict((name, name in running) for name in service_names)

        unexpected = list(x for x in running - service_names if "montagu" in x.lower())
        if any(unexpected):
            raise Exception("There are unexpected Montagu-related containers running: {}".format(unexpected))

        if all(services.values()):
            return True
        elif not any(services.values()):
            return False
        else:
            raise Exception("Montagu service is in a indeterminate state - only some containers are up."
                            "Manual intervention is required. Status: {}".format(services))

    @property
    def api(self):
        return next((x for x in self.client.containers.list() if x.name == api_name), None)

    def stop(self):
        print("Stopping Montagu...", flush=True)
        compose.stop()

    def start(self):
        print("Starting Montagu...", flush=True)
        compose.start()


def get_service():
    return MontaguService()
