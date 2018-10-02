ELRI National Relay Station (forked from the ELRC-SHARE SOFTWARE)
=================================================================

Introduction
------------

This code base is a fork of the [ELRC-SHARE](http://elrc-share.eu)
[software](https://github.com/MiltosD/ELRC2), itself a fork of the
[META-SHARE](http://www.meta-share.org/)
[software](https://github.com/metashare/META-SHARE).
software.


With respect to the ELRC-SHARE, the ELRI National Relay Station (NRS) software
will integrate, among other things:

- group-based policy management,
- automatic language resource processing toolchain integration
- manual quality control workflow elements.

Setup
-----

In order to set up a minimal working development version of the platform, the
following steps need to be undertaken:

01. Copy `metashare/local_settings.sample` to `metashare/local_settings.py` and
    change the local_settings accordingly.

02. Set up a Python 2 virtualenv and install the dependencies via

        pip install -r requirements.txt

03. Launch Solr by `cd`-ing in the `solr/` folder and doing

        java -jar -Djetty.port=chosen_port start.jar
    
    Make sure to update the `SOLR_URL` and `TESTING_SOLR_URL` environment
    variables in `metashare/local_settings.py` accordingly.

04. Set up a PostgreSQL database and provide relevant information to the
    relevant `local_settings.py` section.

05. Generate migrations for the relevant apps by doing a
  
        python manage.py makemigrations accounts repository stats \
        recommendations storage

05. Do a

        python manage.py migrate

    to set up the DB schema.

06. Do a

        python manage.py rebuild_index

    to set up the Solr index.

07. Create the directories `metashare/unprocessed` and `metashare/processed`.

08. Create the file `metashare/maintainers.dat`, which should have the following
    format:
    
    Country_name:maintainer_user_name_1,user_name_2,...
  
    for each authorised country_name/maintainer_user_name in the system.

09. Create the folder specified in the `STATIC_ROOT` `metashare/local_settings.py`
    environment variable and run

        python manage.py collectstatic
    
    to collect all static files to the STATIC_ROOT directory.

10. Do a

        python manage.py runserver --insecure
    
    to launch the app in the development mode.
