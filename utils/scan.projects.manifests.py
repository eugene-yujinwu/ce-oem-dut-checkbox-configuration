#!/usr/bin/env python3

"""
Scan the jobs under a directory containing Jenkins certification projects and,
for each job:
- retrieve the manifest and queue
- use an (external) mapping from queues to CIDs
- for each CID, copy the manifest to a target directory (making sure
  merging is handled appropriately if the target manifest exists)
"""

import argparse
import configparser
import json
from pathlib import Path
import re
from typing import Union
import yaml


def jobs(project: dict):
    for job_entry in project["jobs"]:
        if not isinstance(job_entry, dict):
            yield {}
        else:
            _, job = job_entry.popitem()
            if job_entry:
                raise RuntimeError
            yield job

def coerce_boolean(value: str) -> bool:
    # remove comments
    value = re.sub("\s*#.+$", "", value)
    # convert specific values to boolean
    if value.lower() in {'no', 'false', 'off'}:
        return False
    if value.lower() in {'yes', 'true', 'on'}:
        return True
    return value

def read_manifest(manifest: Union[dict, str], root: Path):
    config = configparser.ConfigParser(delimiters=('=',))
    if isinstance(manifest, dict):
        filename = manifest["file"]
        with open(root / filename) as manifest_file:
            config.read_file(manifest_file)
    else:
        config.read_string(manifest)
    return {
        section_name: {
            key: coerce_boolean(value)
            for key, value in section.items()
        }
        for section_name, section in config.items()
    }

class ManifestMergeError(ValueError):

    def __init__(self, diff1: dict, diff2: dict):
        self.diff1 = diff1
        self.diff2 = diff2

def merge_manifests(manifest_1: dict, manifest_2: dict, max_permissiveness: int = 1):

    assert max_permissiveness > 0

    true_fields_1 = set(field for field, value in manifest_1.items() if value is True)
    true_fields_2 = set(field for field, value in manifest_2.items() if value is True)

    # strict merging
    true_fields_only_1 = true_fields_1 - true_fields_2
    true_fields_only_2 = true_fields_2 - true_fields_1

    # we only merge if all fields that are true in one manifest are also
    # true in the other (remember that the default value is false);
    # anything else suggests an inconsistency
    if true_fields_only_1 or true_fields_only_2:
        if max_permissiveness == 1:
            raise ManifestMergeError(true_fields_only_1, true_fields_only_2)
    else:
        return max_permissiveness, {**manifest_1, **manifest_2}

    # true over default merging
    false_fields_1 = set(field for field, value in manifest_1.items() if value is False)
    false_fields_2 = set(field for field, value in manifest_2.items() if value is False)
    inconsistencies_1 = true_fields_1.intersection(false_fields_2)
    inconsistencies_2 = true_fields_2.intersection(false_fields_1)
    # we only merge if all fields that are true in one manifest are not
    # *explicitly* set to false in the other;
    if inconsistencies_1 or inconsistencies_2:
        if max_permissiveness == 2:
            raise ManifestMergeError(inconsistencies_1, inconsistencies_2)
    else:
        return max_permissiveness, {**manifest_1, **manifest_2}

    # the merged result comprises all fields that are true in *any* of
    # the manifests, along with any remaining false fields
    return max_permissiveness, {
        **{
            field: value
            for field, value in manifest_1.items()
            if value is True or field not in true_fields_2
        },
        **{
            field: value
            for field, value in manifest_2.items()
            if value is True or field not in true_fields_1
        }

    }


parser = argparse.ArgumentParser()
parser.add_argument("projects", type=str, help="The directory containing the project files")
parser.add_argument("mapping", type=str, help="The JSON file that holds the mappin")
parser.add_argument("target", type=str, help="The directory containing the manifest files")
parser.add_argument("--permissive", type=int, default=0, help="The level of maximum permissiveness when merging. Zero is no merging.")
args = parser.parse_args()

projects_parts = Path(args.projects).resolve().parts
root_index = projects_parts.index("hwcert-jenkins-jobs")
root = Path(*projects_parts[:root_index+1])

# pattern that matches inline import of external files;
# used to match and substitute into a form that is parsable by PyYAML
include_template = re.compile(r'(?P<field>[\w-]+):\n(?P<indent>.*)(!include-raw|!include-raw-escape): (?P<filename>.+)')

target = Path(args.target)
target.mkdir(exist_ok=True)

# load external mapping between queues and CIDs
with open(args.mapping) as queue_map_file:
    queue_map = json.load(queue_map_file)

# iterate over all project files
for project_filename in Path(args.projects).glob("**/*.yaml"):

    print(f"* project file: {project_filename}")
    with open(project_filename) as file:
        contents = file.read()

    # replace inline imports of external file with just the filename
    contents = include_template.sub(
        lambda match: f"{match.group('field')}:\n{match.group('indent')}file: {match.group('filename')}", contents
    )
    data = yaml.safe_load(contents)

    # iterate over all projects in the current file
    for project_entry in data:
        project = project_entry["project"]

        # retrieve project-level variables
        project_queue = project.get("queue")
        project_manifest = project.get("manifest")
        project_environment = project.get("checkbox_conf")

        # iterate over all jobs in the current project
        for job in jobs(project):

            # retrieve job-level variables (possibly overriding project-level)
            queue = job.get("queue", project_queue)
            manifest = job.get("manifest", project_manifest)
            environment = job.get("checkbox_conf", project_environment)

            if (not manifest and not environment) or not queue:
                continue

            if manifest is not None:
                manifest_entry_dict = read_manifest(manifest, root)
                try:
                    manifest_dict = manifest_entry_dict["manifest"]
                except KeyError:
                    manifest_dict = {}

            if environment is not None:
                environment_entry_dict = read_manifest(environment, root)
                try:
                    environment_dict = environment_entry_dict["manifest"]
                except KeyError:
                    environment_dict = {}

            if manifest_dict is None and environment_dict is None:
                continue

            # Caution! This assumes there are no (conflicting) overlaps
            manifest_dict.update(environment_dict)

            # associate the queue with the corresponding CIDs
            try:
                cids = queue_map[queue]
            except KeyError:
                continue

            # for each device in the queue:
            # copy the manifest to the target device folder
            for cid in cids:

                target_manifest_folder = target / cid
                target_manifest_filename = target_manifest_folder / "manifest.json"

                try:
                    target_manifest_folder.mkdir()
                except FileExistsError:
                    if args.permissive == 0:
                        continue
                    with open(target_manifest_filename, "r") as existing_manifest_file:
                        existing_manifest_dict = json.load(existing_manifest_file)
                        try:
                            permissiveness, updated_manifest_dict = merge_manifests(
                                existing_manifest_dict,
                                manifest_dict,
                                max_permissiveness=args.permissive
                            )
                        except ManifestMergeError as error:
                            print(f"  ! {cid}")
                            if error.diff1:
                                print(f"  + {error.diff1}")
                            if error.diff2:
                                print(f"  - {error.diff2}")
                            continue

                    if updated_manifest_dict == existing_manifest_dict:
                        print(f"  skipping update to '{target_manifest_filename}'")
                    else:
                        print(f"  merging into to '{target_manifest_filename}' ({permissiveness=})")
                        with open(target_manifest_filename, "w") as target_manifest_file:
                            json.dump(updated_manifest_dict, target_manifest_file, indent=2)
                            target_manifest_file.write('\n')

                else:
                    print(f"  writing to '{target_manifest_filename}' (new manifest)")
                    with open(target_manifest_filename, "w") as target_manifest_file:
                        json.dump(manifest_dict, target_manifest_file, indent=2)
                        target_manifest_file.write('\n')
