from subprocess import run, DEVNULL

from setting_definitions.boolean import BooleanSettingDefinition
from setting_definitions.definition import SettingDefinition
from setting_definitions.enum import EnumSettingDefinition

teamcity_sources = ["test_data", "legacy"]

## NOTE: This duplicates the code in backup.py in order to break a
## circular dependency.  It would be good to factor that out but I
## can't see a really obvious decent spot for it.
def backup_needs_setup():
    return run("../backup/needs-setup.sh", stdout=DEVNULL, stderr=DEVNULL).returncode == 1

def vault_required(settings):
    data_source = settings["initial_data_source"]
    uses_duplicati = settings["backup"] is True or data_source == "restore"
    uses_vault_passwords = settings["password_group"] is not None and \
                           settings['password_group'] != "fake"
    return data_source in teamcity_sources \
           or (uses_duplicati and backup_needs_setup()) \
           or settings["certificate"] == "production" \
           or settings["certificate"] == "support" \
           or uses_vault_passwords \
           or settings["db_annex_type"] != "fake" \
           or settings["notify_channel"] \
           or ("clone_reports" in settings and settings["clone_reports"] is True)


definitions = [
    BooleanSettingDefinition("persist_data",
                             "Should data in the database be persisted?",
                             "If you answer no all data will be deleted from the database when Montagu is stopped. Data"
                             " should be persisted for live systems, and not persisted for testing systems.",
                             default_value=True),
    BooleanSettingDefinition("backup",
                             "Should data be backed up remotely?",
                             "This should be enabled for the production environment.",
                             default_value=True),
    EnumSettingDefinition("initial_data_source",
                          "What data should be imported initially?",
                          [
                              ("minimal", "Minimum required for Montagu to work (this includes enum tables and "
                                          "permissions)"),
                              ("test_data", "Fake data, useful for testing"),
                              ("legacy", "Imported data from SDF versions 6, 7, 8 and 12"),
                              ("restore", "Restore from backup")
                          ],
                          default_value="restore"),
    SettingDefinition("backup_bucket",
                      "Which S3 bucket should be used for backup?",
                      "This is where data will be restored from, if you specified that a restore should happen for the"
                      "initial data import, and it's where data will be backed up to if you enabled backups.",
                      default_value="montagu-live",
                      is_required=lambda x: x["backup"] is True or x["initial_data_source"] == "restore"),
    BooleanSettingDefinition("open_browser",
                             "Open the browser after deployment?",
                             "If you answer yes, Montagu will be opened after deployment",
                             default_value=True),
    SettingDefinition("port",
                      "What port should Montagu listen on?",
                      "Note that this port must be the one that users browsers will be connecting to. In other words, "
                      "if there is another layer wrapping around Montagu (e.g. if it is being deployed to a VM) the "
                      "real port exposed on the physical machine must agree with the port you choose now.",
                      default_value=443),
    SettingDefinition("port_db",
                      "What port should the database listen on?",
                      default_value=6543),
    SettingDefinition("hostname",
                      "What hostname is Montagu being accessed as?",
                      "This hostname should match the SSL certificate. Likely values:"
                      "\n- localhost (for local dev)"
                      "\n- support.montagu.dide.ic.ac.uk (for stage)"
                      "\n- montagu.vaccineimpact.org (for production)"
                      ),
    EnumSettingDefinition("certificate",
                          "What SSL certificate should Montagu use?",
                          [
                              ("self_signed", "Use the non-secure self-signed certificate in the repository"),
                              ("self_signed_fresh", "Generate a new, non-secure self-signed certificate every deploy"),
                              ("production", "Certificate for montagu.vaccineimpact.org"),
                              ("support", "Certificate for support.montagu.dide.ic.ac.uk")
                          ]
                          ),
    EnumSettingDefinition("password_group",
                          "Which password group should montagu use to retrieve database passwords from the vault?",
                          [
                              ("production", "Passwords for production"),
                              ("science",    "Passwords for science"),
                              ("fake",       "Do not use passwords from the vault")
                          ]
                          ),
    EnumSettingDefinition("db_annex_type",
                          "How do we treat the annex database?",
                          [
                              ("fake", "Add a totally safe, but empty, version to the constellation"),
                              ("readonly", "Read-only access to the real annex"),
                              ("real", "Full access to the real annex: PRODUCTION ONLY")
                          ]),
    SettingDefinition("notify_channel",
                      "What slack channel should we post in?",
                      "e.g., montagu. Leave as the empty string to not post",
                      default_value=""),
    BooleanSettingDefinition("clone_reports",
                             "Should montagu-reports be cloned?",
                             "If you answer yes, then we need vault access in order to get the ssh keys for vimc-robot "
                             "If you answer no, then we set up only an empty orderly repository, and you will not be "
                             "able to clone the reports repository",
                             default_value=True),
    SettingDefinition("vault_address",
                      "What is the address of the vault?",
                      "If you have a local vault instance for testing, you probably want http://127.0.0.1:8200.\n"
                      "Otherwise, just use the default",
                      default_value="https://support.montagu.dide.ic.ac.uk:8200",
                      is_required=vault_required),

    SettingDefinition("instance_name",
                      "What is the name of this instance?",
                      default_value="(unknown)"),
    SettingDefinition("docker_prefix",
                      "What docker prefix name should we use?  Leave this as "
                      "'montagu' for the primary deployment on a machine and "
                      "set to an alternative value if you want to run multiple "
                      "copies simultaneously.",
                      default_value="montagu"),

    BooleanSettingDefinition("require_clean_git",
                             "Should we require a clean git state?",
                             "If you answer yes, then we require that git is 'clean' (no untracked or modified files) "
                             "and tagged before deploying.  This is the desired setting on production machines, but "
                             "will be annoying for development",
                             default_value=False),
    BooleanSettingDefinition("add_test_user",
                             "Should we add a test user with access to all modelling groups?",
                             "This must set to False on production!",
                             default_value=False)
]
