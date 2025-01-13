## Purpose
This repository is a place to store the checkbox configuration for all enablement devices.

## The directory structure for this repository
```bash
├── pc
│   ├── 201212-12345 (example)
│   │   ├── checkbox.conf
│   │   └── manifest.json
│   └── default
│       ├── checkbox.conf
│       ├── manifest.json
│       └── pc-mini-manifest.json
├── utils
│   ├── manifest-generator.py
│   └── manifest-update.py
```

## How to generate a manifest
Running `manifest-generator.py` to launch Checkbox manifest browser to configure manifest.json
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-generator.py -o manifest_file.json
```
Then you could move it a specific folder for a DUT system.
e.g. you want to create a manifest file for laptop system with CID 202111-12345.
1. you could run the manifest-generator.py to generate a manifest.json
2. create a folder named as 202111-12345 under pc folder.
3. move that manifest file into pc/202111-12345 folder.

## How to update manifest and checkbox configuration
Running the manifest-update.py to create/update manifest.json file and checkbox configuration for a specific DUT

### For the machine manifest
If the DUT manifest file exists, the script will update the user-provided machine manifest string to it.
Otherwise, the scripts will generate a DUT manifest file with following scenario:

1. machine manifest string is available no matter upload argument is `true` or `false`, apply it to DUT manifest file
2. the upload argument is `true`, apply `default/manifest.json` to DUT manifest file
3. the upload argument is `false`, apply `default/pc-mini-manifest.json` to DUT manifest file. (It's for PC sanity)

### For the checkbox configuration
If the DUT checkbox configuration is exist, the scripts would update the user provided checkbox conf string to it.
Otherwise, the scripts would generate a DUT checkbox configuration with following orders.
1. apply the default/checkbox.conf to DUT checkbox configuration
2. update user provided checkbox conf string to DUT checkbox configuration

### Examples
#### Create or update a new manifest file
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-update.py -c 202315-12345 --manifest-data "{\"com.canonical.certification::has_dp\": true, \"com.canonical.certification::has_dvi\": true}"
```

#### Create or update both manifest and checkbox config files
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-update.py -c 202315-12345 --manifest-data "{\"com.canonical.certification::has_dp\": true, \"com.canonical.certification::has_dvi\": true}" --checkbox-conf-data "[environment]\nSERIAL_PORTS_STATIC = /dev/ttyS3"
```

# Full Launcher Parser

This script parses a full-launcher file and separates its contents into separate file:
- `manifest.json`: Contains the parsed manifest section as a JSON object.


## Script Overview

The script processes a full-launcher file and divides it into following file:
- **manifest.json**: A JSON file representing the `manifest` section in key-value pairs.

## Usage

To run the script, follow these steps:

    Run the script with the path to the input full-launcher file:

    $./full_launcher_parser.py path/to/full-launcher-file

    Example:
    $./full_launcher_parser.py test_full_launcher

    The folder structure will be like:
    ../iot/test-cid/
    ├── full-launcher
    └── manifest.json

## Input File Format

The input full-launcher file should have sections in the following format:

```
[launcher]
line1
line2

[test plan]
line3
line4

[test selection]
line5
line6

[manifest]
key1=true
key2=false

[environment]
line7
line8

Example:
[launcher]
app_id = com.canonical.qa.shiner:checkbox
launcher_version = 1
stock_reports = text, submission_files, certification

[test plan]
unit = com.canonical.qa.shiner::imx8pdk-automated
forced = yes

[test selection]
forced = yes
exclude = com.canonical.certification::image/model-grade
...

[manifest]
com.canonical.certification::has_bt_adapter= true
com.canonical.contrib::has_optee= true
...

[environment]
TOTAL_RTC_NUM=2
HWRNG=rng-caam
...
```