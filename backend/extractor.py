"""
backend/extractor.py

Reads every .txt file in data/, sends each one to Claude AI, and gets
back a structured JSON profile for that country. Saves results to
data/extracted.json which the database builder reads next.

Run after scraper.py:
    python backend/extractor.py
"""

import os
import json
import anthropic
from datetime import datetime


DATA_FOLDER = "data"
OUTPUT_FILE = os.path.join(DATA_FOLDER, "extracted.json")

# The 12 topics we want Claude to tag for every country.
# These match the ESCAP RDTII (Regional Digital Trade Integration Index) pillars.
TOPICS = [
    "Data Localization",
    "Cross-Border Data Flows",
    "E-Commerce Rules",
    "Digital Signatures",
    "Consumer Protection",
    "Customs & Tariffs",
    "Intellectual Property",
    "Cybersecurity Requirements",
    "Privacy & Data Protection",
    "Platform Regulations",
    "Financial Digital Services",
    "Trade Facilitation",
]


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_header(text):
    """Pull country/org from the file header written by scraper.py."""
    info = {}
    for line in text.split("\n")[:8]:
        if ":" in line:
            key, _, val = line.partition(":")
            info[key.strip()] = val.strip()
    return info


def build_prompt(text, country, org, topic):
    """
    The instruction we give Claude. Keeping it specific and structured
    is what makes the outputs consistent and parseable.
    """
    topics_str = "\n".join(f'    "{t}"' for t in TOPICS)

    return f"""You are a digital trade regulation analyst for UNESCAP.
Analyze the regulation document below and return a JSON profile.

Country: {country}
Organization: {org}
Topic area: {topic}

Document text (first 4000 chars):
{text[:4000]}

Return ONLY a JSON object — no explanation, no markdown, no extra text.
Use exactly this structure:

{{
  "country": "{country}",
  "organization": "{org}",
  "summary": "2-3 sentence plain-English summary of this country's digital trade stance",
  "openness_score": <integer 1-10, where 1=very restrictive, 10=very open>,
  "topics": {{
{topics_str.replace('"', '"')}
    (each topic should be an object like):
    "Data Localization": {{
      "status": "Not Required",
      "strictness": "Low",
      "details": "one sentence explanation"
    }}
  }},
  "key_laws": ["list", "of", "key", "laws", "mentioned"],
  "notable_features": ["2 or 3 most distinctive aspects"],
  "analyzed_at": "{datetime.now().isoformat()}"
}}

For status, use natural values like:
  Data Localization: "Required" / "Sector-specific" / "Not Required" / "Not Mentioned"
  Cross-Border Data Flows: "Open" / "Conditional" / "Restricted" / "Not Mentioned"
  E-Commerce Rules: "Comprehensive" / "Partial" / "Basic" / "None" / "Not Mentioned"
  Digital Signatures: "Legally Recognized" / "Partial" / "Not Recognized" / "Not Mentioned"
  Customs & Tariffs: "Zero" / "Low" / "Moderate" / "High" / "Not Mentioned"
  (use your judgment for the others — keep it short and consistent)

For strictness use: "Low" / "Medium" / "High" / "None"
"""


def call_claude(prompt):
    """Send prompt to Claude and get back the raw response text."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def clean_json(raw):
    """
    Claude sometimes wraps the JSON in ```json ... ``` fences.
    Strip those out before parsing.
    """
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def run():
    print("\n" + "=" * 55)
    print("  EXTRACTOR — AI analysis of scraped documents")
    print("=" * 55 + "\n")

    if not os.path.exists(DATA_FOLDER):
        print("data/ folder not found. Run scraper.py first.")
        return

    # find all txt files (skip the log file)
    files = [
        os.path.join(DATA_FOLDER, f)
        for f in sorted(os.listdir(DATA_FOLDER))
        if f.endswith(".txt")
    ]

    if not files:
        print("No .txt files found in data/. Run scraper.py first.")
        return

    print(f"Found {len(files)} documents to analyze\n")

    results = []
    errors  = []

    for i, path in enumerate(files, 1):
        fname = os.path.basename(path)
        print(f"[{i}/{len(files)}] {fname}")

        text   = read_file(path)
        header = get_header(text)

        country = header.get("COUNTRY", "Unknown")
        org     = header.get("ORGANIZATION", "Unknown")
        topic   = header.get("TOPIC", "Digital Trade")

        # skip files with no real content
        if len(text) < 250:
            print(f"      Skipping — too short (placeholder file)")
            continue

        try:
            print(f"      Sending to Claude...")
            prompt   = build_prompt(text, country, org, topic)
            raw      = call_claude(prompt)
            cleaned  = clean_json(raw)
            parsed   = json.loads(cleaned)
            results.append(parsed)
            print(f"      Done — openness score: {parsed.get('openness_score', '?')}/10")

        except json.JSONDecodeError as e:
            print(f"      JSON parse failed: {e}")
            errors.append({"file": path, "error": str(e)})

        except Exception as e:
            print(f"      Error: {e}")
            errors.append({"file": path, "error": str(e)})

        print()

    # save everything
    output = {
        "extracted_at": datetime.now().isoformat(),
        "total": len(results),
        "regulations": results,
        "errors": errors,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f" Done. {len(results)} extracted · {len(errors)} errors")
    print(f" Saved to {OUTPUT_FILE}")
    print(f" Next step: python backend/database.py\n")


if __name__ == "__main__":
    run()
