// The briefing page: reads JSON from GitHub at view time and draws it. Text goes in with textContent only,
// links only when they are https, and the page fetches only raw.githubusercontent.com/SovereignWebsite/ addresses.
(function () {
  'use strict';
  var SPINE = 'https://raw.githubusercontent.com/SovereignWebsite/Site__Agent__Maestro__Claude__6/dev/site/factory/dinis-cruz/account-f/briefing.json';
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

  function paste(line) {
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
    return box;
  }

  function drawWait(list) {
    var n = clear('wait');
    var rank = { high: 0, medium: 1, low: 2 };
    (list || []).slice().sort(function (a, b) { return (rank[a.urgency] === undefined ? 3 : rank[a.urgency]) - (rank[b.urgency] === undefined ? 3 : rank[b.urgency]); }).forEach(function (w) {
      var c = el('div', 'card ' + (rank[w.urgency] !== undefined ? w.urgency : ''));
      var p = el('p');
      p.appendChild(el('span', 'tag', w.urgency || 'n/a'));
      p.appendChild(document.createTextNode(w.what || ''));
      c.appendChild(p);
      if (w.where) { var q = el('p', 'muted'); q.appendChild(document.createTextNode('Where: ')); q.appendChild(link(w.where, w.where)); c.appendChild(q); }
      if (w.line) { c.appendChild(el('p', 'muted', 'Paste this line:')); c.appendChild(paste(w.line)); }
      n.appendChild(c);
    });
    if (!n.firstChild) n.appendChild(el('p', '', 'Nothing is waiting on Dinis.'));
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
    get(SPINE, 'Briefing (maestro)').then(function (b) {
      if (!b) {
        ['wait', 'review', 'projects'].forEach(function (id) { var n = clear(id); n.appendChild(el('p', 'bad', 'The briefing did not load, so this is empty. See Sources.')); });
        clear('decisions'); clear('costs'); clear('flags'); drawSources();
        document.getElementById('loaded').textContent = 'Failed at ' + new Date().toISOString();
        return;
      }
      var src = b.sources || {};
      drawWait(b.waiting_on_dinis);
      drawProjects(b.projects);
      drawDecisions(b.decisions);
      return Promise.all([
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
