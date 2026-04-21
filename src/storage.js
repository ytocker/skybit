import { HIGHSCORE_KEY, SETTINGS_KEY } from './config.js';

export function loadHighScore() {
    try {
        const v = parseInt(localStorage.getItem(HIGHSCORE_KEY) || '0', 10);
        return Number.isFinite(v) ? v : 0;
    } catch { return 0; }
}

export function saveHighScore(v) {
    try { localStorage.setItem(HIGHSCORE_KEY, String(v | 0)); } catch {}
}

export function loadSettings() {
    try {
        const raw = localStorage.getItem(SETTINGS_KEY);
        if (!raw) return { crt: true, muted: false };
        return Object.assign({ crt: true, muted: false }, JSON.parse(raw));
    } catch { return { crt: true, muted: false }; }
}

export function saveSettings(s) {
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch {}
}
