# dependency-groups

An implementation of Dependency Groups ([PEP 735](https://peps.python.org/pep-0735/)).

This is a library which is able to parse dependency groups, following includes, and provide that data as output.

## Usage

`dependency_groups` expects data in the form of a dict, the loaded
`[dependency-groups]` table. Start by loading:

```python
import tomllib

with open("pyproject.toml", "rb") as fp:
    pyproject = tomllib.load(fp)

groups = pyproject["dependency-groups"]
```

Using `dependency_groups.resolve`, you can produce a list of strings, which
must be valid Dependency Specifiers.

```python
from dependency_groups import resolve

groups = {
  "test": ["pytest", {"include-group": "runtime"}],
  "runtime": ["flask"],
}

resolve(groups, "test")  # ['pytest', 'flask']
```

The library provides its resolution machinery via an object oriented interface,
which allows users to explore the structure of data before or during
resolution using `DependencyGroupInclude` and `DependencyGroupResolver`.

For example,

```python
from dependency_groups import DependencyGroupResolver

groups = {
  "test": ["pytest", {"include-group": "runtime"}],
  "runtime": ["flask"],
}

resolver = DependencyGroupResolver(groups)

# you can lookup a group without resolving it
resolver.lookup("test")  # [Requirement('pytest'), DependencyGroupInclude('runtime')]

# and resolve() produces packaging Requirements
resolver.resolve("test")  # [Requirement('pytest'), Requirement('flask')]
```

### Functional Interface

```python
def resolve(
    dependency_groups: Mapping[str, str | Mapping[str, str]], group: str, /
) -> tuple[str, ...]:
    """
    Resolve a dependency group to a tuple of requirements, as strings.

    :param dependency_groups: the parsed contents of the ``[dependency-groups]`` table
        from ``pyproject.toml``
    :param group: the name of the group to resolve

    :raises TypeError: if the inputs appear to be the wrong types
    :raises ValueError: if the data does not appear to be valid dependency group data
    :raises LookupError: if group name is absent
    :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
    """
```

### Models

Parsed Dependency Group Includes are represented by a dataclass:

```python
@dataclasses.dataclass
class DependencyGroupInclude:
    include_group: str
```

### Resolver

```python
class DependencyGroupResolver:
    """
    A resolver for Dependency Group data.

    This class handles caching, name normalization, cycle detection, and other
    parsing requirements. There are only two public methods for exploring the data:
    ``lookup()`` and ``resolve()``.

    :param dependency_groups: A mapping, as provided via pyproject
        ``[dependency-groups]``.
    """

    def lookup(self, group: str) -> tuple[Requirement | DependencyGroupInclude, ...]:
        """
        Lookup a group name, returning the parsed dependency data for that group.
        This will not resolve includes.

        :param group: the name of the group to lookup

        :raises ValueError: if the data does not appear to be valid dependency group
            data
        :raises LookupError: if group name is absent
        :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
        """

    def resolve(self, group: str) -> tuple[Requirement, ...]:
        """
        Resolve a dependency group to a list of requirements.

        :param group: the name of the group to resolve

        :raises TypeError: if the inputs appear to be the wrong types
        :raises ValueError: if the data does not appear to be valid dependency group
            data
        :raises LookupError: if group name is absent
        :raises packaging.requirements.InvalidRequirement: if a specifier is not valid
        """
```

### Errors

The following error classes are defined:

```python
class CyclicDependencyError(ValueError):
    """
    An error representing the detection of a cycle.
    """
```

### CLI Usage

`dependency-groups` provides a simple, module-level entrypoint.
It can parse a pyproject.toml file and print a dependency group's contents back
out.
Just use `python -m dependency_groups --help` for details!

## License

`dependency-groups` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
