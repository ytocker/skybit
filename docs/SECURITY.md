# Skybit Security

This document describes the threat model, the defenses currently in
place, and the operational runbooks (key rotation, schema migration,
incident response).

> Skybit is a casual single-player Pygame game with an optional Supabase
> leaderboard. The threat model is calibrated for that scope —
> "discourage casual cheaters and lock down the obvious web-app
> vulnerabilities," not "withstand a determined APT."

## Architecture (security-relevant slice)

```
┌──────────────────────┐      HMAC-signed envelope      ┌──────────────────┐
│  Browser (pygbag)    │ ─── POST /rest/v1/rpc/         │  Supabase        │
│  ├─ game/security/   │      submit_score (RLS)        │  ├─ submit_score │
│  ├─ inject_theme JS  │ ─── POST /rest/v1/rpc/         │  │  RPC          │
│  │  (anon key only)  │      log_play (RLS)            │  ├─ log_play RPC │
│  └─ localStorage:    │ ─── POST /rest/v1/             │  ├─ scores       │
│     device_id, …     │      security_events           │  ├─ plays        │
│                      │                                 │  ├─ submissions_ │
│                      │                                 │  │  audit        │
│                      │                                 │  └─ security_    │
│                      │                                 │     events       │
└──────────────────────┘                                 └──────────────────┘
```

Native (desktop) builds skip the Supabase path entirely; their threat
surface is limited to the local `skybit_scores.json` (HMAC-protected).

## Threat model

| Threat                                      | Mitigation |
|---------------------------------------------|------------|
| Edit a single score in DevTools / curl      | `submit_score` RPC validates score range, name length, duration, plausibility ceiling, rate-limit. Direct `INSERT` on `public.scores` is REVOKED for `anon`. |
| Fly straight forever, max-score             | Server-side trajectory check: y-stddev × 100 must be ≥ 800 (~8 px). RunRecorder samples bird-y at ~10 Hz; collision-disable hacks produce ~0 std-dev → rejected. |
| Replay events without dying                 | `submit_score` requires `chain_last == 'death'`. Death event is sealed inside `World._die()` only. |
| Forge events / truncate the chain           | Each event is HMAC-chained with the previous link. `chain_count` must be ≥ pillars + 1 → truncation rejected. |
| Spam submissions                            | Server-side: 30-second per-device cooldown via `submissions_audit`. Client-side: matching cooldown + UI feedback. |
| AFK / bot endless run                       | `duration_too_long` cap at 1800 seconds. |
| XSS / unicode bidi spoof in player name     | `sanitize_name` (NFKC, strip control + zero-width + bidi, blocklist, length clamp). Applied client-side AND in the SQL `scores_name_len` check. |
| Tampered local scoreboard                   | `skybit_scores.json` wrapped in HMAC envelope; any byte-flip wipes the file on load. |
| Supabase service-role key leak in build     | `tools/check_anon_key.py` decodes every JWT-shaped string in `build/web/` and fails the build if any has `role != 'anon'`. Runs in pre-commit + GitHub Actions. |
| Click-jacking / iframe embedding            | `X-Frame-Options: DENY`, CSP `frame-ancestors 'none'`. |
| MITM / downgrade                            | `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`. |
| Browser fingerprinting attacks              | `Permissions-Policy` disables camera, mic, geolocation, USB, serial, BT, payment, MIDI, motion sensors. |
| Information disclosure on crash             | `main.py` redacts traceback to a generic message unless `SKYBIT_DEV=1`. Full trace still goes to `stderr`. |
| Untrusted dependency CVEs                   | `pip-audit` runs in the security workflow on every PR. |
| Secret committed to git history             | `gitleaks` runs on every push (full history). |

## Caveats (honest)

* The HMAC secret ships **inside the WASM bundle** — a determined
  attacker can extract it. The HMAC isn't perfect secrecy; it's a
  speed bump that converts "edit one number" into "reverse-engineer
  the WASM and replay events." Real authority is the server-side
  plausibility ceiling.
* A user can clear `localStorage` between submissions to defeat the
  client-side rate limit, but the server has its own audit table on
  `device_id` *plus* a fresh device generates a new UUID — so a
  single attacker cycling devices still hits IP-shaped rate limits
  if you add Supabase's edge rate limiting later.
* The trajectory variance check (y-stddev) is statistical: a
  sufficiently sophisticated attacker can synthesize a realistic
  flight path. Combined with the chain-of-events HMAC and the
  duration/pillar/score plausibility checks, this remains very
  expensive to fake convincingly.

## Operational runbooks

### Rotating the HMAC secret

1. Generate a new key: `openssl rand -hex 24`.
2. In Netlify → Site settings → Environment variables, set
   `SKYBIT_HMAC_KEY` to the new value.
3. Trigger a redeploy. `inject_theme.py` substitutes the placeholder
   into `inject_theme.py`'s JS bridge AND writes
   `game/security/_build_secret.py` so the Python side picks it up.
4. The previous key is no longer accepted; older client tabs will
   still submit, but server-side validation limits the damage.

### Applying the schema migration

The `supabase/schema.sql` file is hand-applied (no migration tool):

1. Open Supabase dashboard → SQL editor.
2. Paste the entire file. The Security hardening block is idempotent
   — re-running it is safe (uses `if not exists`, `or replace`,
   `drop policy if exists`).
3. After applying, verify:
   ```sql
   select polname from pg_policies where tablename = 'scores';
   -- Should NOT contain 'anon insert scores'.
   select pronargs from pg_proc where proname = 'submit_score';
   -- Should return 11 (the new arg list).
   ```

### Manual probes after deploy

```sh
# Verify CSP and the rest of the headers landed.
curl -sI https://skybit.netlify.app/ \
  | grep -Ei 'content-security|x-frame|referrer|permissions|strict-transport'

# Direct-insert path is now closed:
curl -s -X POST "$SB/rest/v1/scores" \
  -H "apikey: $ANON" -H "Authorization: Bearer $ANON" \
  -H "Content-Type: application/json" \
  -d '{"name":"x","score":99999}'
# → expect "permission denied" or 401.

# RPC path with bogus args is closed:
curl -s -X POST "$SB/rest/v1/rpc/submit_score" \
  -H "apikey: $ANON" -H "Authorization: Bearer $ANON" \
  -H "Content-Type: application/json" \
  -d '{"p_name":"x","p_score":99999,"p_device":"00000000-0000-4000-8000-000000000000","p_duration":3,"p_run_sig":"","p_pillars":0,"p_y_stddev_centi":0,"p_y_range_centi":0,"p_chain_last":"","p_chain_count":0,"p_client_sig":"shortsig"}'
# → expect "client_sig_missing" or "straight_run_detected".
```

### Monitored anomalies

The `security_events` table receives client-reported anomalies tagged
with the device UUID and a JSON detail blob. Useful queries:

```sql
-- Top anomaly kinds in the last 24h.
select name, count(*) from public.security_events
  where ts > now() - interval '24 hours'
  group by 1 order by 2 desc;

-- Devices with elevated anomaly rate (potential cheating attempts).
select device_id, count(*) from public.security_events
  where ts > now() - interval '7 days'
  group by 1 having count(*) > 50 order by 2 desc;
```

## Privacy posture

* Player name + integer score + anonymous device UUID + per-run stats.
  No IP, no user-agent, no precise location, no third-party trackers.
* `clear_all_local_data()` exposed via `game.security.privacy` lets a
  player erase every Skybit-owned local artefact (right to erasure).
* Telemetry opt-out: `set_telemetry(False)` short-circuits
  `play_log.log_run`. Default is on; we recommend the menu surface
  this on first launch alongside `mark_gdpr_notice_shown()`.
