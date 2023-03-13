#!/usr/bin/env python3

import subprocess
import os
import sys
import json
import argparse
import configparser


GIT_URL="https://git.launchpad.net/~oem-qa/+git"
GIT_REPO="ce-oem-dut-checkbox-configuration"


def _issue_command(cmd):
    proc = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        shell = True
    )
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        print(stderr.decode("utf-8"))

    return proc.returncode, stdout.decode("utf-8")


def checkbox_conf_update(checkbox_env, checkbox_file):
    print("## Check and merge checkbox config")
    config=configparser.ConfigParser()
    config.optionxform = lambda option: option
    if os.path.exists(checkbox_file):
        config.read(checkbox_file)

    # Replace new line for user-input string
    checkbox_env = checkbox_env.replace("\\n", "\n")

    if checkbox_env:
        print("merging checkbox environ variable..")
        config.read_string(checkbox_env)

    print("update to {}".format(checkbox_file))
    with open(checkbox_file, "w") as fp:
        config.write(fp)


def manifest_update(manifest_env, manifest_file, default_file):
    print("## Check and merge manifest info")
    dict_content = dict()
    if os.path.exists(manifest_file):
        with open(manifest_file, "r") as fp:
            dict_content.update(json.load(fp))
    if manifest_env:
        print("merging manifest environ variable..")
        dict_content.update(json.loads(manifest_env))

    if not dict_content:
        print("manifest info is empty, applying default manifest..")
        with open(default_file, "r") as fp:
            default_manifest = json.load(fp)
        dict_content.update(default_manifest)

    print("update to {}".format(manifest_file))
    with open(manifest_file, "wt") as fp:
        json.dump(dict_content, fp, sort_keys=True, indent=2)


def update_repo(cid, branch):
    print("## Check difference via git status")
    returncode, output = _issue_command("git status -s")
    if returncode != 0:
        raise SystemExit("Error: Failed to sync with git repo")
    output = output.split("\n")
    commit_files = " ".join([tmp[3:] for tmp in output if cid in tmp])

    if commit_files:
        print("## Update git repo to latest version")
        commit_msg = "Update content for CID {}".format(cid)
        cmd = "git add {}; git commit -m '{}'; git push origin {}".format(
            commit_files, commit_msg, branch
        )
        returncode, output = _issue_command(cmd)
        if returncode != 0:
            raise SystemExit("Error: Failed to sync with git repo")
        else:
            print("Commit latest changes to {} branch".format(branch))
    else:
        print("No changes for CID {}".format(cid))


def get_repo(download, branch):
    if download:
        full_url = "{}/{}".format(GIT_URL, GIT_REPO)
        print("## Clone code from {}".format(full_url))
        returncode, output = _issue_command(
            "git clone {} -b {} --depth 1".format(full_url, branch)
        )
        print(output)
        if returncode != 0:
            raise SystemExit(
                ("Error: Failed to clone code from {}!".format(full_url),
                 "Please check your connections")
            )

    print("## Update git repo to latest version")
    returncode, output = _issue_command("git pull origin {}".format(branch))
    print(output)
    if returncode != 0:
        raise SystemExit("Error: Failed to update git repo!")


def parse_arguments():
    description = (
        "This utility is for merge a checkbox manifest and configuration"
        " for PC projects"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c", "--cid", required=True,
        help="update checkbox manifest configuration for this CID"
    )
    parser.add_argument(
        "--manifest-data", default="",
        help="Manifest data (with JSON format string)"
    )
    parser.add_argument(
        "--checkbox-conf-data", default="",
        help="Checkbox config data (with Config format string)"
    )
    parser.add_argument(
        "-b",
        "--branch",
        default="main",
        help="Git branch of manifest repository"
    )
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Clone latest {} to local system".format(GIT_REPO)
    )
    parser.add_argument(
        "-p",
        "--path",
        default=os.getcwd(),
        help=(
            "The path of checkbox manifest repo in local system. "
            "Default value is current working directory"
        )
    )
    parser.add_argument(
        "-t",
        "--project-type",
        default="pc",
        choices=["pc", "iot"],
        help="The type of enablement project, default is pc"
    )
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_arguments()

    root_path = path = os.path.abspath(args.path)
    print("## Switching to {}".format(root_path))
    os.chdir(root_path)
    get_repo(args.download, args.branch)

    for sub_dir in [args.project_type, args.cid]:
        p_list = os.path.split(path)
        path = os.path.join(path, sub_dir) if sub_dir not in p_list else path

    if not os.path.exists(path):
        print("## CID folder not exists, creating {} folder".format(args.cid))
        os.makedirs(path)

    print("## Switching to {} folder for DUT".format(path))
    os.chdir(path)

    default_manifest = path.replace(args.cid, "default/manifest.json")
    manifest_update(args.manifest_data, "manifest.json", default_manifest)
    if args.checkbox_conf_data:
        checkbox_conf_update(args.checkbox_conf_data, "checkbox.conf")

    print("## Switching to {}".format(root_path))
    os.chdir(root_path)
    update_repo(args.cid, args.branch)


if __name__ == "__main__":
    main()
