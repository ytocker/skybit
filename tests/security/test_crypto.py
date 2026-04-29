"""HMAC + key-derivation tests."""
import os
import pytest

from game.security import crypto


def test_sign_then_verify_roundtrip():
    key = os.urandom(32)
    body = b"hello-skybit"
    sig = crypto.sign(body, key)
    assert len(sig) == 64
    assert crypto.verify(body, sig, key)


def test_tampered_body_rejected():
    key = os.urandom(32)
    sig = crypto.sign(b"original", key)
    assert not crypto.verify(b"tampered", sig, key)


def test_wrong_key_rejected():
    sig = crypto.sign(b"x", b"key1")
    assert not crypto.verify(b"x", sig, b"key2")


def test_short_signature_rejected():
    assert not crypto.verify(b"x", "abc123", b"key")


def test_non_hex_signature_rejected():
    assert not crypto.verify(b"x", "z" * 64, b"key")


def test_derive_key_separation():
    salt = os.urandom(16)
    a = crypto.derive_key(salt, "label-a")
    b = crypto.derive_key(salt, "label-b")
    assert a != b


def test_get_build_secret_falls_back():
    # When no env / no _build_secret module, returns the dev fallback bytes.
    os.environ.pop("SKYBIT_HMAC_KEY", None)
    secret = crypto.get_build_secret()
    assert isinstance(secret, bytes) and len(secret) > 0


def test_env_overrides_fallback(monkeypatch):
    monkeypatch.setenv("SKYBIT_HMAC_KEY", "env-key-value")
    assert crypto.get_build_secret() == b"env-key-value"
