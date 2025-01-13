#!/usr/bin/env python3
import json
import argparse
import os
from configparser import ConfigParser
from typing import Tuple, List, Dict


def dump_manifest(config_dict: Dict[str, Dict[str, str]]):
    """
    Dump the manifest section,
    Args:
        config_dict: A configuration dict for the input full-launcher
        configuration.
    """
    manifest_data = {
        key: value == "true" for key, value in config_dict["manifest"].items()
    }
    return manifest_data


def dump_config_to_dict(config: ConfigParser) -> Dict[str, Dict[str, str]]:
    """
    Dump config file to a dictionary.
    Args:
        config: A configuratoin object for the input full-launcher
    """
    return {
        section: dict(config.items(section)) for section in config.sections()
    }


def dump_files(
    config_dict: Dict[str, Dict[str, str]], files: Tuple[str, List[str]]
):
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
                # This part could be used if one file include multiple sections
                tmp_config = ConfigParser()
                # Fileter out the expected sections for the file
                filtered_data = {
                    key: value
                    for key, value in config_dict.items()
                    if key in sections
                }
                tmp_config.read_dict(filtered_data)
                tmp_config.write(f)
        print("Output files created:\n  {}\n".format(file))


def mandatory_sections_check(
    config_dict: Dict[str, Dict[str, str]], mandatory_sections: List
):
    missing_sections = [
        item for item in mandatory_sections if item not in config_dict.keys()
    ]
    if missing_sections:
        raise SystemError(
            "Missing mandatory sections: {}".format(missing_sections)
        )


def parse_and_separate_file(input_file: str):
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

    if not os.path.exists(input_file):
        raise FileNotFoundError

    # Define output file
    input_dir = os.path.dirname(input_file)
    output_manifest = os.path.join(input_dir, "manifest.json")

    # Define the included sections of the content for each file
    manifest_sections = ["manifest"]

    # Initialize configparser and read the file
    config = ConfigParser(delimiters="=")
    config.optionxform = str
    config.read(input_file)

    files = ([output_manifest, manifest_sections],)

    mandatory_sections = list(manifest_sections)
    config_dict = dump_config_to_dict(config)
    mandatory_sections_check(config_dict, mandatory_sections)
    dump_files(config_dict, files)


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
        raise SystemError(
            "The file {} does not exist.".format(args.input_file)
        )
    except Exception as e:
        raise SystemError("An error occurred: {}".format(e))


if __name__ == "__main__":
    main()
