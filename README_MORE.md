# ELRI National Relay Station (forked from the ELRC-SHARE SOFTWARE)

`ELRC-SHARE SOFTWARE` project: [https://github.com/JuliBakagianni/CEF-ELRC](https://github.com/JuliBakagianni/CEF-ELRC)

`ELDA` webapp project: [https://github.com/ELDAELRA/ELRI](https://github.com/ELDAELRA/ELRI)


## Pull last changes from ELDA

To pull last changes it is necessary to add `ELDA` webapp repository as a new remote repository. Then all changes can be pulled or pushed to any repository.

1. Clone this repository:
```
git clone git@gitlab.vicomtech.es:ELRI_EU2377_2016/ELRI.git
```

2. Add `ELDA` webapp project `URL` as remote:
```
git remote add elda https://github.com/ELDAELRA/ELRI.git
```

3. Pull last changes:
```
git pull elda master
```

4. Push last changes to `GitLab`:
```
git add .
git commit -m "some commentary"
git push origin master
```

5. Change in `metashare/requirements.txt`, resolve conflict with `postgreSQL10`:
```
#psycopg2==2.5.4
psycopg2==2.7
```
6. Set a python2 virtualenv:
```
virtualenv venv
```
6.1. Activate the virtualenv:
```
source venv/bin/activate
```
6.2. Deactivate:
```
deactivate
```

7. Set a  `PostgreSQL` database:


7.1.  install `postgresql`
```
sudo apt install postgresql postgresql-contrib
```

7.2. Change `postgres` access mode to be able to create new database(s) and user(s) (https://gist.github.com/AtulKsol/4470d377b448e56468baef85af7fd614)

7.2.1. Modificar el archivo `/etc/postgres/V/main/pb_hba.conf` adding `trust` connection for the `postgres` user. In this way we will allow this user to login to psql without asking for a password. Also, change the `peer` authentication method to `md5` to avoid conflicts with the OS authentication system.

```
$ sudo vi /etc/postgresql/10/main/pg_hba.conf

#Database administrative login by Unix domain socket
#local all postgres peer
local all postgres trust
# Database administrative login by Unix domain socket
#local   all             all                                     peer
local   all             all                                     md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
#local   replication     all                                     peer
local   replication     all                                     md5
```
7.2.2.  Restart postgresql service
```
    sudo service postgresql restart
```
7.2.3. Now, you can `LOGIN` to the `psql` service using the `postgres` user without need of a password:
```
    psql -U postgres
```
7.2.4. [OPTIONAL] Change the user name postgres password:
```
$ psql -U postgres
postgres=# alter user posrgres with password ‘new-password’;
```
If you want to use this new password you should revert the change in the `pg_hba.conf` file setting the postgres usert authentication method from `trust` to `md5`. And finally, restarting the `postgresql`.

* The file pg_hba.conf will most likely be at /etc/postgresql/9.x/main/pg_hba.conf
or
/etc/postgresql/10/main/pg_hba.conf


7.3.  Create a user:
From command line:
```
createuser elri
```
From `postgresql`, and add its password:
```
$psql -U postgres
postgres=# create role elri;
postgres=# alter user elri with encrypted password 'elri';
```

7.4. Create a database:

From command line:
```
createdb -U postgres elri_metashare
```

7.5. Asign a database to a user:
```
$psql -U postgres
postgres=# grant all privileges on database elri_metashare to elri ;
```

7.6. Allow a user to login to the psql service:
```
$psql -U postgres
postgres=# ALTER ROLE "elri" WITH LOGIN;
```
to this end, it is needed to create a `user` database to make the `psql -U user` command work:
```
$createdb -U postgres elri
$psql -U postgres
postgres=# grant all privileges on database elri to elri ;
```
After that, you will be able to login doing:
```
$psql -U elri
Password:
```
Although, this user already had an associated data base; so it could already do:
```
$psql -U elri elri_metashare
Password:
```
7.7. List all the databases in the `pqsl` service:
```
psql -U postgres -l
```
or from the inside of psql:
```
$ psql -U postgres
postgres-# \list
```

7.8. Change database owner:
```
$ psql -U postgres
alter database elri_metashare owner to elri;
alter database elri owner to elri;
```
Note that this can only be done when logged as the user original owner of the database.
