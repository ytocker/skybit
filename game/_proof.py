"""
Tamper-evident proof of play.

Parallel to the visible ``World.score`` integer, this module keeps an
append-only ledger of every scoring event in the run and a rolling
SHA-256 chain hash over the ledger. The two together are what the
leaderboard submission carries — not the raw ``world.score`` attribute,
which is mutable from any JS console.

Why a separate ledger:
    A casual cheat is to open DevTools and do
    ``pyodide.globals.get('app').world.score = 99999``. That mutation
    only touches the visible counter; ``ProofState`` is unaffected. The
    submission path reads ``ProofState.score()`` (computed from the
    events list) and runs a plausibility check against the events. The
    forgery is rejected before the network call.

Limits:
    Both halves of this module live in the same JS context as the
    attacker. A determined reverse engineer can locate this class via
    Pyodide's ``__dict__`` inspection, monkey-patch ``record``, or hand-
    construct a ledger that passes the plausibility check. We aren't
    trying to defeat that — just the one-line console paste.
"""
import hashlib
import struct
import uuid


class ProofState:
    __slots__ = ("_events", "_chain", "_run_id")

    def __init__(self) -> None:
        self._events: list[tuple[float, int, str]] = []
        # Seed the chain with 32 zero bytes so the very first event still
        # mixes into a non-degenerate hash.
        self._chain: bytes = b"\x00" * 32
        self._run_id: str = str(uuid.uuid4())

    def record(self, t_alive: float, dscore: int, kind: str) -> None:
        """Append one scoring event and roll the chain hash forward.

        ``kind`` is "pipe" for a pillar-pass or "coin" for a coin pickup.
        ``dscore`` is +1 (pipe / regular coin) or +3 (coin during a triple
        window). The plausibility check enforces those bounds."""
        # Quantize t_alive to milliseconds before hashing so floating-
        # point jitter in the integration step doesn't break the chain.
        t_ms = int(round(float(t_alive) * 1000))
        kind_b = kind.encode("ascii")[:8]
        kind_b = kind_b + b"\x00" * (8 - len(kind_b))
        packed = struct.pack(">qIB", t_ms, int(dscore), len(kind)) + kind_b
        self._events.append((float(t_alive), int(dscore), str(kind)))
        self._chain = hashlib.sha256(self._chain + packed).digest()

    def score(self) -> int:
        """Sum of dscores from the ledger. Source of truth for submission."""
        return sum(e[1] for e in self._events)

    def events_tuple(self) -> tuple[tuple[float, int, str], ...]:
        """Immutable copy of the event list."""
        return tuple(self._events)

    def chain_hex(self) -> str:
        return self._chain.hex()

    def run_id(self) -> str:
        return self._run_id

    def event_count(self, kind: str) -> int:
        return sum(1 for e in self._events if e[2] == kind)
