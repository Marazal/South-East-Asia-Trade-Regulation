"""
backend/database.py

Reads data/extracted.json and loads everything into a SQLite database.
SQLite is a file-based database — no server setup needed. The whole
database lives in data/trade.db.

Run after extractor.py:
    python backend/database.py
"""

import sqlite3
import json
import os
from datetime import datetime


EXTRACTED_FILE = os.path.join("data", "extracted.json")
DB_FILE        = os.path.join("data", "trade.db")


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def create_tables(conn):
    c = conn.cursor()

    # One row per country/organization document
    c.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            country          TEXT NOT NULL,
            organization     TEXT,
            summary          TEXT,
            openness_score   REAL,
            notable_features TEXT,
            key_laws         TEXT,
            analyzed_at      TEXT,
            UNIQUE(country, organization)
        )
    """)

    # One row per topic per country (12 topics × N countries)
    c.execute("""
        CREATE TABLE IF NOT EXISTS topic_scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
            country    TEXT,
            topic      TEXT,
            status     TEXT,
            strictness TEXT,
            details    TEXT
        )
    """)

    # One row per law mentioned in a country's document
    c.execute("""
        CREATE TABLE IF NOT EXISTS key_laws (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
            country    TEXT,
            law_name   TEXT
        )
    """)

    conn.commit()


def insert_country(conn, rec):
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO countries
            (country, organization, summary, openness_score, notable_features, key_laws, analyzed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        rec.get("country", "Unknown"),
        rec.get("organization", ""),
        rec.get("summary", ""),
        rec.get("openness_score", 5),
        json.dumps(rec.get("notable_features", [])),
        json.dumps(rec.get("key_laws", [])),
        rec.get("analyzed_at", datetime.now().isoformat()),
    ))
    conn.commit()
    return c.lastrowid


def insert_topics(conn, country_id, country, topics):
    c = conn.cursor()
    for topic_name, data in topics.items():
        c.execute("""
            INSERT INTO topic_scores (country_id, country, topic, status, strictness, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            country_id,
            country,
            topic_name,
            data.get("status", "Not Mentioned"),
            data.get("strictness", "None"),
            data.get("details", ""),
        ))
    conn.commit()


def insert_laws(conn, country_id, country, laws):
    c = conn.cursor()
    for law in laws:
        c.execute(
            "INSERT INTO key_laws (country_id, country, law_name) VALUES (?, ?, ?)",
            (country_id, country, law),
        )
    conn.commit()


def print_summary(conn):
    c = conn.cursor()
    c.execute("SELECT country, openness_score FROM countries ORDER BY openness_score DESC")
    rows = c.fetchall()
    print("\n  Openness rankings (10 = most open):")
    for i, row in enumerate(rows, 1):
        bar = "█" * int(row["openness_score"]) + "░" * (10 - int(row["openness_score"]))
        print(f"  {i:2}. {row['country']:<22} {bar}  {row['openness_score']}/10")


def run():
    print("\n" + "=" * 55)
    print("  DATABASE — Building from extracted data")
    print("=" * 55 + "\n")

    if not os.path.exists(EXTRACTED_FILE):
        print(f"data/extracted.json not found. Run extractor.py first.")
        return

    with open(EXTRACTED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("regulations", [])
    if not records:
        print("No records found in extracted.json.")
        return

    print(f"Loading {len(records)} records into {DB_FILE}...")

    conn = connect()
    create_tables(conn)

    loaded = 0
    for rec in records:
        country    = rec.get("country", "Unknown")
        country_id = insert_country(conn, rec)

        topics = rec.get("topics", {})
        if topics:
            insert_topics(conn, country_id, country, topics)

        laws = rec.get("key_laws", [])
        if laws:
            insert_laws(conn, country_id, country, laws)

        loaded += 1
        print(f"  + {country}")

    print_summary(conn)
    conn.close()

    print(f"\n  {loaded} countries stored in {DB_FILE}")
    print(f"  Next step: python backend/server.py\n")


if __name__ == "__main__":
    run()
