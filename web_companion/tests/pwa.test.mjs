import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
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
