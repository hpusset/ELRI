ELRI National Relay Station Image
=================================================================

Build
-----

01. Building the image locally

```
$ docker build . -t elrinrs/nationalrelaystation:MASTER
```

02. Publishing the image to the repository

```
$ docker push elrinrs/nationalrelaystation:MASTER
```

Reminders
-----

- Need to change files in GIT when not building images in MASTER branch:

File                       | Property             | Description
-------------              | -------------        | -------------
Dockerfile                 | RELEASE              | Replace `trunk` for the desired release