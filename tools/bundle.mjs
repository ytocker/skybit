// Bundles all src/*.js modules into a single <script> block inside play.html so
// the game runs from file:// (no http server, no modules). Strips `import`/`export`
// statements and concatenates in dependency order.
//
// Usage: node tools/bundle.mjs

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');

// Dependency order (leaves first).
const ORDER = [
    'config.js',
    'palette.js',
    'gfx.js',
    'sprites.js',
    'storage.js',
    'audio.js',
    'input.js',
    'fx.js',
    'entities.js',
    'world.js',
    'hud.js',
    'scenes.js',
    'main.js',
];

function stripModule(src) {
    // Remove `import ... from '...';` lines (single- or multi-line).
    src = src.replace(/^\s*import[\s\S]*?from\s*['"][^'"]+['"]\s*;?\s*$/gm, '');
    src = src.replace(/^\s*import\s*['"][^'"]+['"]\s*;?\s*$/gm, '');
    // Remove `export ` keyword prefix on declarations (const/let/var/function/class).
    src = src.replace(/^\s*export\s+(default\s+)?(const|let|var|function|class)\b/gm, '$2');
    // Remove any remaining bare `export { ... };` statements.
    src = src.replace(/^\s*export\s*\{[^}]*\}\s*;?\s*$/gm, '');
    return src;
}

const chunks = ORDER.map((name) => {
    const p = path.join(root, 'src', name);
    const raw = fs.readFileSync(p, 'utf8');
    return `// ----- ${name} -----\n` + stripModule(raw);
});

const style = fs.readFileSync(path.join(root, 'style.css'), 'utf8');

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#0e1a2b">
<title>Skybit — Retro Pixel Flyer (single-file build)</title>
<style>
${style}
</style>
</head>
<body>
<div id="stage">
    <canvas id="game" width="180" height="320"></canvas>
</div>
<script>
(function(){
'use strict';
${chunks.join('\n\n')}
})();
</script>
</body>
</html>
`;

const out = path.join(root, 'play.html');
fs.writeFileSync(out, html);
console.log('wrote', out, Math.round(html.length / 1024) + ' KB');
