Resolver
========

The library provides its resolution machinery via an object oriented interface,
which allows users to explore the structure of data before or during
resolution using ``DependencyGroupInclude`` and ``DependencyGroupResolver``.

For example,

.. code-block:: python

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

Models
------

.. autoclass:: dependency_groups.DependencyGroupInclude

Resolver
--------

.. autoclass:: dependency_groups.DependencyGroupResolver

Errors
------

.. autoclass:: dependency_groups.CyclicDependencyError
