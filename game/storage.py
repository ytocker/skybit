"""High-score persistence: top-10 leaderboard + back-compat best score.

File format (JSON):
  { "scores": [ {"name": "YAN", "score": 42 }, ... ] }

All writes silently no-op on failure so a missing/locked file never crashes the game.
"""
import json
import os

from game import config as _cfg

TOP_N = 10


def _normalize_name(name: str) -> str:
    n = "".join(c for c in (name or "").upper() if c.isalnum())
    return (n + "???")[:3]


def load_scores() -> list[dict]:
    try:
        with open(_cfg.SCORES_FILE, "r") as f:
            data = json.load(f)
        raw = data.get("scores", [])
        scores = []
        for entry in raw:
            try:
                scores.append({
                    "name": _normalize_name(entry.get("name", "")),
                    "score": int(entry.get("score", 0)),
                })
            except Exception:
                continue
        scores.sort(key=lambda e: -e["score"])
        return scores[:TOP_N]
    except Exception:
        return []


def save_scores(scores: list[dict]) -> None:
    try:
        serial = [{"name": _normalize_name(e["name"]), "score": int(e["score"])} for e in scores[:TOP_N]]
        with open(_cfg.SCORES_FILE, "w") as f:
            json.dump({"scores": serial}, f)
    except Exception:
        pass


def qualifies_for_top(score: int, scores: list[dict]) -> bool:
    if score <= 0:
        return False
    if len(scores) < TOP_N:
        return True
    return score > scores[-1]["score"]


def insert_score(scores: list[dict], name: str, score: int) -> tuple[list[dict], int]:
    """Return (new_list, rank_index_0_based)."""
    entry = {"name": _normalize_name(name), "score": int(score)}
    new_list = list(scores) + [entry]
    new_list.sort(key=lambda e: -e["score"])
    new_list = new_list[:TOP_N]
    try:
        rank = new_list.index(entry)
    except ValueError:
        rank = TOP_N
    return new_list, rank


def best_score(scores: list[dict]) -> int:
    return scores[0]["score"] if scores else 0


# ── back-compat single-int API (older callers) ────────────────────────────

def load_highscore() -> int:
    return best_score(load_scores())


def save_highscore(score: int) -> None:
    scores = load_scores()
    new_list, _ = insert_score(scores, "---", score)
    save_scores(new_list)
