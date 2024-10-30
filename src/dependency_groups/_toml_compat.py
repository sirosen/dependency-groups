try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef, unused-ignore]
    except ImportError:  # pragma: no cover
        tomllib = None  # type: ignore[assignment, unused-ignore]

__all__ = ("tomllib",)
