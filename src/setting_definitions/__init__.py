from setting_definitions.boolean import BooleanSettingDefinition
from setting_definitions.definition import SettingDefinition
from setting_definitions.enum import EnumSettingDefinition


def vault_required(settings):
    return settings["initial_data_source"] != "minimal" \
           or settings["backup"] is True \
           or settings["certificate"] == "production" \
           or settings["certificate"] == "support" \
           or settings["use_real_passwords"] \
           or settings["clone_reports"] is True

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
    BooleanSettingDefinition("use_real_passwords",
                             "Should real, secure passwords be used?",
                             "This affects database user accounts, and is also necessary for Montagu to be able to "
                             "send emails. In testing environments you can answer 'no'. This will mean that:"
                             "\n- The root db user has the default password 'changeme' "
                             "\n- Other db users will have the same password as their username."
                             "\n- Emails will be written to disk (/tmp/montagu_emails) instead of being sent",
                             default_value=True),
    SettingDefinition("vault_address",
                      "What is the address of the vault?",
                      "If you have a local vault instance for testing, you probably want http://127.0.0.1:8200.\n"
                      "Otherwise, just use the default",
                      default_value="https://support.montagu.dide.ic.ac.uk:8200",
                      is_required=vault_required),
    BooleanSettingDefinition("clone_reports",
                             "Should montagu-reports be cloned?",
                             "If you answer yes, then we need vault access in order to get the ssh keys for vimc-robot "
                             "If you answer no, then we set up only an empty orderly repository, and you will not be "
                             "able to clone the reports repository",
                             default_value=True),
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
