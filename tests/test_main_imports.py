# tests/test_main_imports.py


def test_main_module_imports_without_litellm():
    import importlib

    m = importlib.import_module("main")
    assert hasattr(m, "initialize_system")
    assert hasattr(m, "run_trading_cycle")
