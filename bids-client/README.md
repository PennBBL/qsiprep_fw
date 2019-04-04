# bids-client
Holding place for BIDS enabled client
REF: https://flywheelio.aha.io/epics/FW-E-39

## Overview
The BIDS Client has three components:

- Upload
- Curate
- Export

Below is more information about each of the components.

##### Build the image
The following command will build the docker image containing all BIDS Client components.

```
git clone https://github.com/flywheel-io/bids-client
cd bids-client
docker build -t flywheel/bids-client .
```

## Upload
The upload script (upload_bids.py) takes a BIDS dataset and uploads it to Flywheel.

##### Flywheel CLI
NOTE: This requires the Flywheel CLI.

The upload script has been integrated into the flywheel cli as
```
fw import bids [folder] [group] [project] [flags]
```

##### Docker Script
A docker script has been provided to simplify the below process.
To run:
```
./docker/upload.sh \
    /path/to/BIDS/dir/in/container \
    --api-key '<PLACE YOUR API KEY HERE>' \
    --type 'Flywheel' \
    -g '<PLACE GROUP ID HERE>'
```

An optional project flag can also be given if the given BIDS directory is not at the project level.
```
    -p '<PLACE PROJECT LABEL HERE>'
```

##### Run Docker image locally
Startup container
```
docker run -it --rm \
    -v /path/to/BIDS/dir/locally:/path/to/BIDS/dir/in/container \
     bids-client /bin/bash
```

Run the upload script
```
python /code/upload_bids.py \
    --bids-dir /path/to/BIDS/dir/in/container \
    --api-key '<PLACE YOUR API KEY HERE>' \
    --type 'Flywheel' \
    -g '<PLACE GROUP ID HERE>'
```

## Curate

##### Gear
The BIDS Curation step (curate_bids.py) has been transformed into a gear for better usability.
The git repo for the gear is here: https://github.com/flywheel-apps/curate-bids

##### Docker Script
Run it using the docker script
```
./docker/curate.sh \
    --api-key '<PLACE YOUR API KEY HERE>' \
    -p '<PLACE PROJECT LABEL HERE>' \
    [optional flags]
```
Flags:
```
  --reset               Reset BIDS data before running
  --template-file       Template file to use
```

## Export
The export script (export_bids.py) takes a curated dataset within Flywheel and downloads it to local disk.

##### Flywheel CLI
NOTE: This requires the Flywheel CLI.

Usage:
```
fw export bids [dest folder] [flags]
```

Flags:
```
  -h, --help             help for bids
  -p, --project string   The label of the project to export
      --source-data      Include sourcedata in BIDS export
```

##### Docker Script
To run
```
./docker/export.sh \
    /path/to/BIDS/dir/in/container \
    --api-key '<PLACE YOUR API KEY HERE>' \
    -p '<PLACE PROJECT LABEL HERE>'
```

##### Run Docker image locally
Startup container
```
docker run -it --rm \
    -v /path/to/BIDS/dir/locally:/path/to/BIDS/dir/in/container \
     bids-client /bin/bash
```

Run the export script
```
python /code/export_bids.py \
    --bids-dir /path/to/BIDS/dir/in/container \
    --api-key '<PLACE YOUR API KEY HERE>' \
    -p '<PROJECT LABEL TO DOWNLOAD>'
```
