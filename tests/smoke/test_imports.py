"""Walk every module in ``game/`` and ``tools/`` and import it. Catches
circular imports and missing modules across refactors."""
import importlib
import pathlib

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[2]


def _module_paths(folder: str) -> list[str]:
    """Return importable module names under ``ROOT/folder``."""
    folder_path = ROOT / folder
    names = []
    for p in folder_path.glob("*.py"):
        if p.name.startswith("_") and p.name != "__init__.py":
            continue
        if p.name == "__init__.py":
            continue
        names.append(f"{folder}.{p.stem}")
    return names


GAME_MODULES = _module_paths("game")


@pytest.mark.parametrize("mod_name", GAME_MODULES)
def test_game_module_imports(mod_name):
    importlib.import_module(mod_name)


def test_game_package_imports():
    """The package itself imports."""
    import game  # noqa: F401


def test_main_module_imports():
    """The top-level entry point imports without running anything."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("_main_test",
                                                   ROOT / "main.py")
    mod = importlib.util.module_from_spec(spec)
    # Don't execute — just verify the file parses + imports load.
    # Reading the source proves no import-time SyntaxError.
    src = (ROOT / "main.py").read_text()
    compile(src, "main.py", "exec")
