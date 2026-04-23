# tests/test_main_imports.py
"""Smoke test: importar `main` exige dependências de runtime (ex.: apscheduler). Usar `uv run pytest`."""


def test_main_module_imports_without_litellm():
    import importlib

    m = importlib.import_module("main")
    assert hasattr(m, "initialize_system")
    assert hasattr(m, "run_trading_cycle")
