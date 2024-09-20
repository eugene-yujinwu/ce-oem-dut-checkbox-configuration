#!/usr/bin/env python3

"""
Query the `physicalmachinesview` from C3,
retrieve the queues that each device subscribes to,
create a mapping from queues to Canonical IDs and
store it in a JSON file.

Use a JSON input file that stores a list of queues as a filter,
i.e. restrict the mapping to queues found in that file.
"""

import argparse
import base64
import json
import os
import requests
from collections import defaultdict


# code for authenticating to C3 and using an endpoint:
# https://github.com/canonical/hexr/blob/main/docs/how-to/authenticate.md
# https://certification.canonical.com/api/v2/schema

def get_access_token(client_id, secret):
    credential = base64.b64encode("{0}:{1}".format(client_id, secret).encode("utf-8")).decode("utf-8")
    headers={
            'Authorization': "Basic {0}".format(credential),
            "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {
        'grant_type': 'client_credentials',
        'scope': 'read write'
    }
    response = requests.post("https://certification.canonical.com/oauth2/token/", headers=headers, data=params)
    response.raise_for_status()
    return response.json()['access_token']

def c3_query_all(access_token, url):
    headers={
        "Authorization": "Bearer {0}".format(access_token)
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    results = response.json()
    for result in results['results']:
        yield result
    if results['next']:
        yield from c3_query_all(access_token, results['next'])


parser = argparse.ArgumentParser()
parser.add_argument("output", type=str, help="The output JSON file that holds the mapping")
parser.add_argument("--filter", type=str, help="The JSON file with list of queues to use as filter")
args = parser.parse_args()

try:
    client_id = os.environ["C3_ID"]
    secret = os.environ["C3_SECRET"]
except KeyError:
    print("Error: undefined C3_ID or C3_SECRET")
    exit(1)
else:
    access_token = get_access_token(client_id, secret)

if args.filter:
    queue_filter_filename = args.filter
    with open(queue_filter_filename) as queue_filter_file:
        queue_filter = set(json.load(queue_filter_file))
else:
    queue_filter = None

# result: a mapping from queues to CIDs
queue_map = defaultdict(set)

# this is in a try-finally so that partial results can be captured and inspected
# even if Ctrl-C is pressed
try:
    result = c3_query_all(access_token, f"https://certification.canonical.com/api/v2/physicalmachinesview")
    for machine in result:
        cid = machine['canonical_id']
        queues_str = machine['queues']
        if queues_str:
            queues = queues_str.split(',')
            for queue in queues:
                queue = queue.strip()
                if queue_filter is None or queue in queue_filter:
                    queue_map[queue].add(cid)
                    print(f"[*] {cid} <- {queue}")
                else:
                    print(f"[ ] {cid} <- {queue}")
        else:
            print(f"[ ] {cid}")
except KeyboardInterrupt:
    pass
finally:
    with open(args.output, "w") as file:
        json.dump(
            {
                queue: list(cids)
                for queue, cids in queue_map.items()
            },
            file,
            indent=2
        )
        file.write('\n')
