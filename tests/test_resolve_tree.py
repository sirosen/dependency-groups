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
    assert includes[0].resolved_contents == ["sqlalchemy"]


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
