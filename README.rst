Dependency Groups
=================

An implementation of Dependency Groups (`PEP 735 <https://peps.python.org/pep-0735/>`_).

This is a library which is able to parse dependency groups, following includes, and provide that data as output.

Interfaces
----------

``dependency-groups`` provides the following:

- A ``DependencyGroupResolver`` which implements efficient resolution of
  dependency groups

- A ``resolve()`` function which converts a dependency group name to a list of
  strings (powered by the resolver)

- Three CLI commands:

  - ``python -m dependency_groups GROUPNAME`` prints a dependency group's
    contents

  - ``lint-dependency-groups`` loads all dependency groups to check for
    correctness

  - ``pip-install-dependency-groups GROUPNAME...`` wraps a ``pip`` invocation
    to install the contents of a dependency group

- A pre-commit hooks which runs ``lint-dependency-groups``

Documentation
-------------

Full documentation is available on `the Dependency Groups doc site <https://dependency-groups.readthedocs.io/>`_.
