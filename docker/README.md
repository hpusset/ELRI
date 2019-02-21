ELRI National Relay Station Docker Images
=================================================================

Introduction
------------

Docker image provisioning of the project composed by the next components:

- Postgres server image for the database requirement
- NRS image for the metashare application requirement (based on the metashare and project_management directories in main structure)
- Solr image for the indexing component requirement (based on the solr directory in main structure)
- NGINX image for the web server requirement and managing custom rules to the NRS application
- Toolchain image for the toolchain requirement

Requirements
------------

### Recommended

01. Docker CE (Community Edition) version 18.09.0 or above [Install Link](https://docs.docker.com/v17.12/install/#server)

02. Docker-compose version 1.23.1 or above [Install Link](https://docs.docker.com/compose/install)

03. Docker user (unprivileged) in docker group:
```
Example user elri:
$ useradd --shell /bin/false --expiredate 1 elri # No login and no shell user for automation purposes (e.g. start docker containers)
$ usermod -a -G docker elri # Add user to the docker group to allow interaction with docker
```

### Minimum

- Docker CE (Community Edition) version 17.12.0

Setup
-----

## Development

In order to set up a minimal working development version of the platform, the
following steps need to be undertaken with the user created with the purpose of managing docker containers:

01. Checkout `compose` directory from this project

02. Merge `docker-compose-runner.yml` and `docker-compose-runner-dev.yml` files:

```        
$ docker-compose -f docker-compose-runner.yml -f docker-compose-runner-dev.yml config > docker-compose.yml
```

03. Change the following property files to match the destination country requirements:

### db_secret.properties:

Property          | Default value     | Description
-------------     | -------------     | -------------
DBELRI_USER       | elri_user         | ELRI database user
DBELRI_PASS       | elri_pass         | ELRI database pass
DBELRI_NAME       | elri_metashare_db | ELRI database name
POSTGRES_USER     | root              | ELRI database root user
POSTGRES_PASSWORD | rootpass          | ELRI database root pass

### nrs_secret.properties:

Property           | Default value                   | Description
-------------      | -------------                   | -------------
ELRI_TIMEZONE      | Europe/Lisbon                   | ELRI country timezone
ELRI_LANGUAGE      | pt-pt*                          | ELRI country language code
ELRI_SALT          | e07fc77c1ec(...)                | ELRI salt used with encryption
ELRI_ALERT_MAILS   | elri-nrs-support@vicomtech.org  | ELRI alert mails 'from' field
ELRI_COUNTRY       | Portugal                        | ELRI country value
ELRI_EMAIL_TLS     | True                            | ELRI Mail server TLS usage
ELRI_EMAIL_HOST    | elri_mailserver                 | ELRI Mail server hostname
ELRI_EMAIL_PORT    | 1025                            | ELRI Mail server port
ELRI_EMAIL_USER    | elri_noreply_user@smtserver.com | ELRI Mail server auth user (if exists)
ELRI_EMAIL_PASS    | xxxxxxxx                        | ELRI Mail server auth password (if exists)
ELRI_SUP_LANGUAGES | [("English", "English"),(...)]  | ELRI Supported languages
ELRI_WORKERS       | 4                               | Number of workers used
ELRI_THREADS       | 8                               | Number of threads used

```
* Countries:
    es-es (Spanish)
    en-ie (English)
    fr-fr (French)
    ga-ie (Gaelic)
    pt-pt (Portuguese)

```

### web_secret.properties:

Property          | Default value     | Description
-------------     | -------------     | -------------
ELRI_HOSTNAME     | dev               | ELRI hostname
ELRI_DOMAINNAME   | elri-nrs.eu       | ELRI domain name
ELRI_PROTOCOL     | http              | General protocol used by the web server (when Nginx is in charge of SSL offloading)

04. Start the project:

```
$ docker-compose up
```

05. Super user creation for application login:

```
$ docker exec -ti elri_app /elri/create_super_user.sh
```

## Production

In order to set up a minimal working production version of the platform, the
following steps need to be undertaken:

01. Create OS users:

```
$ useradd --shell /bin/false --uid 8283 --no-create-home --expiredate 1 django # No login and no shell user to match postgres-server container user
$ useradd --shell /bin/false --uid 6263 --no-create-home --expiredate 1 postgres # No login and no shell user to match django container user
$ useradd --shell /bin/false --uid 7273 --no-create-home --expiredate 1 solr # No login and no shell user to match solr container user
```

02. Execute the development procedure above replacing `docker-compose-runner-dev.yml` with `docker-compose-runner-prd.yml` in step `02`

03. Start the project in detached mode:

```
$ docker-compose up -d
```

04. (Optional) To allow SSL termination at the Nginx Web Server:

* Stop the project:

```
$ docker-compose down
```

* Uncomment docker-compose-runner-prd.yml entries identified by the comment:

```
# Uncomment if using SSL termination at nginx server
```

* Change `ELRI_PROTOCOL` value from `http` to `https` at `web_secret.properties` file

* Merge the files `docker-compose-runner-prd.yml` and  `docker-compose-runner.yml` again

* (If certificate is a chain file) Concatenate your primary certificate file (your_domain_name.crt) and the intermediate certificate chain file (DigiCertCA.crt) into a single .pem file:

```
cat your_domain_name.crt DigiCertCA.crt > server.crt
```

For more information:
https://www.digicert.com/csr-ssl-installation/nginx-openssl.htm#ssl_certificate_install

* Update certificate and key:

File          | Destination                             | Description
------------- | -------------                           | -------------
server.crt    | /var/lib/docker/volumes/web-certs/_data | Valid registered Certificate for `ELRI_HOSTNAME`.`ELRI_DOMAINNAME`
server.key    | /var/lib/docker/volumes/web-keys/_data  | Valid registered Certificate key `ELRI_HOSTNAME`.`ELRI_DOMAINNAME`

* Start the project in detached mode:

```
$ docker-compose up -d
```

Testing
-----

- Open a web browser and check the url composed by the variables set in `ELRI_HOSTNAME` and `ELRI_DOMAINNAME` like the example below:

```
http://dev.elri-nrs.eu
```

**Note:** If testing locally and there is no DNS configured for the url above, it can be set in /etc/hosts file to point to `localhost` like the example below:

```
$ vi /etc/hosts
127.0.0.1	localhost dev.elri-nrs.eu
```

- Accessing mail server web page (to check if e-mails are being sent):

```
http://localhost:8025
```

- If needed, database and all other persisted data can be deleted with the following command:

```
$ docker-compose down --volumes
```

- If needed, docker images can be deleted with the following command:

```
$ docker-compose down --rmi all
```

Maintenance
-----

In production environment the following steps are suggested for persisted data safety :

- Backup:

01. Shutdown all containers:

```
$ docker-compose stop
```

02. Backup the volumes that are used for filesystem persisted data:

Volume Name   | Location                             | Description
------------- | -------------                        | -------------
elri-storage  | /var/lib/docker/volumes/elri_storage | Local storage layer path used for persistent object storage
elri-certs    | /var/lib/docker/volumes/elri-certs   | Used when AP configuration exists
web-certs     | /var/lib/docker/volumes/web-certs    | Certificates used by the webserver
web-keys      | /var/lib/docker/volumes/web-keys     | Keys used by the webserver
elri-shared   | /var/lib/docker/volumes/elri-shared  | elri_resources shared by the toolchain and the metashare app
elri-db       | /var/lib/docker/volumes/elri-db      | Postgres database data

03. Startup all containers

```
$ docker-compose start
```

Reminders
-----

01. Need to change files in GIT when not building images in MASTER branch:

File                              | Property             | Description
-------------                     | -------------        | -------------
compose/docker-compose-runner.yml | image (each service) | Replace `MASTER` for the desired release

To do:
-----

- [X] Toolchain integration
- [X] E-mail server configuration (R1.2)
- [ ] Auto configure release name at the Dockerfile/docker-compose-runner.yml files
- [X] Mail service to recieve mails only (mailhog, for testing purposes), for sending e-mails it is preferred to use a e-mail relay service (e.g. google, as it is free of charge)
- [X] Nginx SSL support (R1.1)