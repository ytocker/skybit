"""Boot-level merge safety: does the game still load?

If any of these fail, the merge has broken something fundamental — a
syntax error, a missing module, a vanished asset, a constructor that
suddenly raises. Cheapest possible smoke alarm.
"""
import importlib
import pathlib

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_every_game_module_imports():
    """Walk every ``game/*.py`` and import it. Catches broken refactors,
    circular imports, syntax errors, missing dependencies."""
    failures = []
    for p in (ROOT / "game").glob("*.py"):
        if p.name == "__init__.py":
            continue
        mod_name = f"game.{p.stem}"
        try:
            importlib.import_module(mod_name)
        except Exception as e:  # pragma: no cover — only fires on regression
            failures.append(f"{mod_name}: {type(e).__name__}: {e}")
    assert not failures, "modules failed to import:\n" + "\n".join(failures)


def test_main_py_parses():
    """The top-level entry point is parseable. We don't execute it
    (it would block on the pygame event loop)."""
    src = (ROOT / "main.py").read_text()
    compile(src, "main.py", "exec")


def test_app_constructs_to_menu_state(app):
    """``App()`` reaches a sane initial state — STATE_MENU, fresh
    World, alive bird, no exception."""
    from game.scenes import STATE_MENU
    assert app.state == STATE_MENU
    assert app.world is not None
    assert app.world.bird.alive is True
    assert app.world.score == 0


def test_app_renders_one_frame(app):
    """A single render pass on the menu doesn't raise. Catches a HUD
    refactor that breaks the first paint — e.g. removed font, missing
    asset, bad color tuple."""
    app._render()


def test_all_referenced_sound_assets_exist():
    """Every sound name in ``audio._SOUND_FILES`` must have an OGG file
    on disk. Catches a rename that orphans a play_X call."""
    from game.audio import _SOUND_FILES, _SOUND_DIR
    sound_dir = pathlib.Path(_SOUND_DIR)
    missing = [n for n in _SOUND_FILES
               if not (sound_dir / f"{n}.ogg").exists()]
    assert not missing, f"missing sound assets: {missing}"


def test_font_asset_exists():
    """Every HUD scene calls ``_font(size)``, which loads
    LiberationSans-Bold.ttf. Without it, the first render raises
    ``pygame.error: file not found``."""
    font = ROOT / "game" / "assets" / "LiberationSans-Bold.ttf"
    assert font.exists(), f"font missing: {font}"


def test_kfc_logo_asset_exists():
    """The KFC power-up sprite is loaded from ``assets/kfc_logo.jpg``
    on first draw. A missing file would crash the first KFC pickup
    rather than at boot — we want to catch it here."""
    logo = ROOT / "game" / "assets" / "kfc_logo.jpg"
    assert logo.exists(), f"kfc logo missing: {logo}"
