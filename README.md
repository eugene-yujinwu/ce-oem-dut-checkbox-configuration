## Purpose
This repository is a place to stored the checkbox configuration for all enablement devices

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
Running manifest-generator.py to launch Checkbox manifest brower to configure manifest.json
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
If the DUT manifest file is exist, the scripts would update the user provided machine manifest string to it.
Othewise, the scripts would generate a DUT manifest file with following scenario
1. machine manifest string is available no matter upload argument is true or false, apply it to DUT manifest file
2. the upload argument is true, apply default/manifest.json to DUT manifest file
3. the upload argument is false, apply default/pc-mini-manifest.json to DUT manifest file. (It's for PC sanity)

### For the checkbox configuration
If the DUT checkbox configuration is exist, the scripts would update the user provided checkbox conf string to it.
Otherwise, the scripts would generate a DUT checkbox configuration with following orders.
1. apply the default/checkbox.conf to DUT checkbox configuration
2. update user provided checkbox conf string to DUT checkbox configuration

### Example
e.g. create or update a new manifest file
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-update.py -c 202315-12345 --manifest-data "{\"com.canonical.certification::has_dp\": true, \"com.canonical.certification::has_dvi\": true,}"
```

e.g. create or update both manifest and checkbox config file
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-update.py -c 202315-12345 --manifest-data "{\"com.canonical.certification::has_dp\": true, \"com.canonical.certification::has_dvi\": true,}" --checkbox-conf-data "[environment]\nSERIAL_PORTS_STATIC = /dev/ttyS3"
```
