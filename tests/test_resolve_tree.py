import pytest

from dependency_groups import resolve_tree


def test_empty_group():
    groups = {"test": []}
    assert resolve_tree(groups, "test") == []


def test_str_list_group():
    groups = {"test": ["pytest"]}
    assert resolve_tree(groups, "test") == ["pytest"]


def test_single_include_group():
    groups = {
        "test": [
            "pytest",
            {"include-group": "runtime"},
        ],
        "runtime": ["sqlalchemy"],
    }
    tree = resolve_tree(groups, "test")
    assert [x for x in tree if isinstance(x, str)] == ["pytest"]
    includes = [x for x in tree if not isinstance(x, str)]
    assert len(includes) == 1
    assert includes[0].include_group == "runtime"
    assert includes[0].expand() == ("sqlalchemy",)


def test_multilayer_nested_include_group_expansion():
    groups = {
        "test": [
            "pytest",
            {"include-group": "runtime"},
        ],
        "runtime": [
            {"include-group": "db"},
            {"include-group": "types"},
            {"include-group": "web"},
        ],
        "db": ["sqlalchemy"],
        "types": ["useful_types"],
        "web": [
            {"include-group": "wsgi"},
            {"include-group": "schemas"},
        ],
        "wsgi": ["flask", "gunicorn"],
        "schemas": ["marshmallow", "apispec"],
    }
    tree = resolve_tree(groups, "test")

    assert len(tree) == 2
    expanded = [y for x in tree for y in ([x] if isinstance(x, str) else x.expand())]
    for dep in (
        "sqlalchemy",
        "useful_types",
        "flask",
        "gunicorn",
        "marshmallow",
        "apispec",
    ):
        assert dep in expanded


def test_malformed_group_data():
    groups = [{"test": ["pytest"]}]
    with pytest.raises(TypeError, match="Dependency Groups table is not a mapping"):
        resolve_tree(groups, "test")


def test_malformed_group_query():
    groups = {"test": ["pytest"]}
    with pytest.raises(TypeError, match="Dependency group name is not a str"):
        resolve_tree(groups, 0)


def test_no_such_group_name():
    groups = {
        "test": ["pytest"],
    }
    with pytest.raises(LookupError, match="'testing' not found"):
        resolve_tree(groups, "testing")


def test_duplicate_normalized_name():
    groups = {
        "test": ["pytest"],
        "TEST": ["nose2"],
    }
    with pytest.raises(
        ValueError,
        match=r"Duplicate dependency group names: test \((test, TEST)|(TEST, test)\)",
    ):
        resolve_tree(groups, "test")


def test_cyclic_include():
    groups = {
        "group1": [
            {"include-group": "group2"},
        ],
        "group2": [
            {"include-group": "group1"},
        ],
    }
    resolved = resolve_tree(groups, "group1")
    assert len(resolved) == 1
    include = resolved[0]
    with pytest.raises(
        ValueError,
        match=r"Cyclic dependency group include: group2 -> \('group2', 'group1'\)",
    ):
        include.expand()


def test_non_list_data():
    groups = {"test": "pytest, coverage"}
    with pytest.raises(ValueError, match="Dependency group 'test' is not a list"):
        resolve_tree(groups, "test")


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
        resolve_tree(groups, "test")
