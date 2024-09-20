#!/usr/bin/env python3

"""
Scan the jobs under a directory containing Jenkins certification projects,
collect all the (unique) queues involved in these jobs and
store the result in a JSON file.
"""

import argparse
import json
import re
from pathlib import Path
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


parser = argparse.ArgumentParser()
parser.add_argument("projects", type=str, help="The directory containing the project files")
parser.add_argument("output", type=str, help="The output JSON file that holds the queue list")
args = parser.parse_args()

# pattern that matches inline import of external files;
# used to match and substitute into a form that is parsable by PyYAML
include_template = re.compile(r'(?P<field>[\w-]+):\n.*(include-raw|include-raw-escape): (?P<filename>.+)')

# result: a set of queues
queues = set()

# iterate over all project files
for project_filename in Path(args.projects).glob("**/*.yaml"):

    print(f"- project file = {project_filename}")
    with open(project_filename) as file:
        contents = file.read()

    # replace inline imports of external file with just the filename
    contents = include_template.sub(
        lambda match: f"{match.group('field')}: {match.group('filename')}", contents
    )
    data = yaml.safe_load(contents)

    # iterate over all projects in the current file
    for project_entry in data:
        project = project_entry["project"]

        # retrieve project-level variables
        project_queue = project.get("queue")

        # iterate over all jobs in the current project
        for job in jobs(project):

            # retrieve job-level variables (possibly overriding project-level)
            queue = job.get("queue", project_queue)
            if queue is None:
                continue

            # include queue in the result
            if queue not in queues:
                print(f"  {queue=}")
                queues.add(queue)

with open(args.output, "w") as file:
    json.dump(list(queues), file, indent=2)
    file.write('\n')
