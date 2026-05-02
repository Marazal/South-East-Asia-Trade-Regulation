// frontend/js/guide.js
// Renders the Beginner Guide tab — all static content, no API calls needed.

function initGuide() {
  const el = document.getElementById('guide-content');
  if (!el) return;

  el.innerHTML = `
    <div class="section-head">
      <h2>How to use this tool</h2>
      <p>No background in trade law or tech required — start here.</p>
    </div>

    <div class="guide-card">
      <div class="step">
        <div class="step-num">1</div>
        <div>
          <h3>Browse the Country Explorer</h3>
          <p>
            Start on the first tab. Every card represents one Asia-Pacific economy.
            The score in the top-right corner (out of 10) shows how open that country
            is to digital trade — higher means fewer barriers and easier to trade with.
            Click any card to load a full breakdown of how that country handles each of
            the 12 regulatory topics.
          </p>
        </div>
      </div>

      <div class="step">
        <div class="step-num">2</div>
        <div>
          <h3>Use the Pipeline Finder to plan a route</h3>
          <p>
            Go to the second tab. Pick a source economy (where the trade starts) and a
            destination economy (where it needs to go). Click "Find all pipelines" and the
            tool will calculate every possible regulatory pathway — direct routes and routes
            that go through trade blocs like RCEP, CPTPP, or a hub country like Singapore.
            It ranks all of them by efficiency and shows you the best option first.
          </p>
        </div>
      </div>

      <div class="step">
        <div class="step-num">3</div>
        <div>
          <h3>Click any pipeline card for the full breakdown</h3>
          <p>
            Each route card can be expanded by clicking it. Inside you'll see the data risk
            level, which trade agreement applies, how many weeks setup might take, and a list
            of specific advantages and barriers for that particular route.
          </p>
        </div>
      </div>

      <div class="step">
        <div class="step-num">4</div>
        <div>
          <h3>Check the Glossary if something is unclear</h3>
          <p>
            Every term used in this tool — data localization, RCEP, openness score,
            e-signatures, RDTII — is explained in plain language in the Glossary tab.
            Each entry also has a real-world example.
          </p>
        </div>
      </div>
    </div>

    <div class="section-head" style="margin-top:24px;">
      <h2>What is the openness score?</h2>
    </div>
    <div class="guide-card">
      <div class="step" style="border:none;padding-bottom:4px;">
        <div style="flex:1;">
          <p style="font-size:12px;color:var(--muted);line-height:1.8;margin-bottom:14px;">
            The openness score is a number from 1 to 10 that summarises how easy it is to
            do digital trade with a country. It is calculated from 12 regulatory topics —
            things like whether the country requires data to stay onshore, whether it
            recognises e-signatures, and how high its digital tariffs are.
            A high score means fewer barriers. A low score means more friction.
          </p>
          <div class="score-key">
            <div class="sk">
              <span class="score s-hi">8 – 10</span>
              <p>Very open — few barriers, predictable rules, easy to trade digitally</p>
            </div>
            <div class="sk">
              <span class="score s-md">5 – 7</span>
              <p>Moderate — some restrictions but workable with the right agreements</p>
            </div>
            <div class="sk">
              <span class="score s-lo">1 – 4</span>
              <p>Restrictive — significant barriers, requires careful compliance planning</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="section-head" style="margin-top:24px;">
      <h2>What is a trade pipeline?</h2>
    </div>
    <div class="guide-card">
      <div class="step" style="border:none;padding-bottom:4px;">
        <div style="flex:1;">
          <p style="font-size:12px;color:var(--muted);line-height:1.8;margin-bottom:14px;">
            A trade pipeline is the regulatory path your digital trade takes to get from
            one country to another. Sometimes going directly between two countries is not
            the most efficient route — data restrictions, tariff rules, or legal incompatibilities
            can get in the way. Routing through a trade bloc (like RCEP) or a hub country
            (like Singapore) can reduce that friction significantly.
          </p>
          <div class="p-vis" style="margin-bottom:10px;">
            <span class="p-node pn-src">Thailand</span>
            <span class="p-arrow">→</span>
            <span class="p-node pn-hub">RCEP Zone</span>
            <span class="p-arrow">→</span>
            <span class="p-node pn-dst">Japan</span>
          </div>
          <p style="font-size:11px;color:var(--muted);">
            Blue = where your trade starts &nbsp;·&nbsp; Purple = transit hub or trade bloc &nbsp;·&nbsp; Green = destination
          </p>
        </div>
      </div>
    </div>

    <div class="section-head" style="margin-top:24px;">
      <h2>Color key — used consistently throughout</h2>
    </div>
    <div class="color-grid">
      <div class="ck">
        <div class="ck-dot" style="background:var(--green-l);border:1px solid #A8DBBF;"></div>
        <div><h4>Green</h4><p>Open, low risk, advantage</p></div>
      </div>
      <div class="ck">
        <div class="ck-dot" style="background:var(--amber-l);border:1px solid #FAC76A;"></div>
        <div><h4>Orange / amber</h4><p>Moderate, conditional</p></div>
      </div>
      <div class="ck">
        <div class="ck-dot" style="background:var(--red-l);border:1px solid #F4B0A9;"></div>
        <div><h4>Red</h4><p>Restrictive, high risk, barrier</p></div>
      </div>
      <div class="ck">
        <div class="ck-dot" style="background:var(--blue-l);border:1px solid #A8D8EE;"></div>
        <div><h4>Blue</h4><p>Source country / informational</p></div>
      </div>
      <div class="ck">
        <div class="ck-dot" style="background:var(--purple-l);border:1px solid #C4C0F5;"></div>
        <div><h4>Purple</h4><p>Transit hub or trade bloc</p></div>
      </div>
      <div class="ck">
        <div class="ck-dot" style="background:#F1F3F6;border:1px solid #DDE2EB;"></div>
        <div><h4>Gray</h4><p>Neutral / not mentioned</p></div>
      </div>
    </div>

    <div class="section-head" style="margin-top:24px;">
      <h2>How this tool was built</h2>
    </div>
    <div class="guide-card">
      <div class="step">
        <div class="step-num">→</div>
        <div>
          <h3>Step 1: Scrape</h3>
          <p>
            <code>backend/scraper.py</code> downloads regulation documents from official
            government and UN sources (PDPC, ETDA, METI, DFAT, WTO, UNCTAD, and more).
            Each document is saved as a plain text file in the <code>data/</code> folder.
          </p>
        </div>
      </div>
      <div class="step">
        <div class="step-num">→</div>
        <div>
          <h3>Step 2: Extract with AI</h3>
          <p>
            <code>backend/extractor.py</code> sends each document to Claude AI with a
            structured prompt. Claude reads the legal text and returns a JSON profile —
            openness score, topic-by-topic breakdown, key laws, and notable features.
          </p>
        </div>
      </div>
      <div class="step">
        <div class="step-num">→</div>
        <div>
          <h3>Step 3: Store in database</h3>
          <p>
            <code>backend/database.py</code> loads the AI output into a local SQLite database.
            No cloud setup needed — the entire database lives in a single file.
          </p>
        </div>
      </div>
      <div class="step" style="border:none;">
        <div class="step-num">→</div>
        <div>
          <h3>Step 4: Serve the dashboard</h3>
          <p>
            <code>backend/server.py</code> runs a Flask server that serves this page and
            exposes a JSON API. The frontend (plain HTML, CSS, JS — no build tools) calls
            that API to render everything you see here.
          </p>
        </div>
      </div>
    </div>
  `;
}
