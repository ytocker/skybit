"""Identity must be deterministic — the whole point of the
nickname/color swatch is "same player → same display". Also: seeding
must not poison the global RNG for the rest of the app."""
import random

import identity


UUID_A = "11111111-1111-1111-1111-111111111111"
UUID_B = "22222222-2222-2222-2222-222222222222"


def test_nickname_is_deterministic():
    assert identity.nickname(UUID_A) == identity.nickname(UUID_A)


def test_color_is_deterministic():
    assert identity.color(UUID_A) == identity.color(UUID_A)


def test_for_device_matches_individual_helpers():
    name, hex_color = identity.for_device(UUID_A)
    assert name == identity.nickname(UUID_A)
    assert hex_color == identity.color(UUID_A)


def test_different_uuids_differ():
    # Not guaranteed by the algorithm but extremely likely. If this ever
    # collides for these two specific UUIDs, pick different test inputs.
    assert identity.nickname(UUID_A) != identity.nickname(UUID_B)
    assert identity.color(UUID_A) != identity.color(UUID_B)


def test_global_rng_state_not_poisoned():
    """We seed random.seed(uuid) inside nickname(); restoring state is
    the only thing that keeps callers' RNG behaviour intact."""
    random.seed(42)
    expected = random.random()
    random.seed(42)
    identity.nickname(UUID_A)
    assert random.random() == expected


def test_nickname_format():
    """Two words joined by a single dash, title-cased."""
    name = identity.nickname(UUID_A)
    assert "-" in name
    parts = name.split("-")
    assert len(parts) == 2
    assert all(p and p[0].isupper() for p in parts)


def test_color_format():
    """ColorHash returns '#rrggbb'."""
    c = identity.color(UUID_A)
    assert c.startswith("#")
    assert len(c) == 7
    int(c[1:], 16)  # raises ValueError if not a hex triplet
