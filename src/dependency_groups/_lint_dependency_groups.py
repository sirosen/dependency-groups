#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys

from dependency_groups import DependencyGroupResolver

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover
        tomllib = None  # type: ignore[assignment]


def main(*, argv: list[str] | None = None) -> None:
    if not tomllib:
        print(
            "Usage error: dependency-groups CLI requires tomli or Python 3.11+",
            file=sys.stderr,
        )
        sys.exit(2)

    parser = argparse.ArgumentParser(
        description=(
            "Lint Dependency Groups for validity. "
            "This will eagerly load and check all of your Dependency Groups."
        )
    )
    parser.add_argument(
        "-f",
        "--pyproject-file",
        default="pyproject.toml",
        help="The pyproject.toml file. Defaults to trying in the current directory.",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    with open(args.pyproject_file, "rb") as fp:
        pyproject = tomllib.load(fp)
    dependency_groups_raw = pyproject.get("dependency-groups", {})
    resolver = DependencyGroupResolver(dependency_groups_raw)

    errors: list[str] = []
    for groupname in resolver.dependency_groups:
        try:
            resolver.resolve(groupname)
        except (LookupError, ValueError) as e:
            errors.append(str(e))
    if errors:
        print("errors encountered while examining dependency groups:")
        for msg in errors:
            print(f"  {msg}")
        sys.exit(1)
    else:
        print("ok")
        sys.exit(0)


if __name__ == "__main__":
    main()