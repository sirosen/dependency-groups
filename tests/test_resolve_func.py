import pytest

from dependency_groups import resolve


def test_empty_group():
    groups = {"test": []}
    assert resolve(groups, "test") == ()


def test_str_list_group():
    groups = {"test": ["pytest"]}
    assert resolve(groups, "test") == ("pytest",)


def test_single_include_group():
    groups = {
        "test": [
            "pytest",
            {"include-group": "runtime"},
        ],
        "runtime": ["sqlalchemy"],
    }
    assert set(resolve(groups, "test")) == {"pytest", "sqlalchemy"}


def test_sdual_include_group():
    groups = {
        "test": [
            "pytest",
        ],
        "runtime": ["sqlalchemy"],
    }
    assert set(resolve(groups, "test", "runtime")) == {"pytest", "sqlalchemy"}


def test_normalized_group_name():
    groups = {
        "TEST": ["pytest"],
    }
    assert resolve(groups, "test") == ("pytest",)


def test_malformed_group_data():
    groups = [{"test": ["pytest"]}]
    with pytest.raises(TypeError, match="Dependency Groups table is not a mapping"):
        resolve(groups, "test")


def test_malformed_group_query():
    groups = {"test": ["pytest"]}
    with pytest.raises(TypeError, match="Dependency group name is not a str"):
        resolve(groups, 0)


def test_no_such_group_name():
    groups = {
        "test": ["pytest"],
    }
    with pytest.raises(LookupError, match="'testing' not found"):
        resolve(groups, "testing")


def test_duplicate_normalized_name():
    groups = {
        "test": ["pytest"],
        "TEST": ["nose2"],
    }
    with pytest.raises(
        ValueError,
        match=r"Duplicate dependency group names: test \((test, TEST)|(TEST, test)\)",
    ):
        resolve(groups, "test")


def test_cyclic_include():
    groups = {
        "group1": [
            {"include-group": "group2"},
        ],
        "group2": [
            {"include-group": "group1"},
        ],
    }
    with pytest.raises(
        ValueError,
        match=(
            "Cyclic dependency group include while resolving group1: "
            "group1 -> group2, group2 -> group1"
        ),
    ):
        resolve(groups, "group1")


def test_cyclic_include_many_steps():
    groups = {}
    for i in range(100):
        groups[f"group{i}"] = [{"include-group": f"group{i+1}"}]
    groups["group100"] = [{"include-group": "group0"}]
    with pytest.raises(
        ValueError,
        match="Cyclic dependency group include while resolving group0:",
    ):
        resolve(groups, "group0")


def test_cyclic_include_self():
    groups = {
        "group1": [
            {"include-group": "group1"},
        ],
    }
    with pytest.raises(
        ValueError,
        match=(
            "Cyclic dependency group include while resolving group1: "
            "group1 includes itself"
        ),
    ):
        resolve(groups, "group1")


def test_cyclic_include_ring_under_root():
    groups = {
        "root": [
            {"include-group": "group1"},
        ],
        "group1": [
            {"include-group": "group2"},
        ],
        "group2": [
            {"include-group": "group1"},
        ],
    }
    with pytest.raises(
        ValueError,
        match=(
            "Cyclic dependency group include while resolving root: "
            "group1 -> group2, group2 -> group1"
        ),
    ):
        resolve(groups, "root")


def test_non_list_data():
    groups = {"test": "pytest, coverage"}
    with pytest.raises(ValueError, match="Dependency group 'test' is not a list"):
        resolve(groups, "test")


@pytest.mark.parametrize(
    "item",
    (
        {},
        {"foo": "bar"},
        {"include-group": "testing", "foo": "bar"},
        object(),
    ),
)
def test_unknown_object_shape(item):
    groups = {"test": [item]}
    with pytest.raises(ValueError, match="Invalid dependency group item:"):
        resolve(groups, "test")
