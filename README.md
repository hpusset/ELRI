ELRI National Relay Station (forked from the ELRC-SHARE SOFTWARE)
=================================================================

Introduction
------------

This code base is a fork of the [ELRC-SHARE](http://elrc-share.eu)
[software](https://github.com/MiltosD/ELRC2), itself a fork of the
[META-SHARE](http://www.meta-share.org/)
[software](https://github.com/metashare/META-SHARE).


With respect to the ELRC-SHARE, the ELRI National Relay Station (NRS) software
will integrate, among other things:

- group-based policy management,
- automatic language resource processing toolchain integration
- manual quality control workflow elements.

Requirements
------------

- Java 8

Setup
-----

In order to set up a minimal working development version of the platform, the
following steps need to be undertaken:

01. Copy `metashare/local_settings.sample` to `metashare/local_settings.py` and
    change the local_settings accordingly.

02. Set up a Python 2 virtualenv

        virtualenv venv

    activate it

        source venv/bin/activate

    and install the dependencies via

        pip install -r requirements.txt

    Check the version for `psycopg2` in the requirements file. You may need to
    use `psycopg2==2.7`.
    Check if `flup` is also in the requirements file. It may be needed.

03. Launch Solr by `cd`-ing in the `solr/` folder and doing

        java -jar -Djetty.port=chosen_port start.jar

    Make sure to update the `SOLR_URL` and `TESTING_SOLR_URL` environment
    variables in `metashare/local_settings.py` accordingly.

04. Set up a PostgreSQL database and provide relevant information to the
    relevant `local_settings.py` section, this is updating the `DATABASES`
    variable.

    4.1. Install `postgresql`

        sudo apt install postgresql postgresql-contrib

    4.2. Change `postgresql` access mode to create new database(s) and user(s).
         Edit the `pb_hba.conf` file by using the editor of your choice.
         The file `pg_hba.conf` will most likely be at
         /etc/postgresql/9.x/main/pg_hba.conf or
         /etc/postgresql/10/main/pg_hba.conf

        ```
        sudo <editor> /etc/postgresql/10/main/pg_hba.conf
        #Database administrative login by Unix domain socket
        #local all postgres peer
        local all postgres trust
        # Database administrative login by Unix domain socket
        #local  all             all                                     peer
        local   all             all                                     md5
        # Allow replication connections from localhost, by a user with the
        # replication privilege.  
        #local  replication     all                                     peer
        local   replication     all                                     md5
        ```

    And restart the `postgresql` service

        ```
        sudo service postgresql restart
        ```
    4.3. Create a user and assign to it a password. The one you will add to the
         `local_settings.py` file.

        ```
        psql -u postgres
        postgres=# create role your_user;
        postgres=# alter user your_user with encrypted password 'yourPassword' ;
        ```

         and allow this user to login to the psql service:

        ```
        createdb -U postgres your_user
        psql -U postgres
        postgres=# grant all privileges on database your_user to your_user ;
        postgres=# ALTER ROLE "your_user" WITH LOGIN;
        ```

    At this point, you will be able to login with your user doing `psql -U
    your_user`.

    4.4. Create a database. The one you will add to the `local_settings.py`
         file. And grant permissions to the user you created before.

        ```
        createdb -U postgres your_metashare_db
        psql -U postgres
        postgres=# grant all privileges on database your_metashare_db to \
        your_user ;
        ```

    If you have allowed the login for the `your_user` user, you will be able to
    login on the `your_metashare_db` data base by doing

        ```
        psql -U your_user your_metashare_db
        ```

    4.5. Check the `postgresql` service port:

        ```
        sudo netstat -nl | grep postgres
        unix  2      [ ACC ]     STREAM     LISTENING     186337   /var/run/postgresql/.s.PGSQL.5433
        ```

    and check the `PORT` field in the `DATABASES` variable of the
    `local_settings.py`, in this case it should be `5433`.


05. Generate migrations for the relevant apps by doing a

        python manage.py makemigrations accounts repository stats \
        recommendations storage

06. Do a

        python manage.py migrate

    to set up the DB schema.

07. Do a

        python manage.py rebuild_index

    to set up the Solr index.

08. Create the directories `metashare/unprocessed` and `metashare/processed`.

09. Create the file `metashare/maintainers.dat`, which should have the following
    format:

    Country_name:maintainer_user_name_1,user_name_2,...

    for each authorised country_name/maintainer_user_name in the system.

10. Create the folder specified in the `STATIC_ROOT` `metashare/local_settings.py`
    environment variable and run

        python manage.py collectstatic

    to collect all static files to the STATIC_ROOT directory.

11. Create a superuser so that one can log in to the application:

        python manage.py createsuperuser

    and follow the instructions.

12. Add to the `local_settings.py` the list of `ALLOWED_HOSTS` from which the
    webapp will be available:

        ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

    Should you need to access the development server from remote machines, you
    need to set up `ALLOWED_HOSTS` to accept connections from any host:

        ALLOWED_HOSTS = ["*"]

    Also, check the `DJANGO_BASE` and the `DJANGO_URL` variables to know the
    base path under which Django is deployed. By default, the webapp will be
    deployed in `http://localhost:8000/django_base_value`.

13. Do a

        python manage.py runserver --insecure

    to launch the app in the development mode.

    If you want to launch the app in development mode and make it available from
    an internal network run:

        python manage.py runserver 0.0.0.0:port --insecure

    We provide the `start_dev_webapp.sh` script for starting the app in
    development mode and making it accessible from an internal network. And the
    `stop_dev_webapp.sh` script to stop the webapp. Notice that you may need to
    change the ports used in these scripts.   
