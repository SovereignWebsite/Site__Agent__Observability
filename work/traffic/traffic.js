// SovereignWebsite traffic counts: draft 3, not live. Dinis, 23 Nov 2026 (record 2026-11-23__observability-pilot):
// no third-party location lookup; the country is estimated by the drain from the browser's time zone and language.
// observability.b@SovereignWebsite.dinis, 20 Nov 2026. Adapted from SGit-AI's PHP site (assets/telemetry.js).
// Per page, from the site's own hosts only: one encrypted note {v, site, path, ts, tz, lang, type, tab} to a write-only
// append lane. tz is the browser's IANA time zone and lang its first language tag, both clipped; no request goes anywhere
// but the vault service. The drain maps tz to a country (zone.tab) and publishes countries only, never tz or lang.
// Kept on the device: in session storage for the tab, the tab id, the pages sent and a counter; in local storage, only
// the team flag 'sw.traffic.who' when someone sets it on the admin page. No cookies. Never blocks; fails silently.
// Config: /traffic.json {enabled, endpoint, vault_id, lanes[], recipient (sgit public bundle, encrypt PEM), hosts[]}.
// The site's CSP must allow connect-src only 'self', and the SG/Send host (review 003, finding 4).
(async function () {
  const S = 'sw.traffic.'
  const get = k => { try { return sessionStorage.getItem(S + k) } catch (e) { return null } }
  const put = (k, v) => { try { sessionStorage.setItem(S + k, String(v)) } catch (e) {} }
  try {
    if (!window.crypto || !crypto.subtle || !window.fetch) return
    if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true) return
    const host = location.hostname
    if (location.protocol !== 'https:' || /^(localhost|127\.|0\.0\.0\.0$|\[?::1\]?$)|\.local$/.test(host)) return
    const cfg = await (await fetch('/traffic.json', { cache: 'no-store' })).json()
    if (!cfg || cfg.enabled === false || !cfg.recipient || !cfg.recipient.encrypt || !Array.isArray(cfg.lanes) || !cfg.lanes.length) return
    if (!Array.isArray(cfg.hosts) || !cfg.hosts.includes(host)) return

    let tab = get('tab')
    if (!tab) { tab = Array.from(crypto.getRandomValues(new Uint8Array(4)), b => b.toString(16).padStart(2, '0')).join(''); put('tab', tab) }

    const path = location.pathname.slice(0, 200)
    let seen = []; try { seen = JSON.parse(get('seen') || '[]') } catch (e) {}
    if (seen.includes(path)) return                                   // one note per page per tab

    const sent = parseInt(get('n') || '0', 10) || 0
    if (sent >= 40) return                                            // per-tab cap: no person reads 40 pages in a tab

    const type = visitorType()
    const ev = { v: 1, site: host, path, ts: new Date().toISOString().slice(0, 16) + 'Z',
                 tz: zone(), lang: language(), type, tab }
    const payload = await envelope(cfg.recipient.encrypt, JSON.stringify(ev))

    const start = (parseInt(tab, 16) || 0) % cfg.lanes.length
    for (let i = 0; i < cfg.lanes.length; i++) {
      const r = await fetch(`${cfg.endpoint}/api/vault/append/write/${encodeURIComponent(cfg.vault_id)}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, keepalive: true, credentials: 'omit', referrerPolicy: 'no-referrer',
        body: JSON.stringify({ append_token: cfg.lanes[(start + i) % cfg.lanes.length], payload }) })
      if (r.ok) { seen.push(path); put('seen', JSON.stringify(seen.slice(-50))); put('n', sent + 1); return }
      if (r.status !== 507 && r.status !== 404 && r.status < 500) return   // only a full, unknown or failing lane is worth another
    }
  } catch (e) { /* never surfaces */ }


  function visitorType() {
    try { if (localStorage.getItem('sw.traffic.who') === 'team') return 'team' } catch (e) {}
    if (new URLSearchParams(location.search).get('sw-synthetic') === '1') put('synthetic', 1)
    if (get('synthetic') === '1') return 'synthetic'
    const ua = navigator.userAgent || ''
    if (/Googlebot|Google-InspectionTool|Storebot-Google|AdsBot-Google|bingbot|BingPreview|Applebot|DuckDuckBot|YandexBot|Baiduspider|Lighthouse|GPTBot|ClaudeBot|PerplexityBot|CCBot|facebookexternalhit|bot\b|crawler|spider/i.test(ua)) return 'crawler'
    if (navigator.webdriver || /HeadlessChrome/.test(ua)) return 'crawler'
    return 'person'
  }

  function zone() {
    try { const z = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; return /^[A-Za-z_]+(\/[A-Za-z_+-]+){0,2}$/.test(z) ? z.slice(0, 40) : '' } catch (e) { return '' }
  }
  function language() {
    const l = (navigator.languages && navigator.languages[0]) || navigator.language || ''
    return /^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,4})?$/.test(l) ? l : ''
  }

  // sgit hybrid envelope v2 (as the PHP site and sgit PKI): AES-256-GCM, key wrapped with RSA-OAEP-SHA256;
  // payload = base64 of the base64 text of {v:2,w,i,c}.
  async function envelope(pem, text) {
    const der = Uint8Array.from(atob(pem.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '')), c => c.charCodeAt(0)).buffer
    const b64 = bytes => { let s = ''; for (const x of new Uint8Array(bytes)) s += String.fromCharCode(x); return btoa(s) }
    const pub = await crypto.subtle.importKey('spki', der, { name: 'RSA-OAEP', hash: 'SHA-256' }, false, ['encrypt'])
    const aes = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt'])
    const iv = crypto.getRandomValues(new Uint8Array(12))
    const c = await crypto.subtle.encrypt({ name: 'AES-GCM', iv, tagLength: 128 }, aes, new TextEncoder().encode(text))
    const w = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pub, await crypto.subtle.exportKey('raw', aes))
    return btoa(btoa(JSON.stringify({ v: 2, w: b64(w), i: b64(iv), c: b64(c) })))
  }
})()
