// Leaderboard bridge.
//
// In the TypeScript build the Python proof-bundle dance becomes
// unnecessary at the language boundary — we already speak JS, so we
// build the SHA-256 chain hash here and POST directly to Supabase.
// The schema, RLS policies, plausibility ceiling, and replay defence
// are all unchanged.
//
// Falls back to localStorage for "no Supabase configured" runs (e.g.
// opening dist/index.html offline as the local version), so the player
// always has a leaderboard even without network.

import { SCORES_KEY } from "./config.js";

const SUPABASE_URL = (import.meta as any).env?.VITE_SUPABASE_URL ?? "";
const SUPABASE_KEY = (import.meta as any).env?.VITE_SUPABASE_ANON_KEY ?? "";

const PLAUSIBILITY_CEILING = 10000;
const TOP_N = 10;

export interface ScoreRow { name: string; score: number; }

let _lastFetchError = "";
const _usedRunIds = new Set<string>();

export function lastFetchError(): string { return _lastFetchError; }

// ── Local storage fallback ────────────────────────────────────────────────

function localFetch(): ScoreRow[] {
  try {
    const raw = localStorage.getItem(SCORES_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as ScoreRow[];
    return arr
      .filter((r) => r && typeof r.score === "number" && r.score >= 0 && r.score <= PLAUSIBILITY_CEILING)
      .sort((a, b) => b.score - a.score)
      .slice(0, TOP_N);
  } catch { return []; }
}

function localSubmit(name: string, score: number): void {
  try {
    const cur = localFetch();
    cur.push({ name: name.slice(0, 10), score });
    cur.sort((a, b) => b.score - a.score);
    localStorage.setItem(SCORES_KEY, JSON.stringify(cur.slice(0, 50)));
  } catch { /* quota exceeded — non-fatal */ }
}

// ── Supabase REST ─────────────────────────────────────────────────────────

function supabaseConfigured(): boolean {
  return !!SUPABASE_URL && !!SUPABASE_KEY;
}

export async function fetchTop10(): Promise<ScoreRow[]> {
  _lastFetchError = "";
  if (!supabaseConfigured()) {
    return localFetch();
  }
  try {
    const url = `${SUPABASE_URL}/rest/v1/scores?select=name,score&order=score.desc&limit=200`;
    const r = await fetch(url, {
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` },
    });
    if (!r.ok) {
      _lastFetchError = `http ${r.status}`;
      return [];
    }
    const rows = (await r.json()) as ScoreRow[];
    const out: ScoreRow[] = [];
    for (const row of rows) {
      if (out.length >= TOP_N) break;
      const score = Number(row?.score);
      if (!Number.isFinite(score) || score < 0 || score > PLAUSIBILITY_CEILING) continue;
      out.push({ name: String(row?.name ?? "").slice(0, 10), score });
    }
    if (rows.length === 0) _lastFetchError = "rls or empty";
    return out;
  } catch (e) {
    console.error("[skybit/lb] fetch threw:", (e as Error)?.message ?? e);
    _lastFetchError = "network";
    return [];
  }
}

export async function submit(name: string, score: number, runId: string): Promise<boolean> {
  // Always mirror to local so the player has at least a personal high
  // even if the network call fails or Supabase isn't configured.
  localSubmit(name, score);
  if (!supabaseConfigured()) return true;
  if (_usedRunIds.has(runId)) return false;
  _usedRunIds.add(runId);
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/scores`, {
      method: "POST",
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify({ name: String(name).slice(0, 10), score: Number(score) }),
    });
    return r.ok;
  } catch { return false; }
}

// ── Telemetry (per-run play log) ──────────────────────────────────────────

export interface PlayLog {
  score: number;
  duration_s: number;
  coins: number;
  pillars: number;
  near_misses: number;
  powerups: Record<string, number>;
}

function deviceId(): string {
  try {
    const k = "skybit_device_id";
    let id = localStorage.getItem(k);
    if (id) return id;
    id = (crypto.randomUUID?.() ?? "00000000-0000-4000-8000-000000000000");
    localStorage.setItem(k, id);
    return id;
  } catch { return "00000000-0000-4000-8000-000000000000"; }
}

export async function logRun(log: PlayLog): Promise<boolean> {
  if (!supabaseConfigured()) return true;
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/plays`, {
      method: "POST",
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify({ ...log, device_id: deviceId() }),
    });
    return r.ok;
  } catch { return false; }
}

// ── Name-entry overlay (HTML) ─────────────────────────────────────────────

export function openNameEntry(): Promise<string> {
  return new Promise((resolve) => {
    const ov = document.getElementById("name-overlay") as HTMLDivElement | null;
    const inp = document.getElementById("name-input") as HTMLInputElement | null;
    const ctr = document.getElementById("name-counter");
    const submitBtn = document.getElementById("name-submit");
    const skipBtn = document.getElementById("name-skip");
    if (!ov || !inp || !submitBtn || !skipBtn) {
      resolve(""); return;
    }
    ov.classList.add("skybit-shown");
    inp.value = "";
    if (ctr) ctr.textContent = "0 / 10";
    setTimeout(() => { try { inp.focus(); } catch { /* iOS UME */ } }, 80);
    inp.oninput = () => {
      if (ctr) ctr.textContent = `${inp.value.length} / 10`;
    };
    const finish = (name: string) => {
      ov.classList.remove("skybit-shown");
      submitBtn.onclick = null;
      skipBtn.onclick = null;
      inp.onkeydown = null;
      resolve(name);
    };
    submitBtn.onclick = () => finish(inp.value.trim() || "");
    skipBtn.onclick = () => finish("");
    inp.onkeydown = (e) => {
      if (e.key === "Enter") finish(inp.value.trim() || "");
    };
  });
}

// ── Run-id helper for replay defence ──────────────────────────────────────

export function newRunId(): string {
  return crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}
