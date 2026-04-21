"""High-score persistence. Tolerant of web/pygbag filesystem quirks."""
import json
import os

from game.config import SAVE_FILE


def load_highscore() -> int:
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return int(data.get("best", 0))
    except Exception:
        return 0


def save_highscore(score: int) -> None:
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({"best": int(score)}, f)
    except Exception:
        pass
