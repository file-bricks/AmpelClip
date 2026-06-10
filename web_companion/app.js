import { anonymizeText, normalizeProfile, createDefaultProfile, BUILTIN_PATTERNS } from './library.js'

const STORAGE_KEY = 'ampelclip-web-profile-v1'

// ── State ────────────────────────────────────────────────────────────────────

let profile = loadProfile()
let deferInstall = null

// ── DOM Refs ─────────────────────────────────────────────────────────────────

const elStatus       = document.getElementById('status')
const elInstallBtn   = document.getElementById('btn-install')
const elImportBtn    = document.getElementById('btn-import')
const elFileInput    = document.getElementById('file-input')
const elExportBtn    = document.getElementById('btn-export')
const elResetBtn     = document.getElementById('btn-reset')
const elAmpelDot     = document.getElementById('ampel-dot')
const elAmpelLabel   = document.getElementById('ampel-label')
const elCaseSens     = document.getElementById('chk-case')
const elWholeWords   = document.getElementById('chk-words')
const elBuiltinList  = document.getElementById('builtin-list')
const elSensibelInput = document.getElementById('sensibel-input')
const elSensibelAdd  = document.getElementById('sensibel-add')
const elSensibelItems = document.getElementById('sensibel-items')
const elWhiteInput   = document.getElementById('white-input')
const elWhiteAdd     = document.getElementById('white-add')
const elWhiteItems   = document.getElementById('white-items')
const elOriginal     = document.getElementById('text-original')
const elResult       = document.getElementById('text-result')
const elAnonymize    = document.getElementById('btn-anonymize')
const elCopyResult   = document.getElementById('btn-copy')

// ── PWA Install ───────────────────────────────────────────────────────────────

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault()
  deferInstall = e
  elInstallBtn.classList.add('visible')
})

elInstallBtn.addEventListener('click', async () => {
  if (!deferInstall) return
  deferInstall.prompt()
  const { outcome } = await deferInstall.userChoice
  if (outcome === 'accepted') elInstallBtn.classList.remove('visible')
  deferInstall = null
})

// ── Service Worker ────────────────────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js').catch(() => {})
}

// ── Profile Load/Save ─────────────────────────────────────────────────────────

function loadProfile() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return createDefaultProfile()
    return normalizeProfile(JSON.parse(raw))
  } catch {
    return createDefaultProfile()
  }
}

function saveProfile() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
  } catch {
    setStatus('Einstellungen konnten nicht gespeichert werden (Privater Modus?).', true)
  }
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderAmpel() {
  const s = profile.settings.ampel_status
  elAmpelDot.className = `ampel-dot ampel-dot--${s}`
  const labels = { rot: 'ROT — inaktiv', gelb: 'GELB — Vorschau', gruen: 'GRÜN — aktiv' }
  elAmpelLabel.textContent = labels[s] ?? s
}

function renderSettings() {
  elCaseSens.checked   = profile.settings.case_sensitive
  elWholeWords.checked = profile.settings.whole_words
}

function renderBuiltins() {
  elBuiltinList.innerHTML = ''
  for (const [key, info] of Object.entries(BUILTIN_PATTERNS)) {
    const enabled = Boolean(profile.builtin_patterns[key])
    const id = `chk-builtin-${key}`
    const li = document.createElement('li')
    li.style.listStyle = 'none'
    li.innerHTML = `
      <label class="check-row" title="${info.token}">
        <input type="checkbox" id="${id}" ${enabled ? 'checked' : ''}>
        <span>${info.name}</span>
        <code style="margin-left:auto;font-size:.75rem;color:var(--muted)">${info.token}</code>
      </label>`
    li.querySelector('input').addEventListener('change', e => {
      profile.builtin_patterns[key] = e.target.checked
      saveProfile()
    })
    elBuiltinList.appendChild(li)
  }
}

function renderList(items, container, onDelete) {
  container.innerHTML = ''
  for (const item of items) {
    const li = document.createElement('li')
    li.className = 'list-item'
    const span = document.createElement('span')
    span.textContent = item
    span.style.wordBreak = 'break-all'
    const del = document.createElement('button')
    del.className = 'list-item__del'
    del.title = 'Entfernen'
    del.textContent = '×'
    del.addEventListener('click', () => onDelete(item))
    li.appendChild(span)
    li.appendChild(del)
    container.appendChild(li)
  }
}

function renderSensibelList() {
  renderList(profile.lists.sensibel, elSensibelItems, item => {
    profile.lists.sensibel = profile.lists.sensibel.filter(t => t !== item)
    saveProfile()
    renderSensibelList()
  })
}

function renderWhiteList() {
  renderList(profile.lists.whitelist, elWhiteItems, item => {
    profile.lists.whitelist = profile.lists.whitelist.filter(t => t !== item)
    saveProfile()
    renderWhiteList()
  })
}

function renderAll() {
  renderAmpel()
  renderSettings()
  renderBuiltins()
  renderSensibelList()
  renderWhiteList()
}

// ── Event Handlers ────────────────────────────────────────────────────────────

elCaseSens.addEventListener('change', () => {
  profile.settings.case_sensitive = elCaseSens.checked
  saveProfile()
})

elWholeWords.addEventListener('change', () => {
  profile.settings.whole_words = elWholeWords.checked
  saveProfile()
})

function addToList(input, listKey, renderFn) {
  const val = input.value.trim()
  if (!val) return
  if (!profile.lists[listKey].includes(val)) {
    profile.lists[listKey].push(val)
    saveProfile()
    renderFn()
  }
  input.value = ''
  input.focus()
}

elSensibelAdd.addEventListener('click', () => addToList(elSensibelInput, 'sensibel', renderSensibelList))
elSensibelInput.addEventListener('keydown', e => { if (e.key === 'Enter') addToList(elSensibelInput, 'sensibel', renderSensibelList) })

elWhiteAdd.addEventListener('click', () => addToList(elWhiteInput, 'whitelist', renderWhiteList))
elWhiteInput.addEventListener('keydown', e => { if (e.key === 'Enter') addToList(elWhiteInput, 'whitelist', renderWhiteList) })

// ── Profil Import ─────────────────────────────────────────────────────────────

elImportBtn.addEventListener('click', () => elFileInput.click())

elFileInput.addEventListener('change', async () => {
  const file = elFileInput.files?.[0]
  if (!file) return
  try {
    const text = await file.text()
    profile = normalizeProfile(JSON.parse(text))
    saveProfile()
    renderAll()
    setStatus(`Profil „${file.name}" geladen.`)
  } catch (err) {
    setStatus(`Fehler: ${err.message}`, true)
  }
  elFileInput.value = ''
})

// ── Profil Export ─────────────────────────────────────────────────────────────

elExportBtn.addEventListener('click', () => {
  const payload = { ...profile, app: { name: 'AmpelClip Web', version: '1.0.0', exported_at: new Date().toISOString() } }
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'ampelclip-profile.json'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
  setStatus('Profil exportiert.')
})

// ── Reset ─────────────────────────────────────────────────────────────────────

elResetBtn.addEventListener('click', () => {
  profile = createDefaultProfile()
  saveProfile()
  renderAll()
  setStatus('Profil zurückgesetzt.')
})

// ── Anonymisierung ────────────────────────────────────────────────────────────

elAnonymize.addEventListener('click', () => {
  const input = elOriginal.value
  if (!input.trim()) { setStatus('Kein Text eingegeben.', true); return }
  elResult.value = anonymizeText(input, profile)
  setStatus('Text anonymisiert.')
})

elCopyResult.addEventListener('click', async () => {
  const text = elResult.value
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    setStatus('In Zwischenablage kopiert.')
  } catch {
    elResult.select()
    setStatus('Bitte manuell kopieren (Strg+C).', true)
  }
})

// ── Status ────────────────────────────────────────────────────────────────────

function setStatus(msg, isError = false) {
  elStatus.textContent = msg
  elStatus.className = `status-bar${isError ? ' status-bar--error' : ''}`
}

// ── Init ──────────────────────────────────────────────────────────────────────

renderAll()
setStatus('Bereit. Kein Text oder Profil geladen.')
