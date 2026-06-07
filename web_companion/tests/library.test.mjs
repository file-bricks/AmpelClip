import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  anonymizeText,
  normalizeProfile,
  createDefaultProfile,
  collectLiteralSpans,
  substituteOutsideSpans,
  BUILTIN_PATTERNS,
} from '../library.js'

// ── Grundfunktionen ───────────────────────────────────────────────────────────

test('anonymizeText gibt leeren String für leere Eingabe zurück', () => {
  const profile = createDefaultProfile()
  assert.equal(anonymizeText('', profile), '')
  assert.equal(anonymizeText(null, profile), '')
  assert.equal(anonymizeText(undefined, profile), '')
})

test('BUILTIN_PATTERNS enthält alle 6 erwarteten Schlüssel', () => {
  const expected = ['iban', 'email', 'phone_de', 'creditcard', 'postcode_de', 'date_de']
  for (const k of expected) {
    assert.ok(k in BUILTIN_PATTERNS, `Fehlender Schlüssel: ${k}`)
  }
})

// ── Whitelist-Schutz (Kernfall, vom Advisor gefordert) ────────────────────────

test('freigegebene E-Mail überlebt Builtin-Email-Pattern', () => {
  const profile = createDefaultProfile()
  profile.builtin_patterns.email = true
  profile.lists.whitelist = ['admin@example.com']
  const text = 'Schreib an admin@example.com und auch an user@example.com'
  const result = anonymizeText(text, profile)
  assert.ok(result.includes('admin@example.com'), 'Whitelisted E-Mail muss erhalten bleiben')
  assert.ok(result.includes('[EMAIL]'), 'Nicht-whitelisted E-Mail muss ersetzt werden')
  assert.ok(!result.includes('user@example.com'), 'user@example.com muss weg sein')
})

test('nicht-freigegebene E-Mail wird durch [EMAIL] ersetzt', () => {
  const profile = createDefaultProfile()
  profile.builtin_patterns.email = true
  const result = anonymizeText('Kontakt: kontakt@test.de', profile)
  assert.ok(!result.includes('kontakt@test.de'))
  assert.ok(result.includes('[EMAIL]'))
})

// ── Sensible Eigenbegriffe ────────────────────────────────────────────────────

test('benutzerdefinierter sensibler Begriff wird durch [ANONYM] ersetzt', () => {
  const profile = createDefaultProfile()
  profile.lists.sensibel = ['Geheimnis']
  const result = anonymizeText('Das ist ein Geheimnis und bleibt so.', profile)
  assert.ok(!result.includes('Geheimnis'))
  assert.ok(result.includes('[ANONYM]'))
})

// ── whole_words ───────────────────────────────────────────────────────────────

test('wholeWords=true trifft keinen Teilstring', () => {
  const profile = createDefaultProfile()
  profile.settings.whole_words = true
  profile.lists.sensibel = ['test']
  const result = anonymizeText('testing the testcase aber test ist sensibel', profile)
  assert.ok(result.includes('testing'), 'testing darf nicht ersetzt werden')
  assert.ok(result.includes('testcase'), 'testcase darf nicht ersetzt werden')
  assert.ok(!result.includes(' test ') || result.includes('[ANONYM]'),
    'isoliertes "test" muss ersetzt werden')
})

test('wholeWords=true erkennt deutsches Wort mit Umlaut (Müller)', () => {
  const profile = createDefaultProfile()
  profile.settings.whole_words = true
  profile.lists.sensibel = ['Müller']
  const result = anonymizeText('Herr Müller ist hier.', profile)
  assert.ok(!result.includes('Müller'))
  assert.ok(result.includes('[ANONYM]'))
})

test('wholeWords=true ersetzt Umlautwort nicht als Teil eines Kompositums', () => {
  const profile = createDefaultProfile()
  profile.settings.whole_words = true
  profile.lists.sensibel = ['Müller']
  const result = anonymizeText('MüllerGmbH bleibt, Herr Müller geht.', profile)
  assert.ok(result.includes('MüllerGmbH'), 'MüllerGmbH darf nicht ersetzt werden')
})

// ── Groß-/Kleinschreibung ─────────────────────────────────────────────────────

test('case_sensitive=false (Standard) erkennt gemischte Schreibweise', () => {
  const profile = createDefaultProfile()
  profile.settings.case_sensitive = false
  profile.lists.sensibel = ['Geheim']
  const result = anonymizeText('geheim und GEHEIM', profile)
  assert.ok(!result.includes('geheim'))
  assert.ok(!result.includes('GEHEIM'))
})

// ── Deaktivierte Patterns ─────────────────────────────────────────────────────

test('deaktiviertes Builtin-Email-Pattern lässt E-Mail stehen', () => {
  const profile = createDefaultProfile()
  profile.builtin_patterns.email = false
  const result = anonymizeText('Schreib an info@test.de', profile)
  assert.ok(result.includes('info@test.de'))
})

// ── normalizeProfile ──────────────────────────────────────────────────────────

test('normalizeProfile wirft Fehler bei falschem schema_version', () => {
  assert.throws(() => normalizeProfile({ schema_version: 'wrong-v99' }), /Nicht unterstütztes/)
})

test('normalizeProfile wirft Fehler bei null', () => {
  assert.throws(() => normalizeProfile(null), /JSON-Objekt/)
})

test('normalizeProfile akzeptiert gültiges Profil', () => {
  const raw = {
    schema_version: 'ampelclip-profile-v1',
    settings: { ampel_status: 'gruen', case_sensitive: true, whole_words: true },
    lists: { sensibel: ['Max', 'Max'], whitelist: ['Max Mustermann'] },
    builtin_patterns: { iban: true, email: false },
  }
  const p = normalizeProfile(raw)
  assert.equal(p.settings.case_sensitive, true)
  assert.equal(p.settings.whole_words, true)
  assert.equal(p.builtin_patterns.iban, true)
  assert.equal(p.builtin_patterns.email, false)
  assert.deepEqual(p.lists.sensibel, ['Max'])
  assert.deepEqual(p.lists.whitelist, ['Max Mustermann'])
})

// ── collectLiteralSpans ───────────────────────────────────────────────────────

test('collectLiteralSpans liefert leeres Array für leere Begriffsliste', () => {
  const result = collectLiteralSpans('foo bar baz', [], { caseSensitive: true, wholeWords: false })
  assert.deepEqual(result, [])
})

test('collectLiteralSpans verschmilzt überlappende Spans', () => {
  const spans = collectLiteralSpans('foo bar', ['foo b', 'foo ba'], {
    caseSensitive: true,
    wholeWords: false,
  })
  assert.equal(spans.length, 1)
  assert.equal(spans[0][0], 0)
  assert.ok(spans[0][1] >= 6)
})

// ── substituteOutsideSpans ────────────────────────────────────────────────────

test('substituteOutsideSpans ohne geschützte Spans ersetzt alle Treffer', () => {
  const re = /test/g
  const result = substituteOutsideSpans('test und test', re, 'X', [])
  assert.equal(result, 'X und X')
})

test('substituteOutsideSpans lässt geschützten Bereich intakt', () => {
  const text = 'AAA BBB AAA'
  const re = /AAA/g
  const spans = [[4, 7]]
  const result = substituteOutsideSpans(text, re, 'X', spans)
  assert.equal(result, 'X BBB X')
})

// ── Regression: Stale-Span PII-Leak ──────────────────────────────────────────

test('Stale-Span-Regression: Sensibel-Ersatz verschiebt keine Whitelist-Grenzen (PII-Leak-Check)', () => {
  const p = createDefaultProfile()
  p.builtin_patterns.email = true
  p.lists.sensibel = ['AA']
  p.lists.whitelist = ['ZZZZ']
  const result = anonymizeText('AA bad@x.io ZZZZ', p)
  assert.ok(result.includes('[ANONYM]'), `AA muss ersetzt werden, got: ${result}`)
  assert.ok(result.includes('[EMAIL]'), `E-Mail muss ersetzt werden, got: ${result}`)
  assert.ok(result.includes('ZZZZ'), `ZZZZ (Whitelist) muss erhalten bleiben, got: ${result}`)
  assert.ok(!result.includes('bad@x.io'), `E-Mail darf nicht im Klartext bleiben, got: ${result}`)
})
