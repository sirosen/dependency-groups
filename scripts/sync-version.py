"""
Update references to this project's version to match what's in the canary workflow.

When a new project version is tagged in git,
Dependabot will eventually submit a PR to update the `canary.yaml` workflow,
which contains a reference to the project version as-tagged in git.
The PR will trigger a pre-commit.ci run that will run this script.
This script will find the current version in `canary.yaml`
and copy that version to other locations.
"""

import pathlib
import re
import sys
import typing as t

canary_file = pathlib.Path(".github/workflows/canary.yaml")
uses_line_pattern = re.compile(
    r"""^ +uses: *(["']?).+?@(?P<version>.+?)\1$""",
    flags=re.MULTILINE,
)

repo_line_pattern = re.compile(
    r"""^.*repo: *(["']?)https://github.com/sirosen/dependency-groups\1$""",
    flags=re.MULTILINE,
)
rev_line_pattern = re.compile(
    r"""^.+rev: *(["']?)(?P<version>.+?)\1$""",
    flags=re.MULTILINE,
)

readme = pathlib.Path("README.md")
pre_commit_config = pathlib.Path(".pre-commit-config.yaml")


def get_version_in_canary() -> str:
    if not canary_file.is_file():
        raise FileNotFoundError(canary_file)
    content = canary_file.read_text()
    match = uses_line_pattern.search(content)
    if match is None:
        raise ValueError(f"No version found in '{canary_file.name}'")
    return match.group("version")


def replacer(new_version: str) -> t.Callable[[re.Match[str]], str]:
    def re_sub_replacer(match: re.Match[str]) -> str:
        old_version = match.group("version")
        return match.group().replace(old_version, new_version)

    return re_sub_replacer


def update_pre_commit_line(path: pathlib.Path, version: str) -> int:
    if not path.is_file():
        raise FileNotFoundError(readme)
    content = path.read_text()
    match = repo_line_pattern.search(content)
    if match is None:
        raise ValueError(f"No 'repo:' found in {path}")
    pre_content, remaining_content = content[: match.end()], content[match.end() :]
    updated_content = rev_line_pattern.sub(replacer(version), remaining_content, 1)
    new_content = pre_content + updated_content
    if content == new_content:
        return 0

    path.write_text(pre_content + updated_content)
    return 1


def main() -> int:
    rc = 0
    new_version = get_version_in_canary()

    rc |= update_pre_commit_line(readme, new_version)
    rc |= update_pre_commit_line(pre_commit_config, new_version)

    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError) as error:
        print(f"{error.__class__.__name__}: {error.args[0]}")
        sys.exit(2)
