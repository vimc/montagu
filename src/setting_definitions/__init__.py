from subprocess import run, DEVNULL

from setting_definitions.boolean import BooleanSettingDefinition
from setting_definitions.definition import SettingDefinition
from setting_definitions.enum import EnumSettingDefinition

def vault_required(settings):
    data_source = settings["initial_data_source"]
    uses_bb8 = settings["bb8_backup"] is True or data_source == "bb8_restore"
    uses_vault_passwords = settings["password_group"] is not None and \
                           settings['password_group'] != "fake"
    return settings["copy_static_files"] is True \
           or uses_bb8 \
           or settings["certificate"] == "production" \
           or settings["certificate"] == "support" \
           or uses_vault_passwords \
           or settings["notify_channel"]


definitions = [
    BooleanSettingDefinition("persist_data",
                             "Should data in the database be persisted?",
                             "If you answer no all data will be deleted from the database when Montagu is stopped. Data"
                             " should be persisted for live systems, and not persisted for testing systems.",
                             default_value=True),
    BooleanSettingDefinition("bb8_backup",
                             "Should data be backed up remotely using BB8?",
                             "This should be enabled for the production "
                             "environment.",
                             default_value=True),
    EnumSettingDefinition("initial_data_source",
                          "What data should be imported initially?",
                          [
                              ("minimal", "Minimum required for Montagu to "
                                          "work (this includes enum tables and "
                                          "permissions)"),
                              ("test_data", "Fake data, useful for testing"),
                              ("legacy", "Imported data from SDF versions 6, 7, 8 and 12"),
                              ("bb8_restore", "Restore from BB8 backup")
                          ],
                          default_value="restore"),
    BooleanSettingDefinition("update_on_deploy",
                             "Should data be updated on deploy?",
                             "Only has an effect if 'persist_data' is true, "
                             "'bb8_backup' is false and "
                             "'initial_data_source' is 'bb8_restore'",
                             default_value=False),
    BooleanSettingDefinition("open_browser",
                             "Open the browser after deployment?",
                             "If you answer yes, Montagu will be opened after deployment",
                             default_value=False),
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
                      "\n- montagu.vaccineimpact.org (for production)",
                      default_value="localhost"),
    SettingDefinition("orderly_web_api_url",
                        "What is the URL of the OrderlyWeb api, used to coordinate adding users to both Montagu and OrderlyWeb? ",
                        "Likely values:"
                        "\n http://localhost:8888/api/v1 (for local dev)"
                        "\n https://support.montagu.dide.ic.ac.uk:10443/reports/api/v1 (for UAT)"
                        "\n https://support.montagu.dide.ic.ac.uk:11443/reports/api/v1 (for Science)"
                        "\n https://montagu.vaccineimpact.org/reports/api/v1 (for Production)",
                        default_value="http://localhost:8888/api/v1"),
    EnumSettingDefinition("certificate",
                          "What SSL certificate should Montagu use?",
                          [
                              ("self_signed", "Use the non-secure self-signed certificate in the repository"),
                              ("self_signed_fresh", "Generate a new, non-secure self-signed certificate every deploy"),
                              ("production", "Certificate for montagu.vaccineimpact.org"),
                              ("support", "Certificate for support.montagu.dide.ic.ac.uk")
                          ],
                          default_value="self_signed"),
    EnumSettingDefinition("password_group",
                          "Which password group should montagu use to retrieve database passwords from the vault?",
                          [
                              ("production", "Passwords for production"),
                              ("science", "Passwords for science"),
                              ("fake", "Do not use passwords from the vault")
                          ],
                          default_value="fake"),
    SettingDefinition("notify_channel",
                      "What slack channel should we post in?",
                      "e.g., montagu. Leave as the empty string to not post",
                      default_value=""),
    BooleanSettingDefinition("copy_static_files",
                             "Should we copy configured static files from "
                             "into the static server container?",
                             "This can only be true if data source is restore",
                             default_value=False),
    SettingDefinition("vault_address",
                      "What is the address of the vault?",
                      "If you have a local vault instance for testing, you probably want http://127.0.0.1:8200.\n"
                      "Otherwise, just use the default",
                      default_value="https://support.montagu.dide.ic.ac.uk:8200",
                      is_required=vault_required),

    SettingDefinition("instance_name",
                      "What is the name of this instance?",
                      default_value="(unknown)"),

    BooleanSettingDefinition("require_clean_git",
                             "Should we require a clean git state?",
                             "If you answer yes, then we require that git is 'clean' (no untracked or modified files) "
                             "and tagged before deploying.  This is the desired setting on production machines, but "
                             "will be annoying for development",
                             default_value=False),
    BooleanSettingDefinition("enable_db_replication",
                             "Should we enable database replication for streaming backups to the annex?",
                             "Only needed on production, or for testing the backup",
                             default_value=False),
    BooleanSettingDefinition("add_test_user",
                             "Should we add a test user with access to all modelling groups?",
                             "This must set to False on production!",
                             default_value=False),
    BooleanSettingDefinition("include_guidance_reports",
                             "Should we copy guidance reports from "
                             "orderly into the contrib portal container?",
                             "This can only be true if data source is restore",
                             default_value=False),
    BooleanSettingDefinition("use_production_db_config",
                             "Should we use the high-performance database "
                             "config?",
                             "This uses more memory",
                             default_value=False),
    BooleanSettingDefinition("use_real_diagnostic_reports",
                             "Should we run the real diagnostic reports when a burden estimate set is fully uploaded?",
                             "This can be true on UAT, Science and Production.",
                             default_value=False),
    BooleanSettingDefinition("email_burden_estimate_uploader",
                             "Should we send diagnostic reports to uploaders of burden estimates?",
                             "This should be false until we're confident that the reports are being correctly generated.",
                             default_value=False),
    BooleanSettingDefinition("fake_smtp",
                              "Should we add a fake smtp server for notification emails?",
                              "This should be true on all environments except Production.",
                              default_value=True)
]
