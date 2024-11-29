#!/usr/bin/env python3

"""
Generate a manifest.json for a device manifest with a default value
of "true" based on a specific test plan.

If a machine manifest is provided, the tool will generate the corresponding
device manifest and compare it with the given machine manifest. It will
return true if the two manifests are identical; otherwise, it will return
false and print the differences.
"""

import json
import subprocess
import argparse
import sys


def get_manifest_from_testplan(test_plan, out_file):
    """
    get the manifest from the output of checkbox-cli expand command,
    write it to a specified file.

    Args:
        test_plan: The test plan to expand.
        out_file: The output filename.
    """

    # Check if checkbox-cli is accessible
    try:
        subprocess.run(
            ["checkbox-cli", "--version"],
            capture_output=True, check=True
            )
    except FileNotFoundError:
        raise SystemExit(
            "checkbox-cli command not found."
            "Please install it or check your PATH.")

    try:
        result = subprocess.run(
            ["checkbox-cli", "expand", test_plan, "-f", "json"],
            capture_output=True, text=True, check=True
            )
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"Error executing checkbox-cli: {e}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise SystemExit("Output from checkbox-cli is not valid JSON.")

    ids = set()
    for entry in data:
        if entry["unit"] == "manifest entry":
            ids.add(entry["id"])

    sorted_ids = sorted(ids)

    new_data = {id: True for id in sorted_ids}

    with open(out_file, 'w') as f:
        json.dump(new_data, f, indent=2)


def compare_json_keys(old_json_file, new_json_file):
    """
    Compares the keys in two JSON files and prints the difference.

    Args:
        old_json_file: The path to the orignial manifest file to be compared.
        new_json_file: The path to the new manifest file.

    Returns:
        Boolean: True if the files are identical, False if they differ.
    """

    try:
        with open(old_json_file, 'r') as f:
            old_data = json.load(f)
        with open(new_json_file, 'r') as f:
            new_data = json.load(f)

        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())

        ret = True
        # Added keys
        added_keys = new_keys - old_keys
        if added_keys:
            ret = False
            print("Added manifests:")
            for key in added_keys:
                print(f"{key}: {new_data[key]}")

        # Removed keys
        removed_keys = old_keys - new_keys
        if removed_keys:
            ret = False
            print("Removed manifest:")
            for key in removed_keys:
                print(f"{key}: {old_data[key]}")

        return (ret)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {old_json_file} or {new_json_file}")
    except json.JSONDecodeError:
        raise SystemExit("JSON decoding error")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a manifest from a test plan, Compare it with"
            " an specific manifest."
        )
    )
    parser.add_argument('--test_plan', type=str, help='Test plan to expand')
    parser.add_argument(
        '--new_manifest',
        type=str,
        help='Path to the new manifest file extracted from the test plan'
    )
    parser.add_argument(
        '--orig_manifest',
        type=str,
        help='Path to the original manifest file to be compare')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    get_manifest_from_testplan(args.test_plan, args.new_manifest)

    if args.orig_manifest:
        if compare_json_keys(args.orig_manifest, args.new_manifest):
            print("Manifests are identical")
            sys.exit(0)
        else:
            print("Manifests are different")
            sys.exit(1)
