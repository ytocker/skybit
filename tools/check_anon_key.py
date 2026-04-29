"""Build-time guard: fail loudly if the deployed bundle leaks a Supabase
service-role key.

Skybit's HTML embeds the Supabase *anon* key (read-only-ish, RLS-gated). The
service-role key bypasses RLS and must NEVER ship to clients. This script
walks the post-build directory, finds anything JWT-shaped, decodes the
payload, and aborts the build if any token claims `"role":"service_role"`.

Run after pygbag + inject_theme.py:

    python tools/check_anon_key.py build/web

Exits 0 if clean, 1 if a service-role key (or any obvious secret-shaped
literal) is found.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
from pathlib import Path

# JWT pattern: three base64url segments separated by dots. Loose match — we
# refine by trying to decode the payload below.
_JWT_RE = re.compile(rb"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")

# Env-var names that must never appear inside the build output.
_FORBIDDEN_ENV_REFERENCES = (
    b"SUPABASE_SERVICE_ROLE_KEY",
    b"SERVICE_ROLE_KEY",
    b"SKYBIT_HMAC_KEY",  # build-time only; the placeholder is replaced
)

_SCAN_EXTENSIONS = {".html", ".htm", ".js", ".mjs", ".json", ".css", ".txt", ".map"}


def _b64url_decode(seg: bytes) -> bytes:
    pad = b"=" * (-len(seg) % 4)
    return base64.urlsafe_b64decode(seg + pad)


def _jwt_role(token: bytes) -> str | None:
    try:
        _, payload, _ = token.split(b".")
        data = json.loads(_b64url_decode(payload))
    except Exception:
        return None
    role = data.get("role")
    return role if isinstance(role, str) else None


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _SCAN_EXTENSIONS:
            continue
        try:
            blob = path.read_bytes()
        except OSError:
            continue
        for match in _JWT_RE.finditer(blob):
            token = match.group(0)
            role = _jwt_role(token)
            if role and role != "anon":
                findings.append(f"{path}: JWT with role={role!r} (must be 'anon' or absent)")
        for needle in _FORBIDDEN_ENV_REFERENCES:
            if needle in blob:
                findings.append(f"{path}: contains forbidden literal {needle.decode()!r}")
    return findings


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("build/web")
    if not target.exists():
        print(f"check_anon_key: target {target} does not exist (skipping)", file=sys.stderr)
        return 0
    findings = scan(target)
    if findings:
        print("check_anon_key: SECURITY FAIL — service-role / secret-shaped token in build", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"check_anon_key: OK — scanned {target}, no service-role tokens found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
