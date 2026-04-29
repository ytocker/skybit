"""Build-leak guard tests."""
import base64
import json
from pathlib import Path

from tools import check_anon_key


def _jwt(role: str) -> str:
    header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"role": role}).encode()).rstrip(b"=").decode()
    sig = "AAAAAAAA"  # 8 chars, satisfies the regex; payload decode is what matters
    return f"{header}.{payload}.{sig}"


def test_anon_token_passes(tmp_path: Path):
    f = tmp_path / "index.html"
    f.write_text(f"<script>var k='{_jwt('anon')}';</script>")
    assert check_anon_key.scan(tmp_path) == []


def test_service_role_token_fails(tmp_path: Path):
    f = tmp_path / "index.html"
    f.write_text(f"<script>var k='{_jwt('service_role')}';</script>")
    findings = check_anon_key.scan(tmp_path)
    assert findings and "service_role" in findings[0]


def test_forbidden_literal_fails(tmp_path: Path):
    f = tmp_path / "index.html"
    f.write_text("<script>var k=process.env.SUPABASE_SERVICE_ROLE_KEY;</script>")
    findings = check_anon_key.scan(tmp_path)
    assert findings and "SUPABASE_SERVICE_ROLE_KEY" in findings[0]
