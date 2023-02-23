## Purpose
This repository is a place to stored the checkbox configuration for all enablement devices

## The directory structure for this repository
```bash
├── pc
│   ├── 201212-12345 (example)
│   │   ├── extra_checkbox.conf
│   │   └── manifest.json
│   └── default
│       └── manifest.json
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

## How to update manifest
Running manifest-update.py to create/update manifest.json file for single DUT with CID number

e.g. create or update a new manifest file
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-update.py -c 202315-12345 --manifest-data "{\"com.canonical.certification::has_dp\": true, \"com.canonical.certification::has_dvi\": true,}"
```

e.g. create or update both manifest and checkbox config file
```
u:~/ce-oem-dut-checkbox-configuration$ python3 utils/manifest-update.py -c 202315-12345 --manifest-data "{\"com.canonical.certification::has_dp\": true, \"com.canonical.certification::has_dvi\": true,}" --checkbox-conf-data "[environment]\nSERIAL_PORTS_STATIC = /dev/ttyS3"
```
