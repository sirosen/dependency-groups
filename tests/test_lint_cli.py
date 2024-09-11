import dataclasses

import pytest


@dataclasses.dataclass
class CLIResult:
    code: int
    stdout: str
    stderr: str


@pytest.fixture
def run(capsys):
    from dependency_groups._lint_dependency_groups import main as cli_main

    def _run(*argv):
        try:
            cli_main(argv=[str(arg) for arg in argv])
            rc = 0
        except SystemExit as e:
            rc = e.code

        stdio = capsys.readouterr()
        return CLIResult(rc, stdio.out, stdio.err)

    return _run


def test_lint_no_groups_ok(run, tmp_path):
    tomlfile = tmp_path / "pyproject.toml"
    tomlfile.write_text("[project]\n")

    res = run("-f", tomlfile)
    assert res.code == 0
    assert res.stdout == "ok\n"
    assert res.stderr == ""


def test_lint_bad_group_item(run, tmp_path):
    tomlfile = tmp_path / "pyproject.toml"
    tomlfile.write_text(
        """\
[dependency-groups]
foo = [{badkey = "value"}]
"""
    )

    res = run("-f", tomlfile)
    assert res.code == 1
    assert (
        res.stdout
        == """\
errors encountered while examining dependency groups:
  ValueError: Invalid dependency group item: {'badkey': 'value'}
"""
    )
    assert res.stderr == ""


def test_no_toml_failure(run, tmp_path, monkeypatch):
    monkeypatch.setattr("dependency_groups._lint_dependency_groups.tomllib", None)

    tomlfile = tmp_path / "pyproject.toml"
    tomlfile.write_text("")

    res = run("-f", tomlfile)
    assert res.code == 2
    assert "requires tomli or Python 3.11+" in res.stderr


def test_dependency_groups_list_format(run, tmp_path):
    tomlfile = tmp_path / "pyproject.toml"
    tomlfile.write_text("[[dependency-groups]]")

    res = run("-f", tomlfile)
    assert res.code == 1
    assert (
        res.stdout
        == """\
errors encountered while examining dependency groups:
  TypeError: Dependency Groups table is not a mapping
"""
    )
    assert res.stderr == ""
