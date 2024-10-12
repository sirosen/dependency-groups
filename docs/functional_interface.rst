Functional Interface
====================

.. autofunction:: dependency_groups.resolve

Example usage:

.. code-block:: toml

    # in pyproject.toml
    [dependency-groups]
    test = ["pytest", {include-group = "runtime"}]
    runtime = ["flask"]

.. code-block:: python

    from dependency_groups import resolve
    import tomllib

    with open("pyproject.toml", "rb") as fp:
        pyproject = tomllib.load(fp)

    groups = pyproject["dependency-groups"]

    resolve(groups, "test")  # ['pytest', 'flask']
