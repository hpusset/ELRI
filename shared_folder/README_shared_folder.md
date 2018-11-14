# ELRI Toolchain Docker management

- [Introduction](#introduction)
- [Shared Folder](#shared-folder)

## Introduction

The `ELRI Shared Folder` folder allows file sharing between the `ELRI web application` and the `ELRI toolchains` for data processing. It also contains the necessary models to process the data and the toolchains web service configuration file.

## Shared Folder

The `ELRI Shared Folder` is a folder used to share files between the `Docker` image and the server where the image is deployed.

The folder is organised as follows:

```
shared_folder
+-- tch-resources
    +-- translation_tables
    +-- casing_models
+-- config
+-- lang-resources
    +-- timestamp1
        +-- id1_input
        +-- id1_output
        +-- id1_rejected
    +-- timestamp2
        +-- id2_input
        +-- id2_output
        +-- id2_rejected
    +-- timestamp3
...
```

These are the shared files:

- `tch-resources`: contains the models needed by the toolchains (translation and casing models).
  - `translation_tables`: lexical translation tables used by the document alignment module.
  - `casing_models`: truecasing models used by the text preprocessing module.
- `config`: the toolchain configuration file, `web_service.cfg`, is placed in this folder. This file can be edited to change toolchain settings or to update toolchain resource paths.
- `lang-resources`: contains the language resources (`LRs`) handled by the toolchains. The following structure is assumed for each `LR`:
  - `timestamp`: is the time stamp of the upload of the primary `LR` into the system. Taking id to denote the identifier assigned by the system to the current `LR`, this folder contains the following three subfolders:
    - `id_input`: contains the primary data of this `LR`.
    - `id_output`: contains the processed data prepared by the toolchains from the data in id-input.
    - `id_rejected`: contains all data that could not be processed by the toolchains, for one reason or another.
