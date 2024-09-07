#!/usr/bin/env python
import argparse
import sys

from dependency_groups import resolve

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

if not tomllib:
    print(
        "Usage error: dependency-groups CLI requires tomli or Python 3.11+",
        file=sys.stderr,
    )
    sys.exit(2)

parser = argparse.ArgumentParser(
    description=(
        "A dependency-groups CLI. Prints out a resolved group, newline-delimited."
    )
)
parser.add_argument("GROUP_NAME", help="The dependency group to resolve.")
parser.add_argument(
    "-f",
    "--pyproject-file",
    default="pyproject.toml",
    help="The pyproject.toml file. Defaults to trying in the current directory.",
)
args = parser.parse_args()

with open(args.pyproject_file, "rb") as fp:
    pyproject = tomllib.load(fp)

dependency_groups_raw = pyproject.get("dependency-groups", {})
print("\n".join(resolve(dependency_groups_raw, args.GROUP_NAME)))
