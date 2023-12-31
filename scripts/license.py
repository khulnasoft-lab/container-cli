#!/usr/bin/env python

import datetime
import os
import sys

license_text = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


def license_file(path, comment_prefix):
    validate_only = globals()["validate_only"]

    # Parse Copyright statements
    with open(path, "r") as f:
        lines = list(f.readlines())
    copyrights = {}
    copyrights_end = None
    for i in range(len(lines)):
        words = lines[i].split()
        if len(words) > 4 and words[0] == comment_prefix and words[1] == "©":
            years = words[2]
            start_year = years
            end_year = years
            if "-" in years:
                [start_year, end_year] = years.split("-")
            holder = " ".join(words[3:])
            copyrights[holder] = (start_year, end_year)
        elif len(copyrights) > 0 and copyrights_end is None:
            copyrights_end = i

    # Insert Khulnasoft copyright
    vulnmap = "Khulnasoft Limited All rights reserved."
    year = str(datetime.datetime.today().year)
    changed = False
    if vulnmap in copyrights:
        if copyrights[vulnmap][1] != year:
            copyrights[vulnmap] = (copyrights[vulnmap][0], year)
            changed = True
    else:
        copyrights[vulnmap] = (year, year)
        changed = True

    if changed:
        if validate_only:
            print(f"{path}: missing or not updated license found!", file=sys.stderr)
            globals()["exit_code"] = 2
        else:
            write_copyright(path, comment_prefix, copyrights, copyrights_end, lines)
    else:
        if not validate_only:
            print(f"{path}: up to date, skipping", file=sys.stderr)


def write_copyright(path, comment_prefix, copyrights, copyrights_end, lines):
    new_lines = []
    copyrights_list = reversed(sorted(list(copyrights.items()), key=lambda x: x[1][1]))
    for (holder, (start_year, end_year)) in copyrights_list:
        years = start_year if start_year == end_year else f"{start_year}-{end_year}"
        new_lines.append(f"{comment_prefix} © {years} {holder}\n")
    if copyrights_end is not None:
        new_lines += lines[copyrights_end:]
    else:
        new_lines.append(f"{comment_prefix}\n")
        for line in license_text.splitlines():
            if line == "":
                new_lines.append(f"{comment_prefix}\n")
            else:
                new_lines.append(f"{comment_prefix} {line}\n")
        new_lines.append("\n")
        new_lines += lines
    with open(path, "w") as f:
        f.write("".join(new_lines))
    print(f"{path}: updated", file=sys.stderr)


ignores = [
    'internal/workflows/sbom/interfaces_mocks.go'
]


def license_tree(dir):
    for root, dirs, files in os.walk(dir):
        for name in files:
            path = os.path.join(root, name)

            if any(path.startswith(ignore) for ignore in ignores):
                continue

            _, ext = os.path.splitext(name)
            if ext == ".go":
                license_file(path, "//")
            elif ext == ".rego":
                license_file(path, "#")
            elif ext == ".tf":
                license_file(path, "#")
            elif ext == ".yaml" or ext == ".yml":
                license_file(path, "#")


def main():
    # init globals
    globals()["validate_only"] = True if (len(sys.argv) > 1 and sys.argv[1] == '--validate') else False
    globals()["exit_code"] = 0

    # folders to scan
    license_tree("internal")
    license_tree("pkg")

    exit(globals()["exit_code"])


main()
