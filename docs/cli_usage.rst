CLI Usage
=========

There are three CLI tools provided by ``dependency-groups``.

Module Usage
------------

``dependency-groups`` provides a simple, module-level entrypoint.
It can parse a pyproject.toml file and print a dependency group's contents back
out.
Just use ``python -m dependency_groups --help`` for details!

Installer
---------

``dependency-groups`` includes a ``pip`` wrapper, ``pip-install-dependency-groups``.

Usage is simple, just ``pip-install-dependency-groups groupname`` to install!

Use ``pip-install-dependency-groups --help`` for more details.

Linter
------

``dependency-groups`` includes a linter, ``lint-dependency-groups``, as a separate
CLI entrypoint.

Use ``lint-dependency-groups --help`` for details.

The ``lint-dependency-groups`` CLI is also available as a pre-commit hook:

.. code-block:: yaml

    repos:
      - repo: https://github.com/sirosen/dependency-groups
        rev: 0.3.0
        hooks:
          - id: lint-dependency-groups
