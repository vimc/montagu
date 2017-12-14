from time import sleep

import docker

import compose

api_name = "montagu_api_1"
reporting_api_name = "montagu_reporting_api_1"
db_name = "montagu_db_1"
contrib_name = "montagu_contrib_1"
admin_portal_name = "montagu_admin_1"
report_portal_name = "montagu_report_1"
proxy_portal_name = "montagu_proxy_1"
orderly_name = "montagu_orderly_1"

volume_name = "montagu_db_volume"
orderly_volume_name = "montagu_orderly_volume"
template_volume_name="montagu_template_volume"
network_name = "montagu_default"

db_annex_name = "montagu_db_annex_1"

service_names = {
    api_name,
    reporting_api_name,
    db_name,
    contrib_name,
    admin_portal_name,
    report_portal_name,
    proxy_portal_name,
    orderly_name
}


# TODO: more medium term it would feel less weird to initialise this
# object with a 'settings' object so that the annex bit can be done
# more tidily.  But this is pulled into the other modules as "from
# service import service" so that's not going to directly work!
#
# However, this is actually really hard to do correctly - even passing
# 'settings' through as an argument to status() is hard because it's
# used to _load_ the settings and confirm that all settings are filled
# out appropriately!
class MontaguService:
    def __init__(self):
        self.client = docker.from_env()

    @property
    def status(self):
        expected = service_names
        # Always tolerate the annex
        expected = expected.union({db_annex_name})

        actual = dict((c.name, c) for c in self.client.containers.list(all=True))
        unexpected = list(x for x in actual.keys() - expected if "montagu" in x.lower())
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
        return volume_name in [v.name for v in self.client.volumes.list()]

    def _get(self, name):
        return next((x for x in self.client.containers.list() if x.name == name), None)

    def stop(self, settings):
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
        use_fake_db_annex = settings["db_annex_type"] == "fake"
        compose.stop(settings["port"], settings["hostname"],
                     persist_volumes=settings["persist_data"],
                     use_fake_db_annex=use_fake_db_annex)

    def start(self, settings):
        print("Starting Montagu...", flush=True)
        compose.pull(settings['port'], settings['hostname'])
        use_fake_db_annex = settings["db_annex_type"] == "fake"
        compose.start(settings['port'], settings['hostname'], use_fake_db_annex)
        print("- Checking Montagu has started successfully")
        sleep(2)
        if service.status != "running":
            raise Exception("Failed to start Montagu. Service status is {}".format(service.status))


service = MontaguService()
