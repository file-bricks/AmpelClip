// library.js — AmpelClip anonymization engine (ESM)
// Ports the Python logic from Ampel6.py: span-based whitelist protection,
// builtin regex patterns, case-insensitive/whole-word matching.

export const BUILTIN_PATTERNS = {
  iban: {
    name: 'IBAN (Kontonummer)',
    regex: String.raw`\b[A-Z]{2}\d{2}[\s]?(?:\d{4}[\s]?){4,7}\d{0,2}\b`,
    token: '[IBAN]',
    defaultEnabled: true,
  },
  email: {
    name: 'E-Mail Adressen',
    regex: String.raw`\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b`,
    token: '[EMAIL]',
    defaultEnabled: true,
  },
  phone_de: {
    name: 'Telefonnummern (DE)',
    regex: String.raw`(?<![\p{L}\p{N}])(?:\+49|0049|0)[\s.\-]?(?:\d{2,4})[\s.\-]?(?:\d{3,})[\s.\-]?(?:\d{2,})\b`,
    token: '[TELEFON]',
    defaultEnabled: false,
  },
  creditcard: {
    name: 'Kreditkarten',
    regex: String.raw`\b(?:\d{4}[\s\-]?){3}\d{4}\b`,
    token: '[KREDITKARTE]',
    defaultEnabled: false,
  },
  postcode_de: {
    name: 'Postleitzahlen (DE)',
    regex: String.raw`\b\d{5}\b`,
    token: '[PLZ]',
    defaultEnabled: false,
  },
  date_de: {
    name: 'Datumsangaben',
    regex: String.raw`\b\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}\b`,
    token: '[DATUM]',
    defaultEnabled: false,
  },
}

const SCHEMA_VERSION = 'ampelclip-profile-v1'

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// Port of Python _collect_literal_spans.
// Returns sorted, merged list of [start, end] positions for whitelist terms in text.
// Uses Unicode-aware word boundaries for whole_words (JS \b is ASCII-only).
export function collectLiteralSpans(text, terms, { caseSensitive, wholeWords }) {
  const flags = caseSensitive ? 'gu' : 'giu'
  const spans = []

  for (const term of terms) {
    if (!term) continue
    const escaped = escapeRegex(term)
    const pattern = wholeWords
      ? `(?<![\\p{L}\\p{N}])${escaped}(?![\\p{L}\\p{N}])`
      : escaped
    const re = new RegExp(pattern, flags)
    let match
    while ((match = re.exec(text)) !== null) {
      spans.push([match.index, match.index + match[0].length])
    }
  }

  if (spans.length === 0) return []

  spans.sort((a, b) => a[0] - b[0])

  const merged = [spans[0].slice()]
  for (let i = 1; i < spans.length; i++) {
    const [start, end] = spans[i]
    const last = merged[merged.length - 1]
    if (start <= last[1]) {
      last[1] = Math.max(last[1], end)
    } else {
      merged.push([start, end])
    }
  }

  return merged
}

// Port of Python _substitute_outside_spans.
// Applies regex replacement only in text segments NOT covered by protectedSpans.
export function substituteOutsideSpans(text, regex, replacement, protectedSpans) {
  protectedSpans = filterSpansForRegex(text, regex, protectedSpans)
  if (protectedSpans.length === 0) {
    return text.replace(regex, replacement)
  }

  const chunks = []
  let cursor = 0

  for (const [start, end] of protectedSpans) {
    if (cursor < start) {
      chunks.push(text.slice(cursor, start).replace(regex, replacement))
    }
    chunks.push(text.slice(start, end))
    cursor = end
  }

  if (cursor < text.length) {
    chunks.push(text.slice(cursor).replace(regex, replacement))
  }

  return chunks.join('')
}

function filterSpansForRegex(text, regex, protectedSpans) {
  if (protectedSpans.length === 0) return []

  const flags = regex.flags.includes('g') ? regex.flags : `${regex.flags}g`
  const scanRe = new RegExp(regex.source, flags)
  const regexSpans = []
  let match
  while ((match = scanRe.exec(text)) !== null) {
    const start = match.index
    const end = start + match[0].length
    if (start !== end) regexSpans.push([start, end])
    if (match[0].length === 0) scanRe.lastIndex += 1
  }

  if (regexSpans.length === 0) return protectedSpans

  return protectedSpans.filter(([start, end]) => !regexSpans.some(([matchStart, matchEnd]) =>
    matchStart <= start &&
    end <= matchEnd &&
    (matchStart < start || end < matchEnd)
  ))
}

// Main anonymization function.
// Recomputes whitelist spans per pattern on the current text. This keeps offsets
// correct after replacements and prevents whitelist substrings from splitting a
// larger sensitive regex match such as an IBAN.
export function anonymizeText(text, profile) {
  if (!text) return ''

  const { settings = {}, lists = {}, builtin_patterns = {} } = profile
  const caseSensitive = Boolean(settings.case_sensitive)
  const wholeWords = Boolean(settings.whole_words)
  const sensitiveTerms = (lists.sensibel || []).filter(t => typeof t === 'string' && t.length > 0)
  const whitelistTerms = (lists.whitelist || []).filter(t => typeof t === 'string' && t.length > 0)

  const flags = caseSensitive ? 'gu' : 'giu'

  // Build all pattern/token pairs upfront.
  const patterns = []
  for (const term of sensitiveTerms) {
    const escaped = escapeRegex(term)
    const pat = wholeWords
      ? `(?<![\\p{L}\\p{N}])${escaped}(?![\\p{L}\\p{N}])`
      : escaped
    patterns.push({ re: new RegExp(pat, flags), token: '[ANONYM]' })
  }
  for (const [key, info] of Object.entries(BUILTIN_PATTERNS)) {
    if (Boolean(builtin_patterns[key] ?? false)) {
      patterns.push({ re: new RegExp(info.regex, flags), token: info.token })
    }
  }

  if (patterns.length === 0) return text

  let result = text
  for (const { re, token } of patterns) {
    const spans = collectLiteralSpans(result, whitelistTerms, { caseSensitive, wholeWords })
    result = substituteOutsideSpans(result, re, token, spans)
  }
  return result
}

function cleanUniqueStrings(arr) {
  if (!Array.isArray(arr)) return []
  const seen = new Set()
  const result = []
  for (const item of arr) {
    const s = String(item).trim()
    if (s && !seen.has(s)) {
      seen.add(s)
      result.push(s)
    }
  }
  return result
}

function normalizedAmpelStatus(value) {
  return ['rot', 'gelb', 'gruen'].includes(value) ? value : 'rot'
}

// Validates and normalizes a raw profile JSON object.
// Throws if schema_version is missing or wrong.
export function normalizeProfile(raw) {
  if (!raw || typeof raw !== 'object') {
    throw new Error('Profil muss ein JSON-Objekt sein.')
  }
  if (raw.schema_version !== SCHEMA_VERSION) {
    throw new Error(`Nicht unterstütztes Profilformat: ${JSON.stringify(raw.schema_version)}`)
  }

  const settings = (raw.settings && typeof raw.settings === 'object') ? raw.settings : {}
  const lists = (raw.lists && typeof raw.lists === 'object') ? raw.lists : {}
  const builtins = (raw.builtin_patterns && typeof raw.builtin_patterns === 'object') ? raw.builtin_patterns : {}

  return {
    schema_version: SCHEMA_VERSION,
    app: (raw.app && typeof raw.app === 'object') ? raw.app : {},
    settings: {
      ampel_status: normalizedAmpelStatus(settings.ampel_status),
      case_sensitive: Boolean(settings.case_sensitive),
      whole_words: Boolean(settings.whole_words),
    },
    builtin_patterns: Object.fromEntries(
      Object.keys(BUILTIN_PATTERNS).map(k => [k, Boolean(builtins[k] ?? false)])
    ),
    lists: {
      sensibel: cleanUniqueStrings(lists.sensibel),
      whitelist: cleanUniqueStrings(lists.whitelist),
    },
  }
}

// Returns a fresh default profile with iban+email enabled.
export function createDefaultProfile() {
  return {
    schema_version: SCHEMA_VERSION,
    app: { name: 'AmpelClip Web', version: '1.0.0' },
    settings: {
      ampel_status: 'rot',
      case_sensitive: false,
      whole_words: false,
    },
    builtin_patterns: Object.fromEntries(
      Object.keys(BUILTIN_PATTERNS).map(k => [k, BUILTIN_PATTERNS[k].defaultEnabled])
    ),
    lists: { sensibel: [], whitelist: [] },
  }
}
