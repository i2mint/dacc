"""Smoke test: the package imports and exposes a public surface."""


def test_import():
    import dacc

    assert [n for n in dir(dacc) if not n.startswith("_")]
