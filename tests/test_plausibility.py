"""
Plausibility model unit tests.

Run with: ``python -m pytest tests/`` (or ``python -m unittest tests``).
The tests exercise both the happy path and the rejection cases the
leaderboard relies on to drop forged submissions before the network
call.
"""
import unittest

from game._proof import ProofState
from game._plausibility import check, PlausibilityError, MAX_PLAUSIBLE_SCORE
from game.config import PIPE_SPACING, SCROLL_MAX


def _build_legit_run(n_pipes: int, coins_per_pipe: int = 1, triple: bool = False):
    """Reproduce what World would record for ``n_pipes`` pillars and
    ``coins_per_pipe`` regular coins per pipe. Times are spaced at the
    minimum legal interval so the run is exactly at the timing boundary."""
    proof = ProofState()
    pipe_dt = PIPE_SPACING / SCROLL_MAX
    t = 0.0
    pillars = 0
    coins = 0
    for _ in range(n_pipes):
        t += pipe_dt
        proof.record(t, 1, "pipe")
        pillars += 1
        for _ in range(coins_per_pipe):
            t += 0.05
            ds = 3 if triple else 1
            proof.record(t, ds, "coin")
            coins += 1
    return proof, t, pillars, coins


class TestPlausibility(unittest.TestCase):

    def test_happy_path(self):
        proof, t_end, pillars, coins = _build_legit_run(20, coins_per_pipe=2)
        check(
            score=proof.score(),
            pillars_passed=pillars,
            coin_count=coins,
            time_alive=t_end + 0.1,
            events=proof.events_tuple(),
            chain_hex=proof.chain_hex(),
        )  # no exception

    def test_score_inflated_against_ledger(self):
        proof, t_end, pillars, coins = _build_legit_run(5)
        with self.assertRaises(PlausibilityError) as ctx:
            check(
                score=999,                      # client-claimed score
                pillars_passed=pillars,
                coin_count=coins,
                time_alive=t_end + 0.1,
                events=proof.events_tuple(),
                chain_hex=proof.chain_hex(),
            )
        self.assertIn("score", str(ctx.exception).lower())

    def test_impossible_pacing_rejected(self):
        # 200 pillars in 5 seconds is far above SCROLL_MAX.
        proof = ProofState()
        for i in range(200):
            proof.record(i * 0.025, 1, "pipe")
        with self.assertRaises(PlausibilityError) as ctx:
            check(
                score=200,
                pillars_passed=200,
                coin_count=0,
                time_alive=5.0,
                events=proof.events_tuple(),
                chain_hex=proof.chain_hex(),
            )
        self.assertIn("timing", str(ctx.exception).lower())

    def test_chain_hash_mismatch_rejected(self):
        proof, t_end, pillars, coins = _build_legit_run(5)
        with self.assertRaises(PlausibilityError) as ctx:
            check(
                score=proof.score(),
                pillars_passed=pillars,
                coin_count=coins,
                time_alive=t_end + 0.1,
                events=proof.events_tuple(),
                chain_hex="0" * 64,            # wrong hash
            )
        self.assertIn("chain", str(ctx.exception).lower())

    def test_score_above_ceiling_rejected(self):
        # Build a legitimately-paced ledger that just happens to exceed
        # the ceiling — exercises the upper-bound short-circuit.
        proof = ProofState()
        pipe_dt = PIPE_SPACING / SCROLL_MAX
        t = 0.0
        for _ in range(MAX_PLAUSIBLE_SCORE + 5):
            t += pipe_dt
            proof.record(t, 1, "pipe")
        with self.assertRaises(PlausibilityError) as ctx:
            check(
                score=proof.score(),
                pillars_passed=MAX_PLAUSIBLE_SCORE + 5,
                coin_count=0,
                time_alive=t + 0.1,
                events=proof.events_tuple(),
                chain_hex=proof.chain_hex(),
            )
        self.assertIn("MAX_PLAUSIBLE_SCORE", str(ctx.exception))

    def test_coin_dscore_must_be_1_or_3(self):
        proof = ProofState()
        proof.record(1.0, 1, "pipe")
        proof.record(1.5, 5, "coin")          # invalid +5 coin
        with self.assertRaises(PlausibilityError) as ctx:
            check(
                score=6,
                pillars_passed=1,
                coin_count=1,
                time_alive=2.0,
                events=proof.events_tuple(),
                chain_hex=proof.chain_hex(),
            )
        self.assertIn("dscore", str(ctx.exception).lower())

    def test_replay_with_consistent_ledger_passes(self):
        # A self-consistent forgery (events match score, hash matches,
        # plausibility holds) is *not* caught — that's a server-side
        # problem outside this layer's scope. Pin this behavior so the
        # caveat in README.md doesn't silently change.
        proof, t_end, pillars, coins = _build_legit_run(3)
        check(
            score=proof.score(),
            pillars_passed=pillars,
            coin_count=coins,
            time_alive=t_end + 0.1,
            events=proof.events_tuple(),
            chain_hex=proof.chain_hex(),
        )


if __name__ == "__main__":
    unittest.main()
