#!/usr/bin/env python3
import json
import argparse
import os
from configparser import ConfigParser
from typing import Tuple, List


def dump_manifest(config_dict):
    """
    Dump the manifest section,
    Args:
        config_dict: A configuration dict for the input full-launcher
        configuration.
    """
    manifest_data = {}
    for key, value in config_dict["manifest"].items():
        manifest_data[key] = value.lower() == "true"
    return manifest_data


def dump_config_to_dict(config):
    return {
        section: dict(config.items(section)) for section in config.sections()
    }


def dump_files(config_dict, files: Tuple[str, List[str]]):
    """
    Dumps specified sections from a configuration dict into multiple output
    files.

    Args:
        config_dict: A configuration dict for the input full-launcher
                configuration.
        files: A dictionary where:
            - keys (str): File paths for output files.
            - values (List[str]):
                List of section names to be written to the corresponding file.


    """
    for file, sections in files:
        with open(file, "w") as f:
            if file.endswith("manifest.json"):
                json_file = dump_manifest(config_dict)
                json.dump(json_file, f, indent=2)
            else:
                tmp_config = ConfigParser()
                # Fileter out the expected sections for the file
                filtered_data = {
                    key: value
                    for key, value in config_dict.items()
                    if key in sections
                }
                tmp_config.read_dict(filtered_data)
                tmp_config.write(f)


def mandatory_sections_check(config_dict, mandatory_sections):
    missing_sections = [
        item for item in mandatory_sections if item not in config_dict.keys()
    ]
    if missing_sections:
        raise SystemError(
            "Missing mandatory sections: {}".format(missing_sections)
        )


def parse_and_separate_file(input_file):
    """
    Parses full-launcher file and separates it into multiple output files
    includes:
    1.launcher - includes launcher, test plan and test selection
    2.manifest.json
    3.checkbox.conf

    Args:
        input_file (str): Path to the input file.
    """
    # Convert input_file to an absolute path
    input_file = os.path.abspath(input_file)

    # Define output file
    input_dir = os.path.dirname(input_file)
    output_launcher = os.path.join(input_dir, "launcher")
    output_manifest = os.path.join(input_dir, "manifest.json")
    output_checkbox_conf = os.path.join(input_dir, "checkbox.conf")

    # Define the included sections of the content for each file
    launcher_sections = ["launcher", "test plan", "test selection"]
    checkbox_conf_sections = ["environment"]
    manifest_sections = ["manifest"]

    # Initialize configparser and read the file
    config = ConfigParser(delimiters="=")
    config.optionxform = str
    config.read(input_file)

    files = (
        [output_launcher, launcher_sections],
        [output_manifest, manifest_sections],
        [output_checkbox_conf, checkbox_conf_sections],
    )

    # We treat launcher, test plan, test selection, environment and
    # manifest sections as mandatory sections since cert teams infrastructure
    # need those informations.
    mandatory_sections = list(
        set(launcher_sections + checkbox_conf_sections + manifest_sections)
    )

    mandatory_sections_check(dump_config_to_dict(config), mandatory_sections)
    dump_files(dump_config_to_dict(config), files)

    print(
        "Output files created:\n  {}\n  {}\n  {}".format(
            output_launcher, output_manifest, output_checkbox_conf
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Parse and separate full-launcher file into "
            "multiple output files."
        )
    )
    parser.add_argument(
        "input_file", help="Path to the input full-launcher file."
    )
    args = parser.parse_args()

    try:
        parse_and_separate_file(args.input_file)
    except FileNotFoundError:
        print("Error: The file {} does not exist.".format(args.input_file))
    except Exception as e:
        print("An error occurred: {}".format(e))


if __name__ == "__main__":
    main()
