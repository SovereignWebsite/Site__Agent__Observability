// Runs work/traffic/traffic.js (read-only) in a fake browser, with the recipient set to THIS agent's own public key,
// decrypts what it would have sent with this agent's own private key (read from the path in SW_PRIV, never printed),
// and checks the note. No network, no vault, no token.
//   SW_PRIV=~/.sw-secret/encrypt.pem SW_PUB=~/.sw-secret/encrypt.pub node tests/test_script.mjs   (from the repository root)
import fs from 'node:fs'; import vm from 'node:vm'; import crypto from 'node:crypto'; import assert from 'node:assert'
const src = fs.readFileSync('work/traffic/traffic.js', 'utf8')
const pub = fs.readFileSync(process.env.SW_PUB, 'utf8'), priv = fs.readFileSync(process.env.SW_PRIV, 'utf8')
const store = () => { const m = new Map(); return { getItem: k => m.has(k) ? m.get(k) : null, setItem: (k, v) => m.set(k, String(v)), m } }
async function run({ host = 'a.example', href = 'https://a.example/p', ua = 'Mozilla/5.0 Firefox/130', dnt = null, gpc, webdriver, session = store(), local = store(), status = 200, lanes = ['L1', 'L2'] } = {}) {
  const sent = []
  const u = new URL(href)
  const ctx = {
    window: { crypto: globalThis.crypto }, crypto: globalThis.crypto, TextEncoder, Uint8Array, URLSearchParams, Intl, JSON, Date, Promise, parseInt, Array, encodeURIComponent, atob, btoa, String, Math,
    sessionStorage: session, localStorage: local,
    location: { hostname: u.hostname, protocol: u.protocol, pathname: u.pathname, search: u.search },
    navigator: { doNotTrack: dnt, globalPrivacyControl: gpc, webdriver, userAgent: ua, languages: ['en-GB'], language: 'en-GB' },
    fetch: async (url, opt) => {
      if (url === '/traffic.json') return { json: async () => ({ enabled: true, endpoint: 'https://v.example', vault_id: 'v1', lanes, recipient: { encrypt: pub }, hosts: ['a.example'] }) }
      sent.push({ url, opt, body: JSON.parse(opt.body) }); return { ok: status === 200, status }
    },
  }
  ctx.window.fetch = ctx.fetch; vm.createContext(ctx); vm.runInContext(src, ctx); await new Promise(r => setTimeout(r, 400))
  return { sent, session }
}
function open(payload) {
  const env = JSON.parse(Buffer.from(Buffer.from(payload, 'base64').toString(), 'base64').toString())
  const key = crypto.privateDecrypt({ key: priv, oaepHash: 'sha256', padding: crypto.constants.RSA_PKCS1_OAEP_PADDING }, Buffer.from(env.w, 'base64'))
  const c = Buffer.from(env.c, 'base64'), d = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(env.i, 'base64'))
  d.setAuthTag(c.subarray(c.length - 16)); return JSON.parse(Buffer.concat([d.update(c.subarray(0, c.length - 16)), d.final()]).toString())
}
let n = 0; const ok = (name, f) => f().then(() => { n++; console.log('ok', name) })
await ok('one encrypted note, opens, right fields, no extras', async () => {
  const { sent } = await run(); assert.equal(sent.length, 1)
  assert.match(sent[0].url, /\/api\/vault\/append\/write\/v1$/); assert.equal(sent[0].opt.credentials, 'omit'); assert.equal(sent[0].opt.referrerPolicy, 'no-referrer')
  assert.deepEqual(Object.keys(sent[0].body).sort(), ['append_token', 'payload'])
  const note = open(sent[0].body.payload)
  assert.deepEqual(Object.keys(note).sort(), ['lang', 'path', 'site', 'tab', 'ts', 'type', 'tz', 'v'].sort())
  assert.equal(note.site, 'a.example'); assert.equal(note.path, '/p'); assert.equal(note.type, 'person'); assert.match(note.ts, /^\d{4}-\d\d-\d\dT\d\d:\d\dZ$/)
  assert.ok(!JSON.stringify(note).includes('Firefox'))
})
await ok('query and hash never sent', async () => { const { sent } = await run({ href: 'https://a.example/p?email=x@y.z' }); assert.equal(open(sent[0].body.payload).path, '/p') })
await ok('Do Not Track sends nothing', async () => assert.equal((await run({ dnt: '1' })).sent.length, 0))
await ok('Global Privacy Control sends nothing', async () => assert.equal((await run({ gpc: true })).sent.length, 0))
await ok('localhost and http send nothing', async () => { assert.equal((await run({ href: 'https://localhost/p' })).sent.length, 0); assert.equal((await run({ href: 'http://a.example/p' })).sent.length, 0) })
await ok('host not in config sends nothing', async () => assert.equal((await run({ href: 'https://b.example/p' })).sent.length, 0))
await ok('crawler, webdriver, team, synthetic types', async () => {
  assert.equal(open((await run({ ua: 'Mozilla/5.0 (compatible; Googlebot/2.1)' })).sent[0].body.payload).type, 'crawler')
  assert.equal(open((await run({ webdriver: true })).sent[0].body.payload).type, 'crawler')
  const local = store(); local.setItem('sw.traffic.who', 'team'); assert.equal(open((await run({ local })).sent[0].body.payload).type, 'team')
  assert.equal(open((await run({ href: 'https://a.example/p?sw-synthetic=1' })).sent[0].body.payload).type, 'synthetic')
})
await ok('same page twice in a tab sends one note; the tab id is reused', async () => {
  const session = store(); await run({ session }); const r = await run({ session }); assert.equal(r.sent.length, 0)
  const r2 = await run({ session, href: 'https://a.example/q' }); assert.equal(r2.sent.length, 1)
})
await ok('cap of 40 notes per tab', async () => {
  const session = store(); let total = 0
  for (let i = 0; i < 45; i++) total += (await run({ session, href: 'https://a.example/p' + i })).sent.length
  assert.equal(total, 40)
})
await ok('full lane (507) falls over to the next lane; 400 does not', async () => {
  let r = await run({ status: 507 }); assert.equal(r.sent.length, 2); assert.notEqual(r.sent[0].body.append_token, r.sent[1].body.append_token)
  r = await run({ status: 400 }); assert.equal(r.sent.length, 1)
})
await ok('nothing is written to the device but the tab keys', async () => {
  const session = store(), local = store(); await run({ session, local }); assert.equal(local.m.size, 0)
  for (const k of session.m.keys()) assert.match(k, /^sw\.traffic\./)
})
console.log(n, 'passed')
