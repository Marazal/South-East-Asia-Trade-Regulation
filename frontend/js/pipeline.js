// frontend/js/pipeline.js
// Handles the Pipeline Finder tab — populates the country dropdowns,
// calls /api/pipeline, and renders the ranked route cards.

async function initPipeline() {
  try {
    const res  = await fetch('/api/countries');
    const data = await res.json();
    populateSelects(data);
  } catch (e) {
    console.error('Could not load countries for pipeline selects:', e);
  }
}

function populateSelects(countries) {
  const src = document.getElementById('src-sel');
  const dst = document.getElementById('dst-sel');

  // group by region for cleaner UX
  const regions = [...new Set(countries.map(c => c.organization?.split('/')[0] || 'Other'))];
  const byRegion = {};

  countries.forEach(c => {
    // use openness_score to label each option
    const label = `${c.country}  (${c.openness_score}/10)`;
    if (!byRegion[c.country]) byRegion[c.country] = label;
  });

  [src, dst].forEach(sel => {
    sel.innerHTML = '<option value="">— Select economy —</option>';
    countries.forEach(c => {
      const opt = document.createElement('option');
      opt.value       = c.country;
      opt.textContent = `${c.country}  (${c.openness_score}/10)`;
      sel.appendChild(opt);
    });
  });

  // sensible defaults so users can see a result immediately
  src.value = 'Thailand';
  dst.value = 'Japan';
}

async function runPipeline() {
  const srcName = document.getElementById('src-sel').value;
  const dstName = document.getElementById('dst-sel').value;
  const results = document.getElementById('pipeline-results');

  if (!srcName || !dstName) {
    results.innerHTML = '<div class="empty">Please select both a source and destination economy.</div>';
    return;
  }
  if (srcName === dstName) {
    results.innerHTML = '<div class="empty">Source and destination must be different economies.</div>';
    return;
  }

  results.innerHTML = '<div class="loading">Calculating all pipelines...</div>';

  try {
    const url = `/api/pipeline?src=${encodeURIComponent(srcName)}&dst=${encodeURIComponent(dstName)}`;
    const res  = await fetch(url);
    const data = await res.json();

    if (data.error) {
      results.innerHTML = `<div class="empty">${data.error}</div>`;
      return;
    }

    renderPipelineResults(data.routes, srcName, dstName);
  } catch (e) {
    results.innerHTML = '<div class="empty">Error fetching pipeline data. Is the server running?</div>';
  }
}

function renderPipelineResults(routes, srcName, dstName) {
  const results = document.getElementById('pipeline-results');
  if (!routes || routes.length === 0) {
    results.innerHTML = '<div class="empty">No pipeline routes found.</div>';
    return;
  }

  const best = routes[0];

  // build the best-route node visualisation
  const bestNodes = best.nodes.map((n, i) => {
    const cls = i === 0 ? 'pn-src' : i === best.nodes.length - 1 ? 'pn-dst' : 'pn-hub';
    const arrow = i < best.nodes.length - 1 ? '<span class="p-arrow">→</span>' : '';
    return `<span class="p-node ${cls}">${n}</span>${arrow}`;
  }).join('');

  const effColor = effToColor(best.efficiency);

  const html = `
    <div class="section-head">
      <h2>Most efficient pipeline</h2>
    </div>

    <div class="best-card">
      <span class="best-tag">Recommended · #1 of ${routes.length} routes found</span>
      <div class="p-vis">${bestNodes}</div>
      <div class="scores-row">
        <div class="sc-box">
          <div class="v" style="color:${effColor}">${best.efficiency}%</div>
          <div class="l">Efficiency</div>
        </div>
        <div class="sc-box">
          <div class="v">${best.setup_weeks}w</div>
          <div class="l">Est. setup</div>
        </div>
        <div class="sc-box">
          <div class="v">${best.tariff}%</div>
          <div class="l">Avg tariff</div>
        </div>
        <div class="sc-box">
          <div class="v">${best.data_risk}</div>
          <div class="l">Data risk</div>
        </div>
      </div>
      <div style="font-size:11px;font-weight:600;color:var(--muted);margin-bottom:6px;">WHY THIS ROUTE WINS</div>
      <div class="tag-row">
        ${(best.pros || []).map(p => `<span class="t-lo">${p}</span>`).join('')}
      </div>
    </div>

    <div class="section-head" style="margin-top:4px;">
      <h2>All possible pipelines — ${routes.length} routes</h2>
    </div>

    <div class="legend-row">
      <div class="leg-item">
        <div class="leg-dot" style="background:var(--blue-l);border:1px solid #A8D8EE;"></div>
        Source
      </div>
      <div class="leg-item">
        <div class="leg-dot" style="background:var(--purple-l);border:1px solid #C4C0F5;"></div>
        Transit hub / bloc
      </div>
      <div class="leg-item">
        <div class="leg-dot" style="background:var(--green-l);border:1px solid #A8DBBF;"></div>
        Destination
      </div>
      <div class="leg-item">
        <div class="leg-dot" style="background:var(--green);"></div>
        75%+ efficient
      </div>
      <div class="leg-item">
        <div class="leg-dot" style="background:var(--amber);"></div>
        55–74%
      </div>
      <div class="leg-item">
        <div class="leg-dot" style="background:var(--red);"></div>
        Under 55%
      </div>
    </div>

    ${routes.map((r, i) => renderPipeItem(r, i + 1, i === 0)).join('')}
  `;

  results.innerHTML = html;
}

function renderPipeItem(route, rank, expanded) {
  const nodes = route.nodes.map((n, i) => {
    const cls   = i === 0 ? 'mn-s' : i === route.nodes.length - 1 ? 'mn-e' : 'mn-h';
    const arrow = i < route.nodes.length - 1 ? '<span class="mn-a">→</span>' : '';
    return `<span class="mn ${cls}">${n}</span>${arrow}`;
  }).join('');

  const riskTag  = route.data_risk === 'High' ? 't-hi' : route.data_risk === 'Medium' ? 't-md' : 't-lo';
  const effColor = effToColor(route.efficiency);

  return `
    <div class="pipe-item ${expanded ? 'open' : ''}" id="pipe-${rank}" onclick="togglePipe(${rank})">
      <div class="pipe-top">
        <div class="pipe-nodes">${nodes}</div>
        <div class="pipe-badges">
          <span class="eff" style="background:${effColor}">${route.efficiency}%</span>
          <span class="rank">#${rank}</span>
        </div>
      </div>
      <div class="pipe-sub">
        ${route.type} &nbsp;·&nbsp; ~${route.setup_weeks}w setup &nbsp;·&nbsp; ${route.tariff}% avg tariff &nbsp;·&nbsp; ${route.agreement}
      </div>
      <div class="pipe-detail ${expanded ? 'show' : ''}" id="detail-${rank}">
        <div class="detail-3col">
          <div class="d3"><div class="lbl">Data risk</div><div class="val">${route.data_risk}</div></div>
          <div class="d3"><div class="lbl">Compliance</div><div class="val">${route.compliance || '—'}</div></div>
          <div class="d3"><div class="lbl">Agreement</div><div class="val">${route.agreement}</div></div>
        </div>
        <div style="font-size:11px;font-weight:600;color:var(--muted);margin-bottom:5px;">Advantages</div>
        <div class="tag-row">
          ${(route.pros || []).map(p => `<span class="t-lo">${p}</span>`).join('')}
        </div>
        <div style="font-size:11px;font-weight:600;color:var(--muted);margin:8px 0 5px;">Risks &amp; barriers</div>
        <div class="tag-row">
          ${(route.cons || []).map(c => `<span class="${riskTag}">${c}</span>`).join('')}
        </div>
      </div>
    </div>`;
}

function togglePipe(rank) {
  const item   = document.getElementById(`pipe-${rank}`);
  const detail = document.getElementById(`detail-${rank}`);
  const isOpen = detail.classList.contains('show');
  detail.classList.toggle('show', !isOpen);
  item.classList.toggle('open', !isOpen);
}

// ── helpers ──────────────────────────────────────────────

function effToColor(e) {
  return e >= 75 ? 'var(--green)' : e >= 55 ? 'var(--amber)' : 'var(--red)';
}
