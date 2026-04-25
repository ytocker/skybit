"""High-score persistence: top-10 leaderboard + back-compat best score.

Storage is a single JSON document hosted on JSONBin.io (or any compatible
HTTP endpoint with the same `{ "scores": [...] }` shape). Configure via
`LEADERBOARD_BIN_ID` + `LEADERBOARD_KEY` in `game/config.py`.

If the leaderboard isn't configured (empty bin id) or the network is
unreachable, `load_scores` returns `[]` and `save_scores` silently no-ops
— gameplay is never blocked by storage.

JSONBin response shape: GET returns `{"record": {"scores": [...]}, "metadata": {...}}`
PUT body: `{"scores": [...]}`
"""
import json
import sys

from game import config as _cfg

TOP_N = 10
NAME_MAX = 10

_IS_BROWSER = sys.platform == "emscripten"


# ── name + entry hygiene (unchanged contract for existing call sites) ───────

def _normalize_name(name: str) -> str:
    n = "".join(c for c in (name or "").upper() if c.isalnum() or c == " ").strip()
    if not n:
        return "???"
    return n[:NAME_MAX]


def _coerce_entries(raw) -> list[dict]:
    out = []
    for entry in raw or []:
        try:
            out.append({
                "name":  _normalize_name(entry.get("name", "")),
                "score": int(entry.get("score", 0)),
            })
        except Exception:
            continue
    out.sort(key=lambda e: -e["score"])
    return out[:TOP_N]


# ── HTTP helpers (cross-platform) ───────────────────────────────────────────

def _http_get(url: str, headers: dict) -> dict | None:
    """Synchronous GET → parsed JSON, or None on any failure."""
    if not url:
        return None
    if _IS_BROWSER:
        # Pygbag/Pyodide: a synchronous XHR via the JS layer. Async fetch is
        # nicer but we already have a sync caller (App.__init__) and a 2 s
        # timeout, so keep it simple with the blocking XHR shim.
        try:
            import js  # type: ignore
            xhr = js.XMLHttpRequest.new()
            xhr.open("GET", url, False)  # synchronous
            for k, v in headers.items():
                xhr.setRequestHeader(k, v)
            xhr.send()
            if xhr.status != 200:
                return None
            return json.loads(xhr.responseText)
        except Exception:
            return None
    # Native: stdlib urllib with a timeout.
    try:
        import urllib.request
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=_cfg.LEADERBOARD_TIMEOUT_S) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _http_put(url: str, body: dict, headers: dict) -> bool:
    """Synchronous PUT → True on 200/201, False otherwise. Never raises."""
    if not url:
        return False
    payload = json.dumps(body).encode("utf-8")
    if _IS_BROWSER:
        try:
            import js  # type: ignore
            xhr = js.XMLHttpRequest.new()
            xhr.open("PUT", url, False)
            for k, v in {**headers, "Content-Type": "application/json"}.items():
                xhr.setRequestHeader(k, v)
            xhr.send(payload.decode("utf-8"))
            return xhr.status in (200, 201)
        except Exception:
            return False
    try:
        import urllib.request
        h = {**headers, "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=payload, headers=h, method="PUT")
        with urllib.request.urlopen(req, timeout=_cfg.LEADERBOARD_TIMEOUT_S) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def _auth_headers() -> dict:
    h = {"Accept": "application/json"}
    if _cfg.LEADERBOARD_KEY:
        h["X-Master-Key"] = _cfg.LEADERBOARD_KEY
    return h


# ── public API (unchanged signatures so callers keep working) ───────────────

def load_scores() -> list[dict]:
    data = _http_get(_cfg.LEADERBOARD_GET_URL, _auth_headers())
    if not data:
        return []
    # JSONBin wraps the document in {"record": ..., "metadata": ...}.
    record = data.get("record", data)
    return _coerce_entries(record.get("scores", []))


def save_scores(scores: list[dict]) -> None:
    serial = [{"name":  _normalize_name(e["name"]),
               "score": int(e["score"])} for e in scores[:TOP_N]]
    _http_put(_cfg.LEADERBOARD_PUT_URL, {"scores": serial}, _auth_headers())


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


# ── back-compat single-int API (older callers) ──────────────────────────────

def load_highscore() -> int:
    return best_score(load_scores())


def save_highscore(score: int) -> None:
    scores = load_scores()
    new_list, _ = insert_score(scores, "---", score)
    save_scores(new_list)
