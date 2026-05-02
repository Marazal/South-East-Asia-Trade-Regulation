"""
backend/scraper.py

Downloads digital trade regulation documents from official government
and international organization websites. Saves each one as a text file
in the data/ folder so the extractor can read them.

Run this first:
    python backend/scraper.py
"""

import os
import re
import json
import time
import requests
from datetime import datetime


DATA_FOLDER = "data"

# How long to wait between requests so we don't hammer servers
PAUSE_SECONDS = 2

# The sources we pull from. Add more here freely — the rest of the
# pipeline will pick them up automatically on the next run.
SOURCES = [
    {
        "country": "Singapore",
        "organization": "IMDA / PDPC",
        "topic": "Data Protection & Digital Trade",
        "url": "https://www.pdpc.gov.sg/overview-of-pdpa/the-legislation/personal-data-protection-act",
        "region": "ASEAN",
    },
    {
        "country": "Thailand",
        "organization": "ETDA",
        "topic": "Electronic Transactions & PDPA",
        "url": "https://www.etda.or.th/en",
        "region": "ASEAN",
    },
    {
        "country": "Malaysia",
        "organization": "MCMC",
        "topic": "Personal Data Protection & Digital Commerce",
        "url": "https://www.pdp.gov.my/jpdpv2/",
        "region": "ASEAN",
    },
    {
        "country": "Vietnam",
        "organization": "MOIT",
        "topic": "Cybersecurity & Data Localization",
        "url": "https://moit.gov.vn/en/",
        "region": "ASEAN",
    },
    {
        "country": "Indonesia",
        "organization": "Kominfo",
        "topic": "PDP Law & Data Governance",
        "url": "https://www.kominfo.go.id/",
        "region": "ASEAN",
    },
    {
        "country": "Philippines",
        "organization": "NPC",
        "topic": "Data Privacy Act",
        "url": "https://www.privacy.gov.ph/",
        "region": "ASEAN",
    },
    {
        "country": "Japan",
        "organization": "METI",
        "topic": "DFFT & Digital Trade Policy",
        "url": "https://www.meti.go.jp/english/policy/trade_policy/digital_trade/index.html",
        "region": "East Asia",
    },
    {
        "country": "South Korea",
        "organization": "MSIT",
        "topic": "PIPA & Digital Trade",
        "url": "https://www.msit.go.kr/eng/",
        "region": "East Asia",
    },
    {
        "country": "Australia",
        "organization": "DFAT",
        "topic": "Digital Trade Agreements",
        "url": "https://www.dfat.gov.au/trade/topics/digital-trade",
        "region": "Pacific",
    },
    {
        "country": "New Zealand",
        "organization": "MFAT",
        "topic": "Digital Trade & Privacy Act",
        "url": "https://www.mfat.govt.nz/en/trade/digital-trade/",
        "region": "Pacific",
    },
    {
        "country": "India",
        "organization": "MEITY",
        "topic": "DPDPA 2023 & Digital Policy",
        "url": "https://www.meity.gov.in/",
        "region": "South Asia",
    },
    {
        "country": "International",
        "organization": "WTO",
        "topic": "E-Commerce Work Programme",
        "url": "https://www.wto.org/english/tratop_e/ecom_e/ecom_e.htm",
        "region": "Global",
    },
    {
        "country": "International",
        "organization": "UNCTAD",
        "topic": "Digital Economy & Trade",
        "url": "https://unctad.org/topic/trade-analysis/trade-and-digital-economy",
        "region": "Global",
    },
]

# Fallback content for when websites block us or go down.
# Real enough to be useful for demos and development.
FALLBACK_TEXT = {
    "Singapore": """
Singapore Digital Trade Regulatory Framework

Personal Data Protection Act (PDPA):
Singapore's PDPA governs the collection, use, and disclosure of personal data.
Cross-border transfers are permitted provided organizations ensure comparable
protection through contractual means. There is no data localization requirement.

Electronic Transactions Act (ETA):
Electronic signatures and contracts carry full legal validity. Singapore uses
an approved framework for digital signatures that aligns with international
e-commerce standards. The ETA was last amended in 2021 to modernize provisions.

Customs and Digital Tariffs:
Singapore applies zero customs duties on all electronic transmissions in line
with its WTO commitments. This is reinforced in its bilateral Digital Economy
Agreements (DEAs) with Australia, UK, South Korea, and others.

ASEAN Digital Masterplan 2025:
Singapore leads implementation of cross-border paperless trade via the ASEAN
Single Window. All 10 ASEAN members are connected for electronic exchange of
trade documents, including certificates of origin and customs declarations.

Key agreements: DEPA (Digital Economy Partnership Agreement), DEAs with AU/UK/KR/US
""",
    "Thailand": """
Thailand Digital Economy Regulatory Framework

Personal Data Protection Act (PDPA) B.E. 2562 (2019):
Thailand's PDPA came into full force in June 2022 after a two-year delay.
It governs collection, use, and disclosure of personal data. Cross-border transfers
require consent or that the destination country meets adequate protection standards.
There is no blanket data localization requirement in the PDPA.

Electronic Transactions Act B.E. 2544 (2001):
Electronic signatures and contracts are legally valid. The Electronic Transactions
Development Agency (ETDA) oversees digital certification. A 2019 amendment
expanded recognition of e-signatures for most commercial transactions.

Computer Crimes Act B.E. 2550 (2007, amended 2017):
Governs unauthorized access and cybercrime. Platforms operating in Thailand
must comply with content removal requests and data access requirements.

Customs and Trade Facilitation:
Thailand participates in the ASEAN Single Window for electronic trade documents.
Digital goods are not subject to customs duties under Thailand's WTO commitments.
Average MFN tariff for ICT products is approximately 10%.

Financial Sector Data Rules:
Bank of Thailand requires financial institutions to maintain core transaction
data within Thailand. This represents a sector-specific localization rule.
""",
    "Japan": """
Japan Digital Trade Framework — DFFT Initiative

Act on the Protection of Personal Information (APPI):
Japan's main privacy law. Cross-border data transfers are permitted to countries
with equivalent protection or with contractual safeguards. Japan has an adequacy
arrangement with the European Union under GDPR. No data localization required.

Data Free Flow with Trust (DFFT):
Japan launched the DFFT initiative at Davos in 2019. It promotes free data flows
while maintaining trust through appropriate rules on privacy, security, and IP.
The Osaka Track advanced DFFT multilaterally through the G7 and G20.

CPTPP (Comprehensive and Progressive Agreement for Trans-Pacific Partnership):
Japan is a signatory. CPTPP prohibits data localization requirements and ensures
cross-border data flows for covered businesses. It also bans source code disclosure
requirements as a condition of market access.

RCEP (Regional Comprehensive Economic Partnership):
Japan is a member. RCEP includes e-commerce chapter provisions covering paperless
trading, electronic authentication, and consumer protection online.

Digital tariffs: Zero. Japan applies no customs duties on electronic transmissions.
Electronic signatures: Fully legally recognized under the Electronic Signatures Act.
""",
    "India": """
India Digital Trade and Data Governance Framework

Digital Personal Data Protection Act (DPDPA) 2023:
India's first comprehensive data protection law. Passed in August 2023. The Central
Government will notify permitted countries for cross-border data transfers — this
creates a government-controlled whitelist approach. Significant penalties apply.

Reserve Bank of India (RBI) Payment Data Localization:
All payment system data must be stored only within India. This rule has been in
place since 2018 and applies to all payment operators including Visa, Mastercard,
PayPal, and domestic players. Real-time data mirroring abroad is permitted but
the primary copy must remain in India.

Information Technology Act 2000 (amended 2008):
Provides the base legal framework for e-commerce, digital signatures, and
cybersecurity. Sensitive personal data rules under Section 43A require reasonable
security practices.

Foreign Direct Investment in E-Commerce:
100% FDI allowed under automatic route for B2B (marketplace) e-commerce.
Inventory-based e-commerce model not permitted for foreign-invested companies.
Entities with FDI cannot directly sell to consumers on their own platform if
they also carry inventory.

WTO E-Commerce Negotiations:
India has not joined the WTO Joint Statement Initiative (JSI) on e-commerce.
India opposes the permanent moratorium on customs duties on electronic transmissions.
""",
    "WTO": """
WTO Framework for Digital Trade and Electronic Commerce

Work Programme on Electronic Commerce (1998):
WTO members established this to examine trade-related issues arising from
e-commerce. It operates across the Council for Trade in Services, Council for
Trade in Goods, TRIPS Council, and Committee on Trade and Development.

Moratorium on Customs Duties on Electronic Transmissions:
In force since 1998. Members agree not to impose customs duties on electronic
transmissions. Renewed at every Ministerial Conference, most recently MC13 in 2024.
India and South Africa have consistently opposed making it permanent.

Joint Statement Initiative (JSI) on E-Commerce:
Launched at MC11 in 2017. Now includes 90+ WTO members. Covers:
- Electronic authentication and e-signatures
- Consumer protection for online transactions
- Unsolicited commercial electronic messages (spam rules)
- Open government data access
- Transparency in digital regulation
- Paperless trading and trade facilitation

Trade Facilitation Agreement (TFA):
In force since 2017. Article 10 requires members to accept electronic copies
of trade documents where possible. Connects to paperless customs systems.

TRIPS Agreement (Trade-Related IP Rights):
Applies to digital content, software, and databases. Members must provide
effective legal protection against circumvention of technological protection
measures. Copyright in digital works is covered.
""",
    "Australia": """
Australia Digital Trade Policy Framework

Privacy Act 1988 (updated 2022):
Australia's main privacy law covering personal information handling.
Cross-border transfers permitted if comparable protection exists at destination.
No mandatory data localization requirement. A major reform process is underway
following the 2022 review — amendments expected through 2025.

CPTPP and Digital Trade Agreements:
Australia is a CPTPP member and champion of open digital trade. CPTPP prohibits
data localization for most sectors and ensures cross-border data flows.
Australia has signed bilateral DEAs (Digital Economy Agreements) with Singapore
and is pursuing others in the Asia-Pacific region.

RCEP Membership:
Australia joined RCEP in 2022. The e-commerce chapter includes provisions on
electronic authentication, consumer protection, and paperless trading.

Customs and Tariffs:
Zero customs duties on electronic transmissions. Australia supports making the
WTO moratorium permanent. ICT goods receive preferential tariff treatment under
various FTAs.

Online Safety Act 2021:
Regulates online platforms operating in Australia. Creates a takedown regime
for harmful content. Applies to platforms globally if Australian users are served.

Electronic Transactions Act 1999:
Electronic signatures and contracts are fully legally recognized.
""",
}


def make_folder():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)


def fetch_page(url, timeout=12):
    """
    Try to download a URL. Returns HTML string or None.
    Using a browser-like User-Agent because some government sites
    return 403 for requests without one.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"      Could not fetch {url}: {e}")
        return None


def strip_html(html):
    """
    Pull readable text out of an HTML page.
    Strips scripts, styles, and tags — leaves the actual content.
    """
    # drop script/style blocks entirely
    html = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", "", html, flags=re.DOTALL)
    # strip remaining tags
    text = re.sub(r"<[^>]+>", " ", html)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) > 300 else None


def pick_fallback(country, organization):
    """
    If live scraping fails, use the built-in sample text.
    Tries country name first, then organization name.
    """
    for key in FALLBACK_TEXT:
        if key.lower() in country.lower() or key.lower() in organization.lower():
            return FALLBACK_TEXT[key]
    return None


def save_doc(country, organization, topic, url, text, source):
    filename = f"{country}_{organization}".replace(" ", "_").replace("/", "-").replace("(", "").replace(")", "")
    path = os.path.join(DATA_FOLDER, f"{filename}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"COUNTRY: {country}\n")
        f.write(f"ORGANIZATION: {organization}\n")
        f.write(f"TOPIC: {topic}\n")
        f.write(f"URL: {url}\n")
        f.write(f"SOURCE: {source}\n")
        f.write(f"DATE: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)
    return path


def run():
    print("\n" + "=" * 55)
    print("  SCRAPER — Collecting regulation documents")
    print("=" * 55 + "\n")

    make_folder()
    log = []

    for i, src in enumerate(SOURCES, 1):
        country = src["country"]
        org     = src["organization"]
        topic   = src["topic"]
        url     = src["url"]

        print(f"[{i}/{len(SOURCES)}] {country} — {org}")

        html = fetch_page(url)
        text = strip_html(html) if html else None
        source_type = "live"

        if not text:
            text = pick_fallback(country, org)
            source_type = "sample"
            if text:
                print(f"      Using built-in sample data")
            else:
                text = f"Placeholder for {org} — {topic}. Source: {url}"
                source_type = "placeholder"
                print(f"      Created placeholder")
        else:
            print(f"      Got {len(text):,} chars from live page")

        path = save_doc(country, org, topic, url, text, source_type)
        print(f"      Saved to {path}")

        log.append({"country": country, "org": org, "file": path, "source": source_type})

        if i < len(SOURCES):
            time.sleep(PAUSE_SECONDS)

    with open(os.path.join(DATA_FOLDER, "scrape_log.json"), "w") as f:
        json.dump(log, f, indent=2)

    live    = sum(1 for r in log if r["source"] == "live")
    sample  = sum(1 for r in log if r["source"] == "sample")
    print(f"\n Done. {live} live · {sample} sample · {len(log)} total files")
    print(f" Next step: python backend/extractor.py\n")


if __name__ == "__main__":
    run()
