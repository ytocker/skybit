import os, json
from .config import HIGHSCORE_KEY, SETTINGS_KEY

_SAVE = os.path.expanduser('~/.skybit_save.json')


def _load():
    try:
        with open(_SAVE) as f:
            return json.load(f)
    except Exception:
        return {}


def _dump(d):
    try:
        with open(_SAVE, 'w') as f:
            json.dump(d, f)
    except Exception:
        pass


def load_high():
    try:
        return int(_load().get(HIGHSCORE_KEY, 0))
    except Exception:
        return 0


def save_high(v):
    d = _load()
    d[HIGHSCORE_KEY] = int(v)
    _dump(d)
