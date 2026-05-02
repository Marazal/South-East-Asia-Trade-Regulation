"""
backend/server.py

Flask web server. Serves the frontend (index.html, css, js) and exposes
a JSON API that the browser calls to get country data, topic comparisons,
and pipeline routes.

Run last:
    python backend/server.py
Then open: http://localhost:5000
"""

import sqlite3
import json
import os
import math
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app   = Flask(__name__, static_folder="../frontend")
CORS(app)  # allow browser requests from any origin during development

DB_FILE = os.path.join("data", "trade.db")
PORT    = int(os.environ.get("PORT", 5000))


# ── database helpers ──────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, params=()):
    conn = get_db()
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return rows


# ── static file serving ───────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory("../frontend/css", filename)


@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory("../frontend/js", filename)


# ── API: countries ────────────────────────────────────────

@app.route("/api/countries")
def api_countries():
    rows = query("SELECT * FROM countries ORDER BY openness_score DESC")
    for r in rows:
        r["notable_features"] = json.loads(r.get("notable_features") or "[]")
        r["key_laws"]         = json.loads(r.get("key_laws") or "[]")
    return jsonify(rows)


@app.route("/api/country/<name>")
def api_country(name):
    rows = query(
        "SELECT * FROM countries WHERE country LIKE ?",
        (f"%{name}%",)
    )
    if not rows:
        return jsonify({"error": "not found"}), 404

    country = rows[0]
    country["notable_features"] = json.loads(country.get("notable_features") or "[]")
    country["key_laws"]         = json.loads(country.get("key_laws") or "[]")

    topics = query(
        "SELECT topic, status, strictness, details FROM topic_scores WHERE country LIKE ?",
        (f"%{name}%",)
    )
    return jsonify({"country": country, "topics": topics})


# ── API: topics ───────────────────────────────────────────

@app.route("/api/topics")
def api_topics():
    rows = query("SELECT DISTINCT topic FROM topic_scores ORDER BY topic")
    return jsonify([r["topic"] for r in rows])


@app.route("/api/compare/<topic>")
def api_compare(topic):
    rows = query("""
        SELECT c.country, c.openness_score, ts.status, ts.strictness, ts.details
        FROM countries c
        LEFT JOIN topic_scores ts ON c.id = ts.country_id AND ts.topic = ?
        ORDER BY c.openness_score DESC
    """, (topic,))
    return jsonify(rows)


# ── API: pipeline finder ──────────────────────────────────

# Country profiles used for pipeline calculations.
# Loaded from the database at startup and supplemented with
# attributes (rcep, cptpp, asean) that aren't in the scraped docs.

COUNTRY_META = {
    "Singapore":       {"region":"ASEAN",     "tariff":0,  "rcep":True,  "cptpp":True,  "asean":True,  "esig":True,  "localize":False},
    "Malaysia":        {"region":"ASEAN",     "tariff":5,  "rcep":True,  "cptpp":False, "asean":True,  "esig":True,  "localize":False},
    "Thailand":        {"region":"ASEAN",     "tariff":10, "rcep":True,  "cptpp":False, "asean":True,  "esig":True,  "localize":False},
    "Vietnam":         {"region":"ASEAN",     "tariff":10, "rcep":True,  "cptpp":True,  "asean":True,  "esig":True,  "localize":True },
    "Indonesia":       {"region":"ASEAN",     "tariff":15, "rcep":True,  "cptpp":False, "asean":True,  "esig":True,  "localize":True },
    "Philippines":     {"region":"ASEAN",     "tariff":10, "rcep":True,  "cptpp":False, "asean":True,  "esig":True,  "localize":False},
    "Cambodia":        {"region":"ASEAN",     "tariff":15, "rcep":True,  "cptpp":False, "asean":True,  "esig":False, "localize":False},
    "Lao PDR":         {"region":"ASEAN",     "tariff":15, "rcep":True,  "cptpp":False, "asean":True,  "esig":False, "localize":False},
    "Brunei":          {"region":"ASEAN",     "tariff":0,  "rcep":True,  "cptpp":True,  "asean":True,  "esig":True,  "localize":False},
    "Myanmar":         {"region":"ASEAN",     "tariff":20, "rcep":False, "cptpp":False, "asean":True,  "esig":False, "localize":False},
    "Japan":           {"region":"East Asia", "tariff":0,  "rcep":True,  "cptpp":True,  "asean":False, "esig":True,  "localize":False},
    "South Korea":     {"region":"East Asia", "tariff":0,  "rcep":True,  "cptpp":False, "asean":False, "esig":True,  "localize":False},
    "China":           {"region":"East Asia", "tariff":25, "rcep":True,  "cptpp":False, "asean":False, "esig":True,  "localize":True },
    "Hong Kong":       {"region":"East Asia", "tariff":0,  "rcep":False, "cptpp":False, "asean":False, "esig":True,  "localize":False},
    "Taiwan":          {"region":"East Asia", "tariff":0,  "rcep":False, "cptpp":False, "asean":False, "esig":True,  "localize":False},
    "India":           {"region":"South Asia","tariff":20, "rcep":False, "cptpp":False, "asean":False, "esig":True,  "localize":True },
    "Bangladesh":      {"region":"South Asia","tariff":20, "rcep":False, "cptpp":False, "asean":False, "esig":False, "localize":False},
    "Sri Lanka":       {"region":"South Asia","tariff":15, "rcep":False, "cptpp":False, "asean":False, "esig":False, "localize":False},
    "Australia":       {"region":"Pacific",   "tariff":0,  "rcep":True,  "cptpp":True,  "asean":False, "esig":True,  "localize":False},
    "New Zealand":     {"region":"Pacific",   "tariff":0,  "rcep":False, "cptpp":True,  "asean":False, "esig":True,  "localize":False},
    "Papua New Guinea":{"region":"Pacific",   "tariff":15, "rcep":False, "cptpp":False, "asean":False, "esig":False, "localize":False},
}

HUBS = [
    {"name":"WTO Framework",   "boost":1.0,  "requires":None},
    {"name":"RCEP Zone",       "boost":0.9,  "requires":"rcep"},
    {"name":"CPTPP Zone",      "boost":0.85, "requires":"cptpp"},
    {"name":"ASEAN Framework", "boost":0.8,  "requires":"asean"},
    {"name":"Singapore",       "boost":0.6,  "requires":None},
]


def compat(s, d, s_score, d_score):
    """Score how compatible two countries are for digital trade (1-10)."""
    v = 10.0
    if s.get("localize"): v -= 2.5
    if d.get("localize"): v -= 2.5
    v -= min((s["tariff"] + d["tariff"]) / 10, 3)
    if not s.get("esig") or not d.get("esig"): v -= 1.5
    v -= abs(s_score - d_score) * 0.25
    if s["region"] == d["region"]: v += 1.0
    if s.get("rcep")  and d.get("rcep"):  v += 0.5
    if s.get("cptpp") and d.get("cptpp"): v += 0.5
    if s.get("asean") and d.get("asean"): v += 0.5
    return max(1.0, min(10.0, v))


def build_pipeline(src_name, dst_name, src_meta, dst_meta, src_score, dst_score):
    """Calculate all possible pipeline routes and return them sorted by efficiency."""
    routes = []

    # direct route
    c = compat(src_meta, dst_meta, src_score, dst_score)
    routes.append({
        "nodes":      [src_name, dst_name],
        "type":       "Direct bilateral",
        "efficiency": round(c * 10),
        "tariff":     round((src_meta["tariff"] + dst_meta["tariff"]) / 2),
        "data_risk":  "High" if (src_meta["localize"] or dst_meta["localize"]) else "Medium" if abs(src_score - dst_score) > 3 else "Low",
        "setup_weeks":max(4, round(12 - c)),
        "agreement":  "Bilateral",
        "pros":       _pros(src_meta, dst_meta, None, src_name, dst_name),
        "cons":       _cons(src_meta, dst_meta, None, src_name, dst_name),
    })

    # hub routes
    for hub in HUBS:
        req = hub["requires"]
        if req and not (src_meta.get(req) and dst_meta.get(req)):
            continue
        if hub["name"] in (src_name, dst_name):
            continue

        hub_meta  = COUNTRY_META.get(hub["name"], {"tariff":0,"region":"Global","rcep":False,"cptpp":False,"asean":False,"esig":True,"localize":False})
        hub_score = 7.5  # WTO/RCEP/CPTPP treated as high openness

        l1 = compat(src_meta, hub_meta, src_score, hub_score)
        l2 = compat(hub_meta, dst_meta, hub_score, dst_score)
        c  = (l1 + l2) / 2 + hub["boost"]

        routes.append({
            "nodes":      [src_name, hub["name"], dst_name],
            "type":       "Via regional bloc" if req else "Via digital hub",
            "efficiency": round(min(10, c) * 10),
            "tariff":     round((src_meta["tariff"] + dst_meta["tariff"]) / 3),
            "data_risk":  "Medium" if (src_meta["localize"] or dst_meta["localize"]) else "Low",
            "setup_weeks":max(6, round(14 - c)),
            "agreement":  hub["name"],
            "pros":       _pros(src_meta, dst_meta, hub, src_name, dst_name),
            "cons":       _cons(src_meta, dst_meta, hub, src_name, dst_name),
        })

    # deduplicate and sort
    seen, unique = set(), []
    for r in routes:
        k = "|".join(r["nodes"])
        if k not in seen:
            seen.add(k)
            unique.append(r)

    return sorted(unique, key=lambda x: x["efficiency"], reverse=True)


def _pros(s, d, hub, sn, dn):
    out = []
    if not s["localize"] and not d["localize"]: out.append("No data localization barriers")
    if s.get("esig") and d.get("esig"):          out.append("E-signatures mutually recognized")
    if s.get("rcep")  and d.get("rcep"):         out.append("RCEP trade agreement applies")
    if s.get("cptpp") and d.get("cptpp"):        out.append("CPTPP agreement applies")
    if s.get("asean") and d.get("asean"):        out.append("ASEAN Single Window available")
    if hub and "WTO" in hub["name"]:             out.append("WTO zero-tariff moratorium applies")
    if s["tariff"] == 0 and d["tariff"] == 0:    out.append("Zero digital tariffs both ways")
    if not out: out.append("Established diplomatic trade relations")
    return out[:3]


def _cons(s, d, hub, sn, dn):
    out = []
    if s["localize"]:               out.append(f"{sn} mandates data localization")
    if d["localize"]:               out.append(f"{dn} mandates data localization")
    if s["tariff"] > 15 or d["tariff"] > 15: out.append("High digital tariff barriers (>15%)")
    if not s.get("esig") or not d.get("esig"): out.append("E-signature recognition gap")
    if hub and hub["requires"] is None and hub["name"] != "WTO Framework":
        out.append(f"Extra compliance layer via {hub['name']}")
    if not out: out.append("Minor documentation requirements")
    return out[:3]


@app.route("/api/pipeline")
def api_pipeline():
    src_name = request.args.get("src", "")
    dst_name = request.args.get("dst", "")

    if not src_name or not dst_name:
        return jsonify({"error": "src and dst required"}), 400
    if src_name == dst_name:
        return jsonify({"error": "src and dst must be different"}), 400

    # get openness scores from database
    src_rows = query("SELECT openness_score FROM countries WHERE country LIKE ?", (f"%{src_name}%",))
    dst_rows = query("SELECT openness_score FROM countries WHERE country LIKE ?", (f"%{dst_name}%",))

    src_score = src_rows[0]["openness_score"] if src_rows else 5.0
    dst_score = dst_rows[0]["openness_score"] if dst_rows else 5.0

    src_meta = COUNTRY_META.get(src_name)
    dst_meta = COUNTRY_META.get(dst_name)

    if not src_meta or not dst_meta:
        return jsonify({"error": f"Unknown country: {src_name} or {dst_name}"}), 404

    routes = build_pipeline(src_name, dst_name, src_meta, dst_meta, src_score, dst_score)
    return jsonify({"routes": routes, "total": len(routes)})


# ── run ───────────────────────────────────────────────────

if __name__ == "__main__":
    # If no database exists yet (e.g. fresh Railway deploy),
    # auto-load the built-in sample data so the site works immediately.
    if not os.path.exists(DB_FILE):
        print("No database found — loading built-in sample data...")
        os.makedirs("data", exist_ok=True)
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from scripts.seed_samples import seed
        seed()

    print(f"\n Server running at http://localhost:{PORT}\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
