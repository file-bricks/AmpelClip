import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, statSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dir = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dir, '..')

test('library.js existiert', () => {
  readFileSync(path.join(root, 'library.js'), 'utf8')
})

test('app.js existiert', () => {
  readFileSync(path.join(root, 'app.js'), 'utf8')
})

test('app.css existiert', () => {
  readFileSync(path.join(root, 'app.css'), 'utf8')
})

test('sw.js existiert', () => {
  readFileSync(path.join(root, 'sw.js'), 'utf8')
})

test('manifest.webmanifest existiert', () => {
  readFileSync(path.join(root, 'manifest.webmanifest'), 'utf8')
})

test('manifest.webmanifest ist gültiges JSON', () => {
  const raw = readFileSync(path.join(root, 'manifest.webmanifest'), 'utf8')
  JSON.parse(raw)
})

test('manifest hat Pflichtfelder name, short_name, start_url, icons', () => {
  const m = JSON.parse(readFileSync(path.join(root, 'manifest.webmanifest'), 'utf8'))
  assert.ok(m.name, 'name fehlt')
  assert.ok(m.short_name, 'short_name fehlt')
  assert.ok(m.start_url, 'start_url fehlt')
  assert.ok(Array.isArray(m.icons) && m.icons.length > 0, 'icons fehlt oder leer')
})

test('sw.js enthält fetch-Listener', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  assert.ok(sw.includes('fetch'), 'sw.js muss fetch-Events behandeln')
})

test('sw.js enthält install-Listener', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  assert.ok(sw.includes('install'), 'sw.js muss install-Event behandeln')
})

test('index.html referenziert library.js', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('library.js'))
})

test('index.html referenziert app.js', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('app.js'))
})

test('index.html verlinkt manifest.webmanifest', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('manifest.webmanifest'))
})

test('icons/icon.svg existiert', () => {
  const svg = readFileSync(path.join(root, 'icons', 'icon.svg'), 'utf8')
  assert.ok(svg.includes('<svg'), 'Datei ist kein gültiges SVG')
})

test('app.js importiert anonymizeText aus library.js', () => {
  const js = readFileSync(path.join(root, 'app.js'), 'utf8')
  assert.ok(js.includes('anonymizeText'))
  assert.ok(js.includes('./library.js'))
})

test('saveProfile ist gegen localStorage-Fehler gesichert (Bug #3 Fix — Safari Private Mode)', () => {
  const js = readFileSync(path.join(root, 'app.js'), 'utf8')
  const saveProfileFn = js.slice(js.indexOf('function saveProfile()'))
    .split(/\n(?=function )/)[0]
  assert.ok(saveProfileFn.includes('try'), 'saveProfile muss localStorage.setItem in try/catch wrappen')
  assert.ok(saveProfileFn.includes('catch'), 'saveProfile braucht catch-Block')
})

test('Export-Anchor wird zum DOM hinzugefügt (Bug #2 Fix — Firefox/Safari detached click)', () => {
  const js = readFileSync(path.join(root, 'app.js'), 'utf8')
  assert.ok(js.includes('document.body.appendChild'), 'Anchor muss zum DOM hinzugefügt werden')
  assert.ok(js.includes('document.body.removeChild'), 'Anchor muss nach dem Klick entfernt werden')
})

test('Blob-URL-Revoke verwendet setTimeout (Bug #2 Fix — synchrones Revoke bricht Safari)', () => {
  const js = readFileSync(path.join(root, 'app.js'), 'utf8')
  assert.ok(js.includes('setTimeout') && js.includes('revokeObjectURL'),
    'URL.revokeObjectURL muss per setTimeout verzögert aufgerufen werden')
})

// ── iOS-PWA-Installierbarkeit ──

test('icons/apple-touch-icon-180.png existiert', () => {
  const p = path.join(root, 'icons', 'apple-touch-icon-180.png')
  const s = statSync(p)
  assert.ok(s.size > 0, 'apple-touch-icon-180.png ist leer')
})

test('index.html verlinkt apple-touch-icon als PNG', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('apple-touch-icon-180.png'), 'apple-touch-icon muss auf PNG zeigen, nicht SVG')
})

test('index.html hat viewport-fit=cover', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('viewport-fit=cover'), 'viewport-fit=cover fehlt für iOS Safe-Area-Support')
})

test('index.html hat apple-mobile-web-app-title', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('apple-mobile-web-app-title'), 'apple-mobile-web-app-title meta-Tag fehlt')
})

test('index.html hat apple-mobile-web-app-status-bar-style', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(html.includes('apple-mobile-web-app-status-bar-style'), 'apple-mobile-web-app-status-bar-style meta-Tag fehlt')
})

test('index.html hat KEIN apple-mobile-web-app-capable (deprecated iOS 11.3)', () => {
  const html = readFileSync(path.join(root, 'index.html'), 'utf8')
  assert.ok(!html.includes('apple-mobile-web-app-capable'), 'apple-mobile-web-app-capable darf nicht gesetzt sein (deprecated)')
})

test('sw.js enthält apple-touch-icon-180.png im Cache', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  assert.ok(sw.includes('apple-touch-icon-180.png'), 'apple-touch-icon-180.png muss im Service-Worker-Cache sein')
})

test('sw.js enthält PNG-Manifest-Icons im Cache', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  for (const icon of [
    'Icon-192.png',
    'Icon-512.png',
    'Icon-maskable-192.png',
    'Icon-maskable-512.png'
  ]) {
    assert.ok(sw.includes(icon), `${icon} muss im Service-Worker-Cache sein`)
  }
})

test('sw.js CACHE-Name ist v2 oder höher', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  const match = sw.match(/CACHE\s*=\s*['"]ampelclip-web-v(\d+)['"]/)
  assert.ok(match && parseInt(match[1]) >= 2, 'sw.js CACHE-Name muss nach iOS-Update auf v2+ gebumpt sein')
})

test('app.css enthält safe-area-inset Padding', () => {
  const css = readFileSync(path.join(root, 'app.css'), 'utf8')
  assert.ok(css.includes('safe-area-inset'), 'app.css muss env(safe-area-inset-*) für iOS Notch-Support enthalten')
})

test('app.css hat min-height 44px für .btn (Apple HIG Touch-Target)', () => {
  const css = readFileSync(path.join(root, 'app.css'), 'utf8')
  assert.ok(css.includes('min-height: 44px'), '.btn muss min-height: 44px für Apple HIG-Konformität haben')
})

// BUG-W1: sw.js fetch ohne .catch() → Offline-Fehler bei Cache-Miss
// Fix: .catch(() => new Response('Offline', {status:503})) nach fetch(event.request)
// Red-on-Revert: ohne .catch() fehlt der String-Match
test('BUG-W1 regression: sw.js fetch hat .catch() Offline-Fallback', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  assert.ok(sw.includes('.catch('), 'sw.js fetch muss .catch() für Offline-Fallback haben — BUG-W1')
  assert.ok(sw.includes('503'), 'Offline-Fallback muss HTTP 503 zurückgeben')
})

// BUG-W6: caches.match ohne ignoreSearch:true → Offline bei URL-Parametern (?demo=1)
// Fix: caches.match(event.request, { ignoreSearch: true })
// Red-on-Revert: ohne ignoreSearch fehlt der String-Match
test('BUG-W6 regression: sw.js caches.match nutzt ignoreSearch:true', () => {
  const sw = readFileSync(path.join(root, 'sw.js'), 'utf8')
  assert.ok(
    /caches\.match\([^)]*ignoreSearch\s*:\s*true/.test(sw),
    'sw.js caches.match muss { ignoreSearch: true } nutzen — BUG-W6'
  )
})

// BUG-W5: deferInstall wird nach deferInstall.prompt() genullt statt davor → Doppel-Trigger
// Fix: const prompt = deferInstall; deferInstall = null; BEVOR prompt.prompt()
// Red-on-Revert: wenn fix zurückgedreht, liegt deferInstall = null im Handler NACH .prompt()
test('BUG-W5 regression: deferInstall wird VOR prompt() genullt (Doppel-Trigger-Schutz)', () => {
  const js = readFileSync(path.join(root, 'app.js'), 'utf8')
  // Slice auf den Click-Handler-Body (ab 'click', async () =>')
  const handlerStart = js.indexOf("'click', async () => {")
  assert.ok(handlerStart !== -1, "Click-Handler nicht gefunden")
  const handlerBody = js.slice(handlerStart, handlerStart + 300)
  const nullIdx = handlerBody.indexOf('deferInstall = null')
  const promptIdx = handlerBody.indexOf('.prompt()')
  assert.ok(nullIdx !== -1, 'deferInstall = null im Click-Handler nicht gefunden — BUG-W5')
  assert.ok(promptIdx !== -1, '.prompt() im Click-Handler nicht gefunden')
  assert.ok(nullIdx < promptIdx, 'deferInstall muss im Handler VOR .prompt() genullt werden — BUG-W5')
})
