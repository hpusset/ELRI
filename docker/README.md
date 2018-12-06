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

- Docker CE (Community Edition) version 18.09.0 or above [Install Link](https://docs.docker.com/v17.12/install/#server)
- Docker-compose version 1.23.1 or above [Install Link](https://docs.docker.com/compose/install)

### Minimum

- Docker CE (Community Edition) version 17.12.0

Setup
-----

## Development

In order to set up a minimal working development version of the platform, the
following steps need to be undertaken:

01. Checkout `compose` directory to the desired location

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

Property          | Default value     | Description
-------------     | -------------     | -------------
ELRI_TIMEZONE     | Europe/Lisbon     | ELRI country timezone
ELRI_LANGUAGE     | pt-pt             | ELRI country language code
ELRI_SALT         | e07fc77c1ec(...)  | ELRI salt used with encryption
ELRI_ALERT_MAILS  | noreply@elri.com  | ELRI alert mails 'from' field
ELRI_COUNTRY      | Portugal          | ELRI country value
ELRI_EMAIL_TLS    | True              | ELRI Mail server TLS usage
ELRI_EMAIL_HOST   | elri_mailserver   | ELRI Mail server hostname
ELRI_EMAIL_PORT   | 1025              | ELRI Mail server port
ELRI_EMAIL_USER   | ''                | ELRI Mail server auth user (if exists)
ELRI_EMAIL_PASS   | ''                | ELRI Mail server auth password (if exists)

### web_secret.properties:

Property          | Default value     | Description
-------------     | -------------     | -------------
ELRI_HOSTNAME     | nrs               | ELRI hostname
ELRI_DOMAINNAME   | dev.elri.com      | ELRI domain name

04. Start the project:

```
$ docker-compose up
```

05. (Optional) Super user creation for application login:

```
$ docker exec -ti elri_app /elri/create_super_user.sh
```

## Production

In order to set up the production environment we just need to replace in the development procedure above `docker-compose-runner-dev.yml` with `docker-compose-runner-prd.yml`

Testing
-----

01. After starting up the project we can open a web browser and check the url composed by the variables set in `ELRI_HOSTNAME` and `ELRI_DOMAINNAME` like the example below:

```
http://nrs.dev.elri.com
```

**Note:** If testing locally and there is no DNS configured for the url above, it can be set in /etc/hosts file to point to `localhost` like the example below:

```
$ vi /etc/hosts
127.0.0.1	localhost nrs.dev.elri.com
```

02. Accessing mail server web page (to check if e-mails are being sent):

```
http://localhost:8025
```

Reminders
-----

01. Need to change files in GIT when not building images in MASTER branch:

File                              | Property             | Description
-------------                     | -------------        | -------------
django/Dockerfile                 | GIT_URL              | Replace `trunk` for the desired release
solr/Dockerfile                   | GIT_URL              | Replace `trunk` for the desired release
compose/docker-compose-runner.yml | image (each service) | Replace ` MASTER` for the desired release

02. Docker volumes that are created with project content:
- `elri-shared-resources` : Shared resources between `elri_app` and `elri_toolchain` checked out from GIT `elri_resources` directory

To do:
-----

- [X] Toolchain integration
- [X] E-mail server configuration (R1.2)