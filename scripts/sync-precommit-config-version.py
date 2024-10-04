#!/usr/bin/env python
"""
Update the reference to this project's version in `.pre-commit-config.yaml`.
Match what's in the canary workflow.

When a new project version is tagged in git, Dependabot will eventually submit
a PR to update the `canary.yaml` workflow, which contains a reference to the
project version as-tagged in git.

The PR will trigger a pre-commit.ci run that will run this script.
This script will find the current version in `canary.yaml` and copy that
version to `.pre-commit-config.yaml`.

It's desirable for this script to run independently from `bump-version.py`
because the pre-commit version cannot update until the tag is published.
"""

import pathlib
import re
import sys

CANARY_FILE = pathlib.Path(".github/workflows/canary.yaml")

USES_LINE_PATTERN = re.compile(
    r'^\s+uses: "[^@]+@(\d+\.\d+\.\d+)"$', flags=re.MULTILINE
)

REPO_LINE_PATTERN = re.compile(
    r"""^\s*- repo: https://github\.com/sirosen/dependency-groups$""",
    flags=re.MULTILINE,
)
REV_LINE_PATTERN = re.compile(
    r"^.+rev: (\d+\.\d+\.\d+)$",
    flags=re.MULTILINE,
)


def get_version_in_canary() -> str:
    if not CANARY_FILE.is_file():
        raise FileNotFoundError(CANARY_FILE)
    content = CANARY_FILE.read_text()
    match = USES_LINE_PATTERN.search(content)
    if match is None:
        raise ValueError(f"No version found in '{CANARY_FILE.name}'")
    return match.group(1)


def update_pre_commit_line(version: str) -> int:
    path = pathlib.Path(".pre-commit-config.yaml")

    def re_replacer(match: re.Match[str]) -> str:
        old_version = match.group(1)
        return match.group().replace(old_version, version)

    content = path.read_text()
    match = REPO_LINE_PATTERN.search(content)
    if match is None:
        raise ValueError(f"No 'repo:' found in {path}")

    pre_content, remaining_content = content[: match.end()], content[match.end() :]
    updated_content = REV_LINE_PATTERN.sub(re_replacer, remaining_content, 1)
    new_content = pre_content + updated_content
    if content == new_content:
        return 0

    path.write_text(pre_content + updated_content)
    return 1


def main() -> int:
    new_version = get_version_in_canary()
    return update_pre_commit_line(new_version)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError) as error:
        print(f"{error.__class__.__name__}: {error.args[0]}")
        sys.exit(2)
