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

Using `dependency_groups.resolve_tree`, you can produce a list of strings and
`dependency_groups.Dependency` objects. Those objects may be
`Include`s, which can, in turn, be expanded.

```python
from dependency_groups import resolve_tree

groups = {
  "test": ["pytest", {"include-group": "runtime"}],
  "runtime": ["flask"],
}

resolved = resolve_tree(groups, "test")  # ['pytest', Include('runtime')]
include = next(value for value in resolved if not isinstance(value, str))
include.values  # ['flask']
```

## License

`dependency-groups` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
