// The briefing page: reads JSON from GitHub at view time and draws it. Text goes in with textContent only,
// links only when they are https, and the page fetches only raw.githubusercontent.com/SovereignWebsite/ addresses.
(function () {
  'use strict';
  var SPINE = 'https://raw.githubusercontent.com/SovereignWebsite/Site__Agent__Maestro__Claude__6/dev/site/factory/dinis-cruz/account-f/briefing.json';
  var QUESTIONS = 'https://raw.githubusercontent.com/SovereignWebsite/Site__Agent__Decisions/dev/site/factory/dinis-cruz/account-f/questions.json';
  var OK = /^https:\/\/raw\.githubusercontent\.com\/SovereignWebsite\//;
  var status = [];

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = String(text);
    return e;
  }
  function link(url, text) {
    if (typeof url !== 'string' || !/^https:\/\//.test(url)) return el('span', '', text || '');
    var a = el('a', '', text || url);
    a.href = url; a.rel = 'noopener noreferrer';
    return a;
  }
  function clear(id) { var n = document.getElementById(id); while (n.firstChild) n.removeChild(n.firstChild); return n; }
  function get(url, label) {
    if (!OK.test(url)) { status.push({ label: label, url: url, ok: false, why: 'not a SovereignWebsite raw GitHub address' }); return Promise.resolve(null); }
    return fetch(url + '?t=' + Date.now(), { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (j) {
      status.push({ label: label, url: url, ok: true, updated: j && (j.updated || j.as_of) });
      return j;
    }).catch(function (e) {
      status.push({ label: label, url: url, ok: false, why: String(e.message || e) });
      return null;
    });
  }

  function paste(line, id) {
    var box = el('div', 'paste');
    box.appendChild(el('code', '', line));
    var b = el('button', '', 'Copy');
    b.type = 'button';
    b.addEventListener('click', function () {
      function done(ok) { b.textContent = ok ? 'Copied' : 'Select and copy'; setTimeout(function () { b.textContent = 'Copy'; }, 2000); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(line).then(function () { done(true); }, function () { done(false); });
      else done(false);
    });
    box.appendChild(b);
    if (id) {
      var t = el('button', 'tick', 'pasted?'); t.type = 'button';
      t.addEventListener('click', function () { if (markPasted(id)) load(); else t.textContent = 'cannot save here'; });
      box.appendChild(t);
    }
    return box;
  }

  function draftCard(d) {
    var c = el('div', 'card');
    c.appendChild(el('h3', '', (d.title || d.id || 'Draft') + (d.status ? ' (' + d.status + ')' : '')));
    if (d.drafted) c.appendChild(el('p', 'muted', 'Drafted ' + d.drafted));
    var posts = d.posts || {};
    Object.keys(posts).forEach(function (k) {
      var p = posts[k] || {};
      var sec = el('div');
      sec.appendChild(el('h4', '', k.replace(/_/g, ' ')));
      if (p.title) { sec.appendChild(el('p', 'muted', 'Title')); sec.appendChild(el('div', 'caption', p.title)); }
      var body = p.caption || p.text || p.description;
      if (body) { sec.appendChild(el('p', 'muted', p.caption ? 'Caption as it would appear' : p.text ? 'Post as it would appear' : 'Description')); sec.appendChild(el('div', 'caption', body)); }
      if (p.title && p.description && body !== p.description) { sec.appendChild(el('p', 'muted', 'Description')); sec.appendChild(el('div', 'caption', p.description)); }
      if (p.note) sec.appendChild(el('p', 'muted', 'Note: ' + p.note));
      c.appendChild(sec);
    });
    if (d.labels && d.labels.disclosure) { c.appendChild(el('h4', '', 'Disclosure')); c.appendChild(el('div', 'caption', d.labels.disclosure)); }
    if (d.labels && d.labels.not_used) c.appendChild(el('p', 'muted', d.labels.not_used));
    if (d.credit) c.appendChild(el('p', 'muted', 'Credit: ' + d.credit));
    if (d.scheduled_time) c.appendChild(el('p', 'muted', 'Scheduled: ' + (typeof d.scheduled_time === 'string' ? d.scheduled_time : JSON.stringify(d.scheduled_time))));
    if (d.alt_text) { c.appendChild(el('h4', '', 'Alt text')); c.appendChild(el('div', 'caption', d.alt_text)); }
    if (d.checks) c.appendChild(el('p', 'muted', 'Checks: ' + (typeof d.checks === 'string' ? d.checks : JSON.stringify(d.checks))));
    return c;
  }

  function drawReview(list) {
    var n = clear('review');
    var jobs = [];
    (list || []).forEach(function (r) {
      if (r.kind === 'social-draft' && r.json) {
        var holder = el('div');
        n.appendChild(el('p', '', r.what || 'Social draft'));
        n.appendChild(holder);
        jobs.push(get(r.json, 'Draft: ' + (r.what || r.json)).then(function (d) {
          if (!d) holder.appendChild(el('p', 'bad', 'This draft did not load. Open it on GitHub: ')), holder.appendChild(link(r.json.replace('raw.githubusercontent.com', 'github.com').replace('/dev/', '/blob/dev/'), 'the draft'));
          else holder.appendChild(draftCard(d));
        }));
      } else {
        var c = el('div', 'card');
        c.appendChild(el('p', '', r.what || ''));
        var u = r.url || r.json;
        if (u) c.appendChild(link(u, u));
        n.appendChild(c);
      }
    });
    if (!n.firstChild) n.appendChild(el('p', '', 'Nothing to review.'));
    return Promise.all(jobs);
  }


  // One merged list (design: cells/2026-11-27-briefing-page-layout.md, Site__Agent__Design 42727bc). Key by id; questions.json wins and
  // briefing.json fills gaps; the same line to paste is the same row. Groups: Now, Today, Later (collapsed), Done (collapsed).
  var PASTED = 'briefing-pasted-ids';
  function pastedSet() { try { return JSON.parse(localStorage.getItem(PASTED) || '[]'); } catch (e) { return []; } }
  function markPasted(id) { try { var s = pastedSet(); if (s.indexOf(id) < 0) s.push(id); localStorage.setItem(PASTED, JSON.stringify(s)); return true; } catch (e) { return false; } }

  function norm(q) {
    var ctx = q.context_url || q.session || q.where || '';
    if (/^session_[A-Za-z0-9]+$/.test(ctx)) ctx = 'https://claude.ai/code/' + ctx;
    var u = String(q.urgency || '').trim();
    var first = (u.toLowerCase().match(/^[a-z]+/) || [''])[0];
    var group = first === 'now' ? 'now' : (first === 'today' || first === 'high') ? 'today' : 'later';
    var deadline = u.replace(/^[A-Za-z]+\s*[:,;-]?\s*/, '').trim();
    var status = String(q.status || '').toLowerCase();
    return {
      id: q.id || '', title: q.question || q.title || q.what || q.id || 'Question',
      line: q.line_to_paste || q.line_for_dinis || q.line || '',
      where: ctx, answer: q.answer_url || '', opened: q.since || q.opened || '', closed: q.closed || '',
      by: q.asked_by || '', chip: first || 'later', group: group, deadline: deadline,
      done: !!q.closed || /^(answered|withdrawn|closed|done|dropped)/.test(status), status: status
    };
  }

  function passed(deadline) {
    var m = /(\d{1,2}):(\d{2})\s*UTC/i.exec(deadline || '');
    if (!m) return false;
    var now = new Date();
    return (+m[1]) * 60 + (+m[2]) < now.getUTCHours() * 60 + now.getUTCMinutes();
  }

  function row(q, group) {
    var c = el('div', 'row g-' + group + (group === 'done' ? ' done' : ''));
    var top = el('div', 'rtop');
    top.appendChild(el('span', 'tag t-' + group, group === 'done' ? (q.status === 'withdrawn' ? 'Withdrawn' : 'Done') : group === 'now' ? 'Now' : group === 'today' ? 'Today' : 'Later'));
    if (q.deadline && group !== 'done') top.appendChild(el('span', 'deadline', (passed(q.deadline) ? 'passed: ' : '') + q.deadline));
    c.appendChild(top);
    var t = el('p', 'rtitle' + (group === 'done' ? ' struck' : ''), q.title);
    t.classList.add('clamp');
    c.appendChild(t);
    if (q.title.length > 110) {
      var more = el('button', 'linkbtn', 'more'); more.type = 'button';
      more.addEventListener('click', function () { var on = t.classList.toggle('clamp'); more.textContent = on ? 'more' : 'less'; });
      c.appendChild(more);
    }
    if (group !== 'done') {
      if (q.line) c.appendChild(paste(q.line, q.id));
      else c.appendChild(el('div', 'noline', 'No line to paste: open the session'));
      if (q.where) {
        var pi = el('p', 'pastein'); pi.appendChild(document.createTextNode('Paste in: '));
        var a = link(q.where, 'Open session'); a.className = 'btn'; pi.appendChild(a); c.appendChild(pi);
      }
    } else if (q.answer) { var an = el('p', 'meta'); an.appendChild(link(q.answer, 'Answer')); c.appendChild(an); }
    var bits = [];
    if (q.by) bits.push('asked by ' + q.by);
    if (q.opened) bits.push('since ' + q.opened);
    if (q.closed) bits.push('closed ' + q.closed);
    if (q.id) bits.push(q.id);
    if (bits.length) c.appendChild(el('p', 'meta', bits.join(' · ')));
    return c;
  }

  function group(n, key, title, items, collapsed) {
    var box = el(collapsed ? 'details' : 'div', 'grp');
    if (collapsed && key === 'later' && items.length) box.open = false;
    var head = el(collapsed ? 'summary' : 'h2', 'ghead', title + ' (' + items.length + ')');
    if (collapsed && items.length) head.appendChild(el('span', 'peek', ' ' + items.slice(0, 2).map(function (q) { return q.title.slice(0, 60); }).join(' · ')));
    box.appendChild(head);
    items.forEach(function (q) { box.appendChild(row(q, key)); });
    if (!items.length && !collapsed) box.appendChild(el('p', '', key === 'now' ? 'Nothing needs you now.' : 'Nothing today.'));
    if (items.length || !collapsed) n.appendChild(box);
  }

  function drawNeeds(waiting, qdata, qfailed, bfailed) {
    var n = clear('needs');
    var qs = qdata ? (Array.isArray(qdata) ? qdata : (qdata.questions || qdata.items || [])) : [];
    var map = {}, order = [], lines = {};
    function add(q, wins) {
      var r = norm(q);
      var key = r.id ? 'i:' + r.id : (r.line ? 'l:' + r.line : 'x' + order.length);
      var lk = r.line && lines[r.line];
      if (lk) key = lk;
      if (map[key]) {
        var cur = map[key];
        if (wins) { Object.keys(r).forEach(function (f) { if (r[f] !== '' && r[f] !== false) cur[f] = r[f]; }); }
        else Object.keys(r).forEach(function (f) { if (!cur[f] && r[f]) cur[f] = r[f]; });
      } else { map[key] = r; order.push(key); }
      if (r.line) lines[r.line] = key;
    }
    qs.forEach(function (q) { add(q, true); });
    (waiting || []).forEach(function (w) { add(w, false); });
    var list = order.map(function (k) { return map[k]; });
    var mine = pastedSet();
    list.forEach(function (q) { if (q.id && mine.indexOf(q.id) >= 0) { q.done = true; q.status = q.status || 'pasted'; } });
    if (qfailed && bfailed) { n.appendChild(el('p', 'bad', 'The briefing did not load.')); return; }
    if (qfailed) n.appendChild(el('p', 'bad', 'questions.json did not load; showing briefing.json only.'));
    if (bfailed && !qfailed) n.appendChild(el('p', 'bad', 'briefing.json did not load; showing questions.json only.'));
    var open = list.filter(function (q) { return !q.done; });
    function by(a, b) { return (b.deadline ? 1 : 0) - (a.deadline ? 1 : 0) || String(a.opened).localeCompare(String(b.opened)); }
    var g = { now: [], today: [], later: [] };
    open.forEach(function (q) { g[q.group].push(q); });
    Object.keys(g).forEach(function (k) { g[k].sort(by); });
    var done = list.filter(function (q) { return q.done; });
    document.getElementById('counts').textContent = g.now.length + ' now, ' + g.today.length + ' today, ' + g.later.length + ' later';
    group(n, 'now', 'Now', g.now, false);
    group(n, 'today', 'Today', g.today, false);
    group(n, 'later', 'Later', g.later, true);
    group(n, 'done', 'Done', done, true);
    n.appendChild(el('p', 'meta', 'The "pasted?" tick moves a row to Done on this device only (kept in this browser, not shared).'));
  }

  function drawFlags(a) {
    var n = clear('flags');
    if (!a) { n.appendChild(el('p', 'bad', 'The agents view did not load.')); return; }
    n.appendChild(el('p', 'muted', 'Agents data as of ' + (a.as_of || 'unknown') + '. ' + ((a.summary && a.summary.sessions_live) || '?') + ' live sessions.'));
    var s = a.summary || {};
    function row(label, items) {
      var c = el('div', 'card' + (items && items.length ? ' high' : ''));
      c.appendChild(el('strong', '', label + ': '));
      c.appendChild(document.createTextNode(items && items.length ? items.join(', ') : 'none'));
      n.appendChild(c);
    }
    row('Handover due (past 50% of the window)', s.handover_due);
    row('Close to 50%', s.near_half);
    row('Within 10% of auto-compaction', s.near_compaction);
    row('More repositories than the rest', s.more_repos_than_expected);
    row('A wake firing into an archived session', s.wake_into_archived);
    row('Idle or blocked with a needs_action', s.idle_with_needs_action);
    n.appendChild(el('p', '', 'Full table: '));
    n.lastChild.appendChild(link('https://observability.agents.sovereignweb.site/factory/dinis-cruz/account-f/agents/', 'the agents page'));
  }

  function drawProjects(list) {
    var n = clear('projects');
    (list || []).forEach(function (p) {
      var c = el('div', 'card');
      c.appendChild(el('h3', '', p.name || ''));
      if (p.conductor) c.appendChild(el('p', 'muted', 'Conductor: ' + p.conductor));
      if (p.state) c.appendChild(el('p', '', p.state));
      if (p.session) c.appendChild(link(p.session, 'Conductor session'));
      n.appendChild(c);
    });
    if (!n.firstChild) n.appendChild(el('p', '', 'No projects listed.'));
  }

  function drawDecisions(list) {
    var n = clear('decisions');
    (list || []).forEach(function (d) {
      var li = el('li');
      li.appendChild(el('span', 'muted', (d.date || '') + ' '));
      li.appendChild(link(d.url, d.title || d.url));
      n.appendChild(li);
    });
    if (!n.firstChild) n.appendChild(el('li', '', 'No decisions listed.'));
  }

  function drawCosts(c) {
    var n = clear('costs');
    if (!c) { n.appendChild(el('li', 'bad', 'cost-events.json did not load.')); return; }
    (c.events || []).slice(-8).reverse().forEach(function (e) {
      n.appendChild(el('li', '', (e.at || '') + '  ' + (e.kind || '') + '  ' + (e.agent || '') + (e.why ? ': ' + e.why : '')));
    });
  }

  function drawSources() {
    var n = clear('sources');
    status.forEach(function (s) {
      var li = el('li');
      li.appendChild(el('strong', s.ok ? '' : 'bad', (s.ok ? 'Loaded' : 'Failed') + ': '));
      li.appendChild(link(s.url, s.label));
      li.appendChild(el('span', 'muted', s.ok ? (s.updated ? '  updated ' + s.updated : '') : '  ' + s.why));
      n.appendChild(li);
    });
  }

  function load() {
    status = [];
    document.getElementById('loaded').textContent = 'Loading...';
    var ln = clear('needs'); ln.appendChild(el('div', 'row skeleton', 'Loading the briefing')); 
    get(SPINE, 'Briefing (maestro)').then(function (b) {
      if (!b) {
        ['review', 'projects'].forEach(function (id) { var n = clear(id); n.appendChild(el('p', 'bad', 'The briefing did not load, so this is empty. See Sources.')); });
        get(QUESTIONS, 'Questions (decisions)').then(function (q) { drawNeeds([], q, !q, true); drawSources(); });
        clear('decisions'); clear('costs'); clear('flags'); drawSources();
        document.getElementById('loaded').textContent = 'Failed at ' + new Date().toISOString();
        return;
      }
      var src = b.sources || {};
      drawProjects(b.projects);
      drawDecisions(b.decisions);
      var qp = get(src.questions || QUESTIONS, 'Questions (decisions)').then(function (q) { drawNeeds(b.waiting_on_dinis, q, !q, false); });
      return Promise.all([
        qp,
        drawReview(b.to_review),
        src.agents_view ? get(src.agents_view, 'Agents view (observability)').then(drawFlags) : null,
        src.sessions ? get(src.sessions, 'Sessions (maestro)') : null,
        src.cost_events ? get(src.cost_events, 'Cost events (maestro)').then(drawCosts) : null
      ]).then(function () {
        drawSources();
        document.getElementById('loaded').textContent = 'Briefing updated ' + (b.updated || 'unknown') + '; loaded at ' + new Date().toISOString();
      });
    });
  }

  document.getElementById('reload').addEventListener('click', load);
  load();
})();
