#!/usr/bin/env python3
import json
import argparse
import os
from configparser import ConfigParser
from typing import Dict, List


def dump_sections(config, sections: List):
    """
    Dump the target sections from the config file,
    Args:
        config: A configuration object for the input full-launcher
                configuration.
        sections: A list include the target sections in config.
    """
    target_sections = ConfigParser()
    for section in sections:
        if section in config.sections():
            target_sections.add_section(section)
            # Copy all key-value pairs from the original config
            for key, value in config.items(section):
                target_sections.set(section, key, value)
    return target_sections


def dump_files(config, files: Dict[str, List]):
    """
    Dumps specified sections from a configuration object into multiple output files.

    Args:
        config: A configuration object for the input full-launcher
                configuration.
        files: A dictionary where:
            - keys (str): File paths for output files.
            - values (List[str]):
                List of section names to be written to the corresponding file.


    """
    for file in files.keys():
        with open(file, "w") as f:
            launcher = dump_sections(config, files[file])
            if "manifest" in file:
                manifest_data = {}
                for key, value in launcher.items("manifest"):
                    manifest_data[key] = value.lower() == "true"
                json.dump(manifest_data, f, indent=2)
            else:
                launcher.write(f)


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
    config = ConfigParser(delimiters='=')
    config.optionxform = str
    config.read(input_file)

    files = {output_launcher: launcher_sections,
             output_manifest: manifest_sections,
             output_checkbox_conf: checkbox_conf_sections}

    dump_files(config, files)

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
