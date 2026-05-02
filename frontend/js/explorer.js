// frontend/js/explorer.js
// Handles the Country Explorer tab — fetches country data from the API,
// renders the grid of cards, bar chart, and the detail panel when a card is clicked.

let allCountries = [];
let selectedIdx  = null;

async function initExplorer() {
  const grid  = document.getElementById('country-grid');
  const chart = document.getElementById('bar-chart');
  grid.innerHTML  = '<div class="loading">Loading countries...</div>';
  chart.innerHTML = '';

  try {
    const res  = await fetch('/api/countries');
    allCountries = await res.json();
  } catch (e) {
    grid.innerHTML = '<div class="empty">Could not load data. Is the server running?</div>';
    return;
  }

  renderGrid();
  renderChart();
}

function renderGrid() {
  const grid = document.getElementById('country-grid');
  grid.innerHTML = allCountries.map((c, i) => {
    const cls = scoreClass(c.openness_score);
    const preview = (c.summary || '').substring(0, 90) + '...';
    return `
      <div class="c-card ${selectedIdx === i ? 'sel' : ''}" onclick="selectCountry(${i})">
        <div class="c-top">
          <span class="c-name">${c.country}</span>
          <span class="score ${cls}">${c.openness_score}</span>
        </div>
        <div class="c-region">${c.organization || ''}</div>
        <div class="c-summary">${preview}</div>
      </div>`;
  }).join('');
}

function renderChart() {
  const wrap = document.getElementById('bar-chart');
  const sorted = [...allCountries].sort((a, b) => b.openness_score - a.openness_score);
  wrap.innerHTML = sorted.map(c => `
    <div class="bar-row">
      <span class="bar-label">${c.country}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:${c.openness_score * 10}%; background:${scoreColor(c.openness_score)};"></div>
      </div>
      <span class="bar-val">${c.openness_score}/10</span>
    </div>`).join('');
}

async function selectCountry(i) {
  selectedIdx = i;
  renderGrid(); // re-render to show selected state

  const c   = allCountries[i];
  const det = document.getElementById('country-detail');
  det.innerHTML = '<div class="loading">Loading profile...</div>';

  try {
    const res  = await fetch(`/api/country/${encodeURIComponent(c.country)}`);
    const data = await res.json();
    renderDetail(data.country, data.topics);
  } catch (e) {
    det.innerHTML = '<div class="empty">Could not load country detail.</div>';
  }
}

function renderDetail(c, topics) {
  const det     = document.getElementById('country-detail');
  const cls     = scoreClass(c.openness_score);
  const laws    = (c.key_laws || []).map(l => `<span class="pill p-gray">${l}</span>`).join('');
  const feats   = (c.notable_features || []).map(f => `<span class="pill p-blue">${f}</span>`).join('');

  const topicRows = (topics || []).map(t => {
    const pillCls = strictnessPill(t.strictness);
    return `
      <tr>
        <td class="topic-name">${t.topic}</td>
        <td class="topic-details">${t.status || '—'}</td>
        <td><span class="pill ${pillCls}">${t.strictness || 'None'}</span></td>
        <td class="topic-details">${t.details || '—'}</td>
      </tr>`;
  }).join('');

  det.innerHTML = `
    <div class="detail-wrap">
      <div class="detail-header">
        <div>
          <div class="detail-title">${c.country}</div>
          <div class="detail-org">${c.organization || ''}</div>
        </div>
        <span class="score ${cls}" style="font-size:14px;padding:4px 12px;">${c.openness_score}/10</span>
      </div>
      <div class="detail-body">
        <p class="detail-summary">${c.summary || 'No summary available.'}</p>

        <div class="detail-pills" style="margin-bottom:8px;">
          <div class="detail-pills-label">Notable features</div>
          ${feats || '<span class="pill p-gray">No data</span>'}
        </div>

        <div class="detail-pills" style="margin-bottom:16px;">
          <div class="detail-pills-label">Key laws</div>
          ${laws || '<span class="pill p-gray">No data</span>'}
        </div>

        <div class="detail-pills-label" style="margin-bottom:8px;">Topic breakdown</div>
        <div style="overflow-x:auto;">
          <table class="topic-table">
            <thead>
              <tr>
                <th>Topic</th>
                <th>Status</th>
                <th>Strictness</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>${topicRows}</tbody>
          </table>
        </div>
      </div>
    </div>`;

  // scroll down to detail smoothly
  det.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── helpers ──────────────────────────────────────────────

function scoreClass(s) {
  return s >= 7 ? 's-hi' : s >= 5 ? 's-md' : 's-lo';
}

function scoreColor(s) {
  return s >= 7 ? 'var(--green)' : s >= 5 ? 'var(--amber)' : 'var(--red)';
}

function strictnessPill(s) {
  if (s === 'Low')  return 'p-green';
  if (s === 'Medium' || s === 'Med') return 'p-amber';
  if (s === 'High') return 'p-red';
  return 'p-gray';
}
