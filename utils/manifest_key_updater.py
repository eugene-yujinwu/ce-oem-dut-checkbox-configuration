"""
JSON Manifest Sync Tool

This script synchronizes keys/values from a source JSON file to a target JSON file.
When the target file is missing or invalid, it will be initialized with the source content.

Usage: python manifest_key_updater.py <source.json> <target.json>
"""

import json
import argparse


def update_json(file1_path, file2_path):
    # Read the first JSON file (source)
    try:
        with open(file1_path, "r") as f1:
            data1 = json.load(f1)
    except FileNotFoundError:
        print(f"Error: Source file {file1_path} does not exist")
        return
    except json.JSONDecodeError:
        print(f"Error: Source file {file1_path} is not a valid JSON file")
        return

    # Verify the source data is a dictionary
    if not isinstance(data1, dict):
        print("Error: Source JSON file must contain a dictionary object")
        return

    # Handle the target file (file2)
    try:
        with open(file2_path, "r") as f2:
            data2 = json.load(f2)

            # Verify it's a dictionary
            if not isinstance(data2, dict):
                print(
                    f"Warning: Target file {file2_path} is not a dictionary - replacing with source file"
                )
                raise json.JSONDecodeError("Not a dictionary", "", 0)

    except FileNotFoundError:
        print(
            f"Warning: Target file {file2_path} does not exist - creating from source"
        )
        data2 = {}
    except json.JSONDecodeError:
        print(
            f"Warning: Target file {file2_path} is not valid JSON - replacing with source"
        )
        data2 = {}

    # Compare keys and add missing ones
    added_keys = []
    for key in data1:
        if key not in data2:
            data2[key] = data1[key]
            added_keys.append(key)

    # If no keys were added
    if not added_keys:
        print(f"File {file2_path} already contains all keys from {file1_path}")
        return

    try:
        with open(file2_path, "w") as f2:
            json.dump(data2, f2, indent=4, sort_keys=True)
            f2.write("\n")
    except IOError:
        print(f"Error: Could not write to file {file2_path}")
        return

    print(f"Added {len(added_keys)} keys to {file2_path}:")
    for key in added_keys:
        print(f"  - {key}")


def main():
    parser = argparse.ArgumentParser(description="Update manifest JSON keys")

    parser.add_argument("source_JSON", type=str, help="Path to source JSON file")
    parser.add_argument("target_JSON", type=str, help="Path to target JSON file")

    args = parser.parse_args()

    update_json(args.source_JSON, args.target_JSON)


if __name__ == "__main__":
    main()
