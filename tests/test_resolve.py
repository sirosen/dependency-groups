import pytest

from dependency_groups import resolve


def test_empty_group():
    groups = {"test": []}
    assert resolve(groups, "test") == []


def test_str_list_group():
    groups = {"test": ["pytest"]}
    assert resolve(groups, "test") == ["pytest"]


def test_single_include_group():
    groups = {
        "test": [
            "pytest",
            {"include-group": "runtime"},
        ],
        "runtime": ["sqlalchemy"],
    }
    assert set(resolve(groups, "test")) == {"pytest", "sqlalchemy"}


def test_normalized_group_name():
    groups = {
        "TEST": ["pytest"],
    }
    assert resolve(groups, "test") == ["pytest"]


def test_no_such_group_name():
    groups = {
        "test": ["pytest"],
    }
    with pytest.raises(LookupError, match="'testing' not found"):
        resolve(groups, "testing")
