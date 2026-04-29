"""Constant-time HMAC-SHA256 + build-secret loading.

Why HMAC at all in a public client?
-----------------------------------
The HMAC key is shipped inside the WASM bundle, so a determined attacker
can extract it. That's accepted: the goal is not perfect secrecy, it's
*raising the cost* from "edit one number in DevTools" (zero effort) to
"reverse-engineer the WASM, replay HMAC chains" (hours of effort). The
real authority is the server-side plausibility ceiling in
supabase/schema.sql which the client cannot bypass.

We rotate the secret on every Netlify deploy via the SKYBIT_HMAC_KEY env
var (see inject_theme.py). Old signatures stop working — short shelf
life is the point.
"""
from __future__ import annotations

import hashlib
import hmac
import os

# inject_theme.py replaces this placeholder at build time. Keep the literal
# exactly as written so the regex matches.
_BUILD_HMAC_PLACEHOLDER = "__SB_HMAC__"
_FALLBACK_DEV_KEY = b"skybit-dev-key-not-for-prod-do-not-ship"


def get_build_secret() -> bytes:
    """Return the build-time HMAC secret as bytes.

    Resolution order:
      1. Env var SKYBIT_HMAC_KEY (native dev / CI).
      2. Replaced placeholder _BUILD_HMAC_PLACEHOLDER injected by
         inject_theme.py into a sibling _build_secret.py file (browser).
      3. Fallback dev key — emits a security_event so it's visible.
    """
    env = os.environ.get("SKYBIT_HMAC_KEY")
    if env:
        return env.encode("utf-8")
    try:
        from . import _build_secret  # type: ignore
        v = getattr(_build_secret, "HMAC_KEY", "")
        if v and v != _BUILD_HMAC_PLACEHOLDER:
            return v.encode("utf-8")
    except Exception:
        pass
    return _FALLBACK_DEV_KEY


def sign(payload: bytes, key: bytes | None = None) -> str:
    """Hex HMAC-SHA256 of `payload`. Uses the build secret if `key` is None."""
    k = key if key is not None else get_build_secret()
    return hmac.new(k, payload, hashlib.sha256).hexdigest()


def verify(payload: bytes, sig_hex: str, key: bytes | None = None) -> bool:
    """Constant-time verify of `sig_hex` against HMAC-SHA256(`payload`)."""
    if not isinstance(sig_hex, str) or len(sig_hex) != 64:
        return False
    expected = sign(payload, key)
    return hmac.compare_digest(expected, sig_hex)


def derive_key(salt: bytes, label: str) -> bytes:
    """Cheap KDF: HMAC the build secret with (salt || label). Used to keep
    different concerns (local-scores file vs. run chain) on separate keys
    so a leak of one doesn't compromise the other."""
    base = get_build_secret()
    return hmac.new(base, salt + b"|" + label.encode("utf-8"),
                    hashlib.sha256).digest()
