// frontend/js/glossary.js
// Renders the Glossary tab — plain-language definitions for every term
// used in this tool. No API calls, pure static content.

const TERMS = [
  {
    term: 'Openness score',
    def: 'A number from 1 to 10 that summarises how easy it is to do digital trade with a country. Calculated from 12 regulatory topics. Higher means fewer barriers and easier trade. Based on the ESCAP RDTII (Regional Digital Trade Integration Index) methodology.',
    ex: 'Singapore scores 8.5 — very open. China scores 3.5 — very restrictive due to localization rules and high tariffs.',
  },
  {
    term: 'Data localization',
    def: 'A rule that forces companies to store certain data (like customer records or financial transactions) on servers physically inside a country. This creates a major barrier for cloud services and cross-border digital trade because data cannot freely live on servers abroad.',
    ex: 'Indonesia requires certain strategic sector data to stay on Indonesian servers. India requires all payment transaction data to remain in India.',
  },
  {
    term: 'Cross-border data flows',
    def: 'The movement of data (information) from one country to another over the internet. When a company sends customer records to a cloud server in another country, that is a cross-border data flow. Restrictions on this — like localization rules or export approval requirements — are one of the biggest modern trade barriers.',
    ex: "The EU's GDPR restricts sending European personal data to countries without adequate data protection. Vietnam's Cybersecurity Law requires government approval for certain outbound transfers.",
  },
  {
    term: 'E-signatures / digital signatures',
    def: 'A digital version of a handwritten signature used to sign contracts and documents electronically. When legally recognized, businesses can close deals and sign trade agreements without ever printing a piece of paper. When not recognized, physical documents and wet-ink signatures are still required — which slows trade significantly.',
    ex: "Singapore's Electronic Transactions Act gives e-signatures the same legal effect as handwritten signatures. Papua New Guinea has no e-signature law, so physical documents are still required.",
  },
  {
    term: 'Digital tariffs',
    def: 'Taxes charged on digital products or services crossing a border — things like software downloads, streaming services, app purchases, or cloud computing. The WTO currently maintains a moratorium (a temporary pause) preventing countries from charging customs duties on electronic transmissions, but this is not permanent and India and South Africa have opposed it.',
    ex: 'Singapore, Japan, and Australia all apply zero tariffs on digital goods. China applies tariffs of around 25% on certain digital goods categories.',
  },
  {
    term: 'PDPA / GDPR (data protection law)',
    def: 'A law that sets rules for how companies collect, store, use, and share personal data. PDPA stands for Personal Data Protection Act — used in Singapore, Thailand, Malaysia, and others. GDPR is the EU version (General Data Protection Regulation) — widely seen as the global gold standard. Countries with strong data protection laws often find it easier to form mutual recognition agreements, which reduces trade friction.',
    ex: "Thailand's PDPA came into force in 2022, bringing it in line with Singapore and Japan. India's new DPDPA 2023 is stricter — it requires government approval for international data transfers.",
  },
  {
    term: 'Cybersecurity requirements',
    def: 'Rules that force businesses to implement security measures to protect digital systems and data. "Strong / mandatory" means there are detailed rules companies must follow, with penalties. "Medium" means guidelines exist but are not always mandatory. "Low" means minimal requirements.',
    ex: 'China and South Korea both have mandatory cybersecurity reporting obligations. Singapore requires critical information infrastructure operators to report incidents within hours.',
  },
  {
    term: 'RCEP — Regional Comprehensive Economic Partnership',
    def: 'A free trade agreement between 15 Asia-Pacific economies: all 10 ASEAN nations, plus China, Japan, South Korea, Australia, and New Zealand. It is the world\'s largest trade bloc by combined GDP and population. RCEP members benefit from reduced tariffs and simpler trade procedures with each other. The e-commerce chapter covers electronic authentication, consumer protection, and paperless trade.',
    ex: 'If both countries are RCEP members, tariffs on traded goods are lower and customs procedures are simplified. Thailand and Japan are both RCEP members — that helps their pipeline score.',
  },
  {
    term: 'CPTPP — Comprehensive and Progressive Agreement for Trans-Pacific Partnership',
    def: 'A high-ambition free trade agreement between 11 countries around the Pacific: Japan, Canada, Australia, New Zealand, Singapore, Vietnam, Malaysia, Mexico, Chile, Peru, and Brunei. CPTPP has strong digital trade rules — it explicitly bans data localization requirements between members and protects cross-border data flows. The UK joined in 2023.',
    ex: 'CPTPP members cannot impose data localization on each other — a major advantage. Vietnam and Australia are both CPTPP members, which significantly reduces their pipeline friction.',
  },
  {
    term: 'ASEAN Single Window',
    def: 'A digital platform connecting all 10 ASEAN member countries that allows traders to submit customs and trade documents electronically just once, and share them across borders automatically. It dramatically reduces the time and cost of customs clearance for goods traded within Southeast Asia.',
    ex: 'Thailand and Singapore both connect to the ASEAN Single Window. A Thai exporter can submit one set of documents that travels through the system to Singapore customs automatically.',
  },
  {
    term: 'Pipeline efficiency score',
    def: 'A percentage from 0 to 100 showing how smooth a particular trade route is expected to be. It is calculated from: whether either country has data localization, combined tariff levels, regulatory compatibility, e-signature recognition, shared trade agreements (RCEP, CPTPP, ASEAN), and the gap between the two countries\' openness scores.',
    ex: 'Singapore → Japan via RCEP scores ~90% — very smooth. India → Vietnam direct scores ~55% because both have localization rules and different regulatory frameworks.',
  },
  {
    term: 'Transit hub',
    def: 'A country or trade framework used as an intermediate step in a pipeline to reduce friction. Instead of trading directly between two countries with incompatible rules, routing through a hub that has good agreements with both sides can lower barriers and cost.',
    ex: 'Singapore is used as a hub because it has Digital Economy Agreements and trade relationships with almost every Asia-Pacific economy. WTO Framework is used as a hub because it provides the zero-tariff moratorium globally.',
  },
  {
    term: 'RDTII — Regional Digital Trade Integration Index',
    def: "ESCAP's official measurement framework for digital trade regulation across Asia-Pacific economies. It covers 12 policy pillars including tariffs, data flows, IP rights, cybersecurity, e-commerce rules, digital payments, and trade facilitation. Scores are derived from survey data, treaty text analysis, and regulatory assessments. This tool uses RDTII 2025 data.",
    ex: 'A country scoring high on RDTII has open, clear, and predictable digital trade regulations. Singapore consistently scores among the highest in the Asia-Pacific region.',
  },
  {
    term: 'LDC — Least Developed Country',
    def: 'A UN designation for countries with very low income, weak institutional capacity, and high economic vulnerability. LDCs receive special trade preferences from WTO members — including duty-free, quota-free market access for their exports. In the Asia-Pacific, this includes Bangladesh, Lao PDR, Myanmar, and Papua New Guinea.',
    ex: "Bangladesh's LDC status means its exports get duty-free access to many developed-country markets including Japan, Australia, and the EU — partially offsetting its limited digital trade framework.",
  },
  {
    term: 'DFFT — Data Free Flow with Trust',
    def: "An initiative launched by Japan at Davos in 2019. It aims to promote the free movement of data across borders while maintaining trust through appropriate rules on privacy, security, and intellectual property. Think of it as a middle path between total data openness and strict localization. Japan has been advancing DFFT through the G7, G20, and WTO's Osaka Track.",
    ex: 'Japan negotiated DFFT language into its Digital Partnership Agreements with the EU and UK. The concept has influenced how many Asia-Pacific countries think about balancing openness and data governance.',
  },
  {
    term: 'Trade facilitation',
    def: 'Measures that make the movement of goods and services across borders simpler, faster, and cheaper. In the digital context this includes: electronic customs filing, paperless trade documents, single window systems, and automated border procedures. The WTO Trade Facilitation Agreement (TFA) sets the global baseline.',
    ex: "Singapore and Japan have the most advanced paperless customs in Asia-Pacific. Bangladesh still relies heavily on manual processes, which increases the time and cost of trade even when tariffs are low.",
  },
];

function initGlossary() {
  const el = document.getElementById('glossary-content');
  if (!el) return;

  el.innerHTML = `
    <div class="section-head">
      <h2>Glossary — plain-language definitions</h2>
      <p>Every term used in this tool explained without jargon. Each entry includes a real-world example.</p>
    </div>
    <div class="gloss-card">
      ${TERMS.map(t => `
        <div class="g-item">
          <div class="g-term">${t.term}</div>
          <div class="g-def">${t.def}</div>
          <div class="g-ex">
            <span class="pill p-blue" style="font-size:10px;">Example</span>
            <span>${t.ex}</span>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}
