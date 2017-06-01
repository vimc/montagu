# Things that affect the Montagu deployment process
* Is Montagu already present and running on the machine? If no, we need to make 
  some decisions:
  - Should the DB be persisted to a data volume, or should it be removed when
    Montagu stops running?
  - What data should be imported on start up?
    + Absolutely none (this will rarely be useful)
    + The minimal set required for Montagu to work: this is just the enum 
      tables like "touchstone_status", as well as the built in roles and 
      permissions
    + A fuller test data set. This doesn't include any real data, but has 
      everything you need to do manual testing/demonstration
    + The legacy data
    + A backup of a live Montagu data, from a previous installation on a
      different machine
* What certificate should the API use for SSL?
  + A new, generated-on-the-spot, self-signed certificate
  + The real certificate, in which case the deployment script needs to:
    1. Fetch the private key from the vault
    2. Generate a CSR
    3. Automatically obtain a signed certificate from Let's Encrypt

# Interactive vs config
I suggest that when you first run the deploy script you are prompted for answers
to the questions above, and we then store these in a config file. Future runs
would read the answers back out.

The script would revert to interactive if there are new config options that need
to be set, relative to a previous build.

There will probably always be an interactive aspect, so that we can prompt for
a passphrase to unlock secrets in the vault.

# Config file
Maybe just use a simple Java properties file. Here's an example for a live 
system:

    persist_data=true
    api_certificate=real

And here's one for a UAT machine:

    persist_data=false
    api_certificate=self-signed

# Process
Here's what the deployment process will do:

1. Compare `montagu.config` file (if it exists) with in-memory config model. If
   there is anything missing from the config file, interactively walk the user 
   through providing values and then save them to the config file.
2. If Montagu is running, stop it by running `docker-compose down`
3. Backup "things"
4. Set up a new persistent data volume if this is a new installation and the 
   `persist_data` setting is `true`.
5. Generate new database passwords and set them for the database users.
6. Run any database schema migrations.
7. Pull latest images and start new constellation with docker-compose. 
8. If this is a new installation, import data
9. Push new database password to the API container
10. Generate/obtain certificate and copy it into the API container

## Generate new database passwords
We should enable password-less login for the root user to the database on local
connections. This allows us to throw away all the live system passwords every
time we tear down and spin up Montagu. Rather than hanging on to them (which
complicates security) we generate new random passwords during the deployment
process. The deploy script keeps these in memory and distributes them to the 
containers. When the script is over, the passwords vanish from memory and only
exist in the containers that need them.

### List of database user/passwords pairs needed:
* api: Used by the API. Has wide-ranging permissions for insert, update, and 
  delete, but cannot alter schema
* schema_migrator: Used by the schema migrations. Can add, alter and drop 
  tables.

## Import data
A quick reminder of the data sets discussed above: empty, minimal, test data,
legacy, restore from backup.

* "Empty" just means doing nothing. 
* "Minimal" and "Test data" can just be SQL files, either stored directly in the 
  deployment repository, alongside the deployment script, or obtained from 
  TeamCity build artefacts.
* "Legacy" - I'm not sure what the state of the art on this is.
* Back up. A backup might just be another SQL file, or it might be a more 
  efficient file format. We haven't figured out our backup mechanism yet, so 
  it's hard to be sure how we'd fetch this.

## Push new password to API container
I plan (I haven't done it yet) to make the API check 
/etc/montagu/api/config.properties for additional runtime settings that override
the defaults (which live as a resource inside the JAR).

So this would be a matter of creating a new properties file with:

    db.password=LONG_RANDOM_STRING

and copying it into the container.

## Certificate
### Self-signed
I have this working in the Blackbox Tests for the API. I have a couple of Bash 
scripts which use Java's keytool (so they will need to run in a container with
Java) to generate a certificate and copy it into the API container.
