#!/usr/bin/env python3

"""
Compare or generate or update the manifest for a specific test plan.
"""

import json
import subprocess
import argparse


usage = """\
manifest_get_compare.py [-h] {compare,generate} \
--test_plan="TEST_PLAN" --manifest="MANIFEST_FILE"

Examples:
    Compared manifest with a test plan:
        python3 manifest_get_compare.py compare --test_plan="TEST_PLAN"\
 --manifest="MANIFEST_FILE"

    Compare and update the manifest:
        python3 manifest_get_compare.py compare --update\
 --test_plan="TEST_PLAN" --manifest="MANIFEST_FILE"

    Generate manifest for test plan:
        python3 manifest_get_compare.py generate --test_plan="TEST_PLAN"\
 --manifest="MANIFEST_FILE"

"""


def get_manifest_from_testplan(test_plan):
    """
    get the manifest from the output of checkbox-cli expand command,
    write it to a specified file.
    Args:
        test_plan: The test plan for which to get the manifest.
    """

    # Check if checkbox-cli is accessible
    try:
        subprocess.run(
            ["checkbox-cli", "--version"], capture_output=True, check=True
        )
    except FileNotFoundError:
        raise SystemExit(
            "checkbox-cli command not found."
            "Please install it or check your PATH."
        )

    try:
        result = subprocess.run(
            ["checkbox-cli", "expand", test_plan, "-f", "json"],
            capture_output=True,
            text=True,
            check=True,
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

    return ids


def generate_new_manifest(new_manifest_file, ids):
    with open(new_manifest_file, "w") as f:
        json.dump({id: True for id in sorted(ids)}, f, indent=2)


def compare_json_keys(orig_manifest_file, new_keys):
    """
    Compares the keys in original manifest file and the new_keys.
    Args:
        orig_manifest_file: The path to the orignial manifest file to compared.
        new_keys: The manifest key get from test plan.
    """

    try:
        with open(orig_manifest_file, "r") as f:
            old_data = json.load(f)

        old_keys = set(old_data.keys())

        ret = True
        # Added keys
        added_keys = new_keys - old_keys
        if added_keys:
            ret = False
            print("Added manifests:")
            for key in added_keys:
                print(f"{key}")

        # Removed keys
        removed_keys = old_keys - new_keys
        if removed_keys:
            ret = False
            print("Removed manifest:")
            for key in removed_keys:
                print(f"{key}")

        if ret:
            print("Manifests are the same.")

        return ret
    except FileNotFoundError:
        raise SystemExit(f"File not found: {orig_manifest_file}")
    except json.JSONDecodeError:
        raise SystemExit("JSON decoding error")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare or generate or update the manifest for a test plans."
        ),
        usage=usage,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="command should be in compare, generate."
    )
    subparsers.required = True

    parser_compare = subparsers.add_parser(
        "compare", help="Compare or update the manifest with a test plans."
    )
    parser_compare.add_argument(
        "--update", action="store_true", help="compare and update the manifest"
    )
    parser_compare.add_argument(
        "--test_plan",
        required=True,
        help="The test plan to compare.",
    )
    parser_compare.add_argument(
        "--manifest", required=True, help="The manifest file to be compared."
    )

    parser_generate = subparsers.add_parser(
        "generate", help="Generate a manifest file for the test plan."
    )
    parser_generate.add_argument(
        "--test_plan",
        required=True,
        help="Generate manifest for the test plan.",
    )
    parser_generate.add_argument(
        "--manifest", required=True, help="File to store generated manifest."
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    if args.command == "compare":
        print(f"Comparing to test plan: {args.test_plan}")
        print(f"Using manifest: {args.manifest}")
        ids = get_manifest_from_testplan(args.test_plan)
        ret = compare_json_keys(args.manifest, ids)
        if args.update:
            if not ret:
                print("Something changed, update the manifest.")
                generate_new_manifest(args.manifest, ids)
            else:
                print("No update needed.")

    elif args.command == "generate":
        print(f"Generating manifest for test plan: {args.test_plan}")
        ids = get_manifest_from_testplan(args.test_plan)
        print(f"Write manifest to: {args.manifest}")
        generate_new_manifest(args.manifest, ids)


if __name__ == "__main__":
    main()
