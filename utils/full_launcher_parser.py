#!/usr/bin/env python3
import json
import argparse
import os
from configparser import ConfigParser
from typing import Tuple, List, Dict
import re


def dump_manifest(config_dict: Dict[str, Dict[str, str]]):
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
        config_dict: Dict[str, Dict[str, str]],
        files: Tuple[str, List[str]]):
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
            if re.match(r".*manifest-\w+\d{2}\.json$", file):
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


def mandatory_sections_check(config_dict: Dict[str, Dict[str, str]],
                             mandatory_sections: List):
    missing_sections = [
        item for item in mandatory_sections if item not in config_dict.keys()
    ]
    if missing_sections:
        raise SystemError(
            "Missing mandatory sections: {}".format(missing_sections)
        )


def image_type_check(file: str):
    # We are expecting the file name of full-launcher
    # should be like "full-launcher-core22"
    pattern = r"full-launcher-(core|server|desktop)(\d{2})$"
    match = re.search(pattern, file)
    if match:
        return "{}{}".format(match.group(1), match.group(2))
    else:
        raise SystemError(
            "Missing image type for the name of input full "
            "launcher: {}".format(file)
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

    if os.path.exists(input_file):
        image_type = image_type_check(input_file)
    else:
        raise FileNotFoundError

    # Define output file
    input_dir = os.path.dirname(input_file)
    output_launcher = os.path.join(input_dir, "launcher-{}".format(image_type))
    output_manifest = os.path.join(
        input_dir, "manifest-{}.json".format(image_type)
    )
    output_checkbox_conf = os.path.join(
        input_dir, "checkbox-{}.conf".format(image_type)
    )

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
        launcher_sections + checkbox_conf_sections + manifest_sections)

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
        raise SystemError("The file {} does not exist."
                          .format(args.input_file))
    except Exception as e:
        raise SystemError("An error occurred: {}".format(e))


if __name__ == "__main__":
    main()
