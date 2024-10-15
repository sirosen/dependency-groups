CHANGELOG
=========

Unreleased
----------

1.0.0
-----

- Update metadata to 1.0.0 and "Production" status
- Support Python 3.13

0.3.0
-----

- Add a new command, ``pip-install-dependency-groups``, which is capable of
  installing dependency groups by invoking ``pip``

0.2.2
-----

- The pre-commit hook sets ``pass_filenames: false``
- The error presentation in the lint CLI has been improved

0.2.1
-----

- Bugfix to pre-commit config

0.2.0
-----

- Add a new CLI component, ``lint-dependency-groups``, which can be used to lint
  dependency groups.
- Provide a pre-commit hook, named ``lint-dependency-groups``

0.1.1
-----

- Fix a bug in cycle detection for nontrivial cycles

0.1.0
-----

- Initial Release
