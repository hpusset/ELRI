Postgres Database Image
=================================================================

Build
-----

01. Building the image locally

```
$ docker build . --no-cache -t elrinrs/postgres-server:MASTER
```

02. Publishing the image to the repository

```
$ docker push elrinrs/postgres-server:MASTER
```