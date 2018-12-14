SolR Image
=================================================================

Build
-----

01. Building the image locally

```
$ docker build . -t elrinrs/solr:MASTER
```

02. Publishing the image to the repository

```
$ docker push elrinrs/solr:MASTER
```

Reminders
-----

- Need to change files in GIT when not building images in MASTER branch:

File                       | Property             | Description
-------------              | -------------        | -------------
Dockerfile                 | GIT_URL              | Replace `trunk` for the desired release