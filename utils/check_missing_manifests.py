#!/usr/bin/env python3

import argparse
import base64
import json
import os
import re
import urllib.parse
import urllib.request
import sys
from typing import Tuple

BASE_URL = "https://certification.canonical.com/api/v2/labresources/"
CERTIFICATION_LABS = "TEL-L2,TEL-L3,TEL-L5,TEL-L6"


def get_c3_token(client_id, client_secret):
    credential = base64.b64encode(
        "{0}:{1}".format(client_id, client_secret).encode("utf-8")
    ).decode("utf-8")
    headers = {
        "Authorization": "Basic {0}".format(credential),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials", "scope": "read write"}
    # Encode the data to be sent in the POST request
    encoded_data = urllib.parse.urlencode(data).encode("utf-8")
    # Create a request object
    url = "https://certification.canonical.com/oauth2/token/"
    request = urllib.request.Request(url, data=encoded_data, headers=headers)

    # Make the POST request and read the response
    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        response_json = json.loads(response_data)

    return response_json["access_token"]


def get_devices_in_labs(c3_token):
    base_url = BASE_URL
    params = {
        "datacentre__name__in": CERTIFICATION_LABS,
        "pagination": "limitoffset",
        "limit": 0,
    }

    # Encode the parameters
    encoded_params = urllib.parse.urlencode(params)

    # Construct the full URL
    full_url = f"{base_url}?{encoded_params}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {c3_token}",
    }

    # Convert the payload to a JSON string
    # json_payload = json.dumps(payload).encode("utf-8")
    # Create the request object with the data and headers
    req = urllib.request.Request(
        # api_url, data=json_payload, headers=headers, method="GET"
        full_url,
        headers=headers,
        method="GET",
    )

    # Send the request and get the response
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
    cids = {
        d["canonical_id"]
        for d in result["results"]
        if d["role"] == "DUT" and d["canonical_id"]
    }
    return cids


def get_cid_dirs(basedir):
    pattern = r"^\d{6}-\d{5,}$"
    paths = {}
    for root, dirs, files in os.walk(basedir):
        if re.match(pattern, os.path.basename(root)):
            paths[os.path.basename(root)] = root
    return paths


def get_manifest_data(path):
    with open(os.path.join(path, "manifest.json")) as fp:
        data = json.load(fp)
    return data


def check_missing_manifests(
    cids_in_lab: list[str],
    cid_dirs: dict[str, str],
    manifest_id_list: list[str],
) -> Tuple[list[str], dict[str, list[str]]]:
    cids_with_missing_manifest_files = []
    cids_with_missing_manifest_entries = {}
    for cid in cids_in_lab:
        try:
            manifest_path = cid_dirs[cid]
            manifest_data = get_manifest_data(manifest_path)
            missing_manifest_entries = []
            for manifest_id in manifest_id_list:
                if manifest_id not in manifest_data:
                    missing_manifest_entries.append(manifest_id)
            if missing_manifest_entries:
                cids_with_missing_manifest_entries[cid] = (
                    missing_manifest_entries
                )
        except KeyError:
            # No config path found for this CID, so the manifest file is not
            # there either
            cids_with_missing_manifest_files.append(cid)
        except FileNotFoundError:
            cids_with_missing_manifest_files.append(cid)
    return cids_with_missing_manifest_files, cids_with_missing_manifest_entries


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-dir", default=".", help="Path to ce-oem DUT configurations."
    )
    parser.add_argument(
        "--manifest-entries",
        nargs="+",
        help="A list of manifest entries to check.",
    )
    args = parser.parse_args(args)
    client_id = os.getenv("C3_CLIENT_ID")
    client_secret = os.getenv("C3_CLIENT_SECRET")
    c3_token = get_c3_token(client_id, client_secret)
    cids_in_lab = get_devices_in_labs(c3_token)
    cid_dirs = get_cid_dirs(args.config_dir)
    cids_with_missing_manifest_files, cids_with_missing_manifest_entries = (
        check_missing_manifests(cids_in_lab, cid_dirs, args.manifest_entries)
    )
    if cids_with_missing_manifest_entries:
        print(
            (
                f"The following {len(cids_with_missing_manifest_entries)} CIDs "
                "currently in the Certification lab are missing manifest "
                "entries:"
            )
        )
        for (
            cid,
            manifest_entries,
        ) in cids_with_missing_manifest_entries.items():
            print(f"- {cid} (missing entries: {', '.join(manifest_entries)})")
        print()

    if cids_with_missing_manifest_entries:
        raise SystemExit("Error: Missing data. See above.")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
