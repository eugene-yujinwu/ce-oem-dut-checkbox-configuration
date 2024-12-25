#!/usr/bin/env python3
import re
import json
import argparse
import os


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

    # Define output file names
    input_dir = os.path.dirname(input_file)
    output_launcher = os.path.join(input_dir, "launcher")
    output_manifest = os.path.join(input_dir, "manifest.json")
    output_checkbox = os.path.join(input_dir, "checkbox.conf")

    # Define the sections of the content for launcher file
    launcher_sections = ["launcher", "test plan", "test selection"]

    # Read the input file
    with open(input_file, "r") as f:
        lines = f.readlines()

    # Define patterns to match sections
    section_pattern = re.compile(r"^\[(.+)\]$")
    current_section = None
    section_data = {}

    for line in lines:
        line = line.rstrip()
        match = section_pattern.match(line)
        if match:
            current_section = match.group(1)
            section_data[current_section] = []
        elif current_section:
            section_data[current_section].append(line)

    # Write launcher file
    with open(output_launcher, "w") as f:
        f.write("#!/usr/bin/env checkbox-cli-wrapper\n")
        # check if the section launcher, test plan and test selection in
        # predefined launcher_sections
        for section in launcher_sections:
            if section in section_data:
                f.write("[{}]\n".format(section))
                for line in section_data[section]:
                    f.write(line + "\n")

    # Parse and write manifest file as JSON
    manifest_data = {}
    if "manifest" in section_data:
        for line in section_data["manifest"]:
            if "=" in line:
                key, value = map(str.strip, line.split("=", 1))
                manifest_data[key] = value.lower() == "true"

    with open(output_manifest, "w") as f:
        json.dump(manifest_data, f, indent=2)

    # Write checkbox.conf file
    with open(output_checkbox, "w") as f:
        if "environment" in section_data:
            f.write("[environment]\n")
            for line in section_data["environment"]:
                f.write(line + "\n")

    print(
        "Output files created:\n  {}\n  {}\n  {}".format(
            output_launcher, output_manifest, output_checkbox
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
