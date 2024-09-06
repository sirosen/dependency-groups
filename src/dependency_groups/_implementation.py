import re
import sys
import typing as t
from collections import defaultdict
from collections.abc import Mapping

from packaging.requirements import Requirement


class Resolver:
    def __init__(
        self,
        dependency_groups: Mapping[str, t.Union[str, Mapping[str, str]]],
    ) -> None:
        if not isinstance(dependency_groups, Mapping):
            raise TypeError("Dependency Groups table is not a mapping")
        self.dependency_groups = _normalize_group_names(dependency_groups)
        self._resolve_cache: dict[str, tuple[str, ...]] = {}

    def resolve(self, group: str) -> tuple[str, ...]:
        """
        Resolve a dependency group to a list of requirements, as strings.

        :param group: the name of the group to resolve

        :raises TypeError: if the inputs appear to be the wrong types
        :raises ValueError: if the data does not appear to be valid dependency group
            data
        :raises LookupError: if group name is absent
        :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
        """
        if not isinstance(group, str):
            raise TypeError("Dependency group name is not a str")
        return self._resolve(group)

    def resolve_tree(
        self, group: str
    ) -> tuple[t.Union[str, "DependencyGroupInclude"], ...]:
        """
        Perform resolution, revealing the structure of the dependency groups. Returns a
        list of strings and ``DependencyGroupInclude``s.

        :param group: the name of the group to resolve

        :raises TypeError: if the inputs appear to be the wrong types
        :raises ValueError: if the data does not appear to be valid dependency group
            data
        :raises LookupError: if group name is absent
        :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
        """
        if not isinstance(group, str):
            raise TypeError("Dependency group name is not a str")
        return self._resolve_tree(group)

    def _resolve(
        self, group: str, past_groups: tuple[str, ...] = ()
    ) -> tuple[str, ...]:
        """
        This is a helper for cached resolution to strings.

        :param group: The name of the group to resolve.
        :param past_groups: The groups which were already resolved up-tree from the
            current step; used for cycle detection.
        """
        group = _normalize_name(group)
        if group in self._resolve_cache:
            return self._resolve_cache[group]

        if group in past_groups:
            raise ValueError(
                f"Cyclic dependency group include: {group} -> {past_groups}"
            )

        if group not in self.dependency_groups:
            raise LookupError(f"Dependency group '{group}' not found")

        raw_group = self.dependency_groups[group]
        if not isinstance(raw_group, list):
            raise ValueError(f"Dependency group '{group}' is not a list")

        resolved_group = []
        for item in raw_group:
            if isinstance(item, str):
                # packaging.requirements.Requirement parsing ensures that this is a
                # valid PEP 508 Dependency Specifier
                # raises InvalidRequirement on failure
                Requirement(item)
                resolved_group.append(item)
            elif isinstance(item, dict):
                if tuple(item.keys()) != ("include-group",):
                    raise ValueError(f"Invalid dependency group item: {item}")

                include_group = next(iter(item.values()))
                resolved_group.extend(
                    self._resolve(
                        include_group,
                        past_groups + (group,),
                    )
                )
            else:
                raise ValueError(f"Invalid dependency group item: {item}")

        self._resolve_cache[group] = tuple(resolved_group)
        return self._resolve_cache[group]

    def _resolve_tree(
        self, group: str
    ) -> tuple[t.Union[str, "DependencyGroupInclude"], ...]:
        """
        This is a helper for cached resolution to strings and DependencyGroupIncludes.

        :param group: The name of the group to resolve.
        :param past_groups: The groups which were already resolved up-tree from the
            current step; used for cycle detection.
        """
        group = _normalize_name(group)

        if group not in self.dependency_groups:
            raise LookupError(f"Dependency group '{group}' not found")

        raw_group = self.dependency_groups[group]
        if not isinstance(raw_group, list):
            raise ValueError(f"Dependency group '{group}' is not a list")

        resolved_group = []
        for item in raw_group:
            if isinstance(item, str):
                # packaging.requirements.Requirement parsing ensures that this is a
                # valid PEP 508 Dependency Specifier
                # raises InvalidRequirement on failure
                Requirement(item)
                resolved_group.append(item)
            elif isinstance(item, dict):
                if tuple(item.keys()) != ("include-group",):
                    raise ValueError(f"Invalid dependency group item: {item}")

                include_group = next(iter(item.values()))
                resolved_group.append(DependencyGroupInclude(include_group, self))
            else:
                raise ValueError(f"Invalid dependency group item: {item}")

        return resolved_group


class DependencyGroupInclude:
    def __init__(self, include_group: str, resolver: Resolver) -> None:
        self.include_group = include_group
        self.resolver = resolver

    def expand(self) -> tuple[str, ...]:
        return self.resolver.resolve(self.include_group)


def _normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _normalize_group_names(
    dependency_groups: Mapping[str, t.Union[str, Mapping[str, str]]]
) -> Mapping[str, t.Union[str, Mapping[str, str]]]:
    original_names = defaultdict(list)
    normalized_groups = {}

    for group_name, value in dependency_groups.items():
        normed_group_name = _normalize_name(group_name)
        original_names[normed_group_name].append(group_name)
        normalized_groups[normed_group_name] = value

    errors = []
    for normed_name, names in original_names.items():
        if len(names) > 1:
            errors.append(f"{normed_name} ({', '.join(names)})")
    if errors:
        raise ValueError(f"Duplicate dependency group names: {', '.join(errors)}")

    return normalized_groups


def resolve_tree(
    dependency_groups: Mapping[str, t.Union[str, Mapping[str, str]]], group: str, /
) -> tuple[t.Union[str, DependencyGroupInclude], ...]:
    """
    Perform resolution, revealing the structure of the dependency groups. Returns a list
    of strings and ``DependencyGroupInclude``s.

    :param dependency_groups: the parsed contents of the ``[dependency-groups]`` table
        from ``pyproject.toml``
    :param group: the name of the group to resolve

    :raises TypeError: if the inputs appear to be the wrong types
    :raises ValueError: if the data does not appear to be valid dependency group data
    :raises LookupError: if group name is absent
    :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
    """
    return Resolver(dependency_groups).resolve_tree(group)


def resolve(
    dependency_groups: Mapping[str, t.Union[str, Mapping[str, str]]], group: str, /
) -> tuple[str, ...]:
    """
    Resolve a dependency group to a list of requirements, as strings.

    :param dependency_groups: the parsed contents of the ``[dependency-groups]`` table
        from ``pyproject.toml``
    :param group: the name of the group to resolve

    :raises TypeError: if the inputs appear to be the wrong types
    :raises ValueError: if the data does not appear to be valid dependency group data
    :raises LookupError: if group name is absent
    :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
    """
    return Resolver(dependency_groups).resolve(group)


if __name__ == "__main__":
    import tomllib

    filename = "pyproject.toml"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    with open(filename, "rb") as fp:
        pyproject = tomllib.load(fp)

    dependency_groups_raw = pyproject["dependency-groups"]
    print("\n".join(resolve(pyproject["dependency-groups"], sys.argv[1])))
