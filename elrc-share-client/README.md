Overview
--------

**elrc-share-client** is Python API with an interactive command-line tool for retrieving, creating and updating ELRC-SHARE resources.

1. [Installation](#installation)
2. [Using the interactive command line tool](#cli)
    1. [User Authentication](#auth)
    2. [Resource Retrieval](#retrieve)
    3. [Resource Creation/Update](#create)
3. [Using the **ELRCShareClient** class](#pythonapi)

## 1. Installation <a name="installation">
1. Install Python 3.6
2. `cd` to a preferred directory and create a virtual environment based on Python 3.6

    `cd /path/to/my/directory`  
3.  Create a virtual environment

    `python -m venv elrc_env` 
    
    or
    
    `virtualenv --python=/path/to/python3.6/python3 elrc_env` if you have a previous Python 2.7 installation
    
4. Activate the new virtual environment
    
    `source elrc_env/bin/activate` for Linux
    
    `elrc_env/Scripts/activate` for Windows
    
5. install the *elrc-share-client* package with pip

    `pip install https://gitlab.com/ilsp-nlpli-elrc-share/elrc-share-client.git`
    
    `DOWNLOAD_DIR`: 
    The installation process creates a default download directory (`/home/<user>/ELRC-Downloads` for 
    Linux or `C:\Users\<UserName>\Downloads\ELRC-Downloads` for Windows)
    
6. Start the ELRC-SHARE shell

    `elrc-shell`

## 2. Using the interactive command line tool <a name="cli">
### 2.1. User Authentication <a name="auth">
Users that intend to use the elrc-share-client must have an active and elevated account on ELRC-SHARE repository.
After <a href="https://elrc-share.eu/accounts/create/" target="_blank">registration</a>, contact the ELRC-SHARE repository administrators 
at [elrc-share@ilsp.gr](mailto:elrc-share@ilsp.gr), stating your affiliation and role in the context of ELRC or 
of a CEF-funded project. Once this has been approved by the ELRC consortium, you will be notified by email.
#### Available Commands
- `login <username> <password>`
- `logout`
### 2.2. Resource Retrieval <a name="retrieve">
#### Available Commands
- `list`
- `getj`
- `getx`
- `download`

##### Resource Access Authorization
- *Administrators*: all resources
- *ELRC Reviewers*: all resources
- *EC members*: all published, ingested and own resources
- *Simple editors*: own resources
- *Contributors*: no resources

#### `list`
Returns a list of all resources accessible by the user. The returned information for each resource consists of 
the following tab delimited values:

1. The resource id
2. The resource name
3. The resource's publication status

**Options**

 `--my`: Returns all resources that the user owns (has no effect for simple editors).
 
**Examples**

    # List all accessible resources
    list
    
    # List own resources
    list --my

#### `getj`
Returns a json representation of a resource or a list of resources
(as seperate json strings). If no resources are
specified, the command will return all the resources that a logged in
user has access to, based on their
permissions, in a single json object. In addition to the metadata, the
result also contains information about
the publication status of the resource and it's download location (if
no dataset has been uploaded this location
will be an empty directory).

**Arguments**

A list of space seperated resource ids

**Options**

 `-p` or `--pretty`: Pretty prints the json output.

 `--my`: Returns only the resources that the user owns (useful
 for admins, ec members and erlc reviewers).
 
 `-s` or `--save`: Saves the output to a file in the default directory
 
 `--distinct`: Returns each resource as a separate .json string
 
**Examples**

    # Get a json representation of the resource with id 100
    getj 100
    
    # Get a formatted json representation of the resource with id 100
    getj 100 --pretty
    
    # Get json representations of the resources with ids 10, 11, and 23
    getj 10 11 23
    
    # Get a json representation of all the resources that the currently logged in user has access to
    getj
    
    # Get a json represenatation of all accessible resources and save as separate .json files in the default download directory
    getj --save --pretty --distinct

#### `getx`
Returns an XML representation of a resource or a list of resources
(as seperate xml strings) that a logged in user has access to.

**Arguments**

A list of space separated resource ids
    
**Options**

 `-p` or `--pretty`: Pretty prints the xml output
 
 `-s` or `--save`: Saves the output to a file in the default directory
 
 `--my`: Returns only the resources that the user owns (useful
 for admins, ec members and erlc reviewers).

Results returned by the `list`, `getj` and `getx` commands can **also** be saved to a file using output redirection `>`. 
If no path is specified, the result will be saved in the default directory (`/home/<user>/ELRC-Downloads` 
for Linux and `C:\Users\<UserName>\Downloads\ELRC-Downloads` for Windows).

    # default download directory
    getx 100 > resource-100.xml 
    
    # user defined directory
    getx 100 > /path/to/my/directory/resource-100.xml

**Examples**

    # Get an xml representation of the resource with id 100
    getx 100
    
    # Get a formatted xml representation of the resource with id 100
    getx 100 --pretty

    # Get an xml representation of all the resources that the currently logged in user has access to
    # Since this command will return multiple xml strings, the > redirection to file won't work. Use --save instead
    getx
    
    # Get an xml represenatation of all accessible resources and save as separate .xml files in the default download directory
    getx --save --pretty --distinct

    
#### `download`
Retrives the zipped dataset of a resource or a list of resources that a logged in user has access to. The .zip archive is saved as *archive-\<resource-id>.zip* into the specified directory or the default directory if no destination is specified.

**Options**

`-d` or `--dest`: The location where the zip archive is to be saved. If
no destination is specified, the archive will be saved in the default
directory.

**Examples**
    
    # download the datasets of the resources with ids 100 and 110
    download 100 110
    
    # download the datasets of the resources with ids  100 and 110 into the specified destination
    download 100 110 --dest /path/to/my_dir

### 2.3. Resource Creation/Update <a name="create">
##### Available Commands
- `import`
- `update`
- `upload`

#### `import`
Creates a new resource from an xml file, with optional dataset
(.zip archive) to upload. For batch
creation, pass the **absolute path** to the directory containing the metadata xml files, along with any datasets. In 
this case the command will try to upload any .zip archive that has the same name with the xml file,
within the same directory (e.g. resource1.xml, resource1.zip)

**Arguments**

The **absolute path** to the metadata xml file or the containing directory (for
batch creation).

**Options**

`-z` or `--data`: The **absolute path** to the .zip archive to be uploaded along
with the new resource (not used for batch creation).

**Examples**

    # import resource metadata
    import /path/to/resource.xml
    
    # create resource metadata with dataset
    import /path/to/resource.xml --data /path/to/dataset.zip
    
    # create resources from directory
    import /path/to/resources/directory

#### `update`
Updates a resource description from an xml file.

**Arguments**

An ELRC-SHARE resource id.

**Options**

`-f` or `--file`: The **absolute path** to the metadata xml file.

**Examples**
    
    # Update the resource with id 100 with the specified xml file
    update 100 --file /path/to/updated/xml_file.xml

#### `upload`
Uploads a single dataset .zip archive for a given resource id.

**Arguments**

An ELRC-SHARE resource id.

**Options**

`-z` or `--data`: The **absolute path** to the .zip archive to be uploaded.

**Examples**
    
    # Upload the specified .zip archive to resource with id 100 (replaces existing dataset)
    upload 100 --data /path/to/zipped/archive.zip

## 3. Using the ELRCShareClient class <a name="pythonapi">

```python
# create an ELRCShareClient object
from elrc_client.client import ELRCShareClient
client = ELRCShareClient()

# Login to ELRC-SHARE repository using a valid username and password
client.login('username', 'password')


# LISTING RESOURCES
# -----------------

# get a list of my resources
client.list(my=True, raw=False)

# get a list of all accessible resources
client.list(raw=False)

# get a list of all accessible resources and save to .tsv file
with open('list.tsv', 'w', encoding='utf-8') as f:
    f.write(client.list())
        
    
# RETRIEVING RESOURCES
# --------------------

# Get the metadata of resource 338 as formatted xml and save to file (in DOWNLOAD_DIR, as 'resource-338.xml')
client.get_resource(338, as_xml=True, pretty=True, save=True)

# Get the metadata of resource 338 as formatted json and save to file (in DOWNLOAD_DIR, as 'resource-338.json')
client.get_resource(338, as_json=True, pretty=True, save=True)

# Download the dataset associated with resource 338 (saved in DOWNLOAD_DIR as archive-338.zip)
client.download_data(338, progress=False)

# Get metadata in separate xml files (in DOWNLOAD_DIR) for all my resources
client.get_resources(as_xml=True, pretty=True, save=True, my=True)

# Get metadata in separate json files for all accessible resources
client.get_resources(as_json=True, distinct=True, pretty=True, save=True)

# Get metadata in a compact json file for all accessible resources
client.get_resources(as_json=True, pretty=True, save=True)

# Get a python dictionary for all accessible resources
client.get_resources()


# CREATING RESOURCES
# ------------------

# Create a new resource with associated dataset
client.create('path/to/resource.xml', dataset='path/to/dataset.zip')

# Batch create resources from specified directory
# The directory should contain valid xml descriptions and, optionally, .zip files with the same name as the
# associated xml files.
client.create('path/to/xml/descriptions/directory')


# UPDATING EXISTING RESOURCES
# ---------------------------

# Update resource 334 metadata using the specified xml file
client.update_metadata(334, 'path/to/resource-334.xml')

# Upload dataset for resource 334 (replace existing)
client.upload_data(334, 'path/to/dataset.zip')

#-------------------------
#logout
client.logout()

```