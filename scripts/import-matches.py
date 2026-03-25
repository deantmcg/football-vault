"""
import-matches.py

Imports match JSON files from matches/<competition>/<season>/ into the Matches
table in football-vault.db.

Usage:
    python scripts/import-matches.py premier-league 2022-2023
    python scripts/import-matches.py championship 2023-2024
"""

import json
import logging
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "football-vault.db"
MATCHES_DIR = ROOT_DIR / "matches"

LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"import-matches-{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

# ── Logging ─────────────────────────────────────────────────────────────────
logger = logging.getLogger("import-matches")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)-8s  %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ── Caches ──────────────────────────────────────────────────────────────────
_competition_cache = {}   # name -> id
_team_cache = {}          # bbc_code -> id

# ── Counters ────────────────────────────────────────────────────────────────
stats = {
    "files_processed": 0,
    "files_skipped": 0,
    "matches_created": 0,
    "matches_existing": 0,
    "teams_created": 0,
}


def load_caches(conn):
    """Pre-load competitions and teams into lookup dicts."""
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM Competitions")
    for row in cur.fetchall():
        _competition_cache[row["name"]] = row["id"]

    cur.execute("SELECT id, bbc_code FROM Teams WHERE bbc_code IS NOT NULL")
    for row in cur.fetchall():
        _team_cache[row["bbc_code"]] = row["id"]


def resolve_competition(conn, name):
    """Get competition id by name. Logs a warning if not found."""
    if name in _competition_cache:
        return _competition_cache[name]
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM Competitions WHERE name = ? COLLATE NOCASE", (name,))
    row = cur.fetchone()
    if row:
        _competition_cache[row["name"]] = row["id"]
        _competition_cache[name] = row["id"]
        return row["id"]
    logger.warning("Competition not found: '%s'", name)
    return None


def resolve_team(conn, code, name):
    """Get team id by bbc_code. Creates a new team if not found."""
    if code in _team_cache:
        return _team_cache[code]

    cur = conn.cursor()
    cur.execute("SELECT id FROM Teams WHERE bbc_code = ?", (code,))
    row = cur.fetchone()
    if row:
        _team_cache[code] = row["id"]
        return row["id"]

    cur.execute(
        "INSERT INTO Teams (name, normalized_name, bbc_code) VALUES (?, ?, ?)",
        (name, name.upper(), code),
    )
    team_id = cur.lastrowid
    _team_cache[code] = team_id
    stats["teams_created"] += 1
    logger.info("CREATED team: '%s' (bbc_code=%s, id=%d)", name, code, team_id)
    return team_id


def parse_score(score_str):
    """Parse '3 - 0' into (3, 0). Returns (None, None) on failure."""
    if not score_str:
        return None, None
    m = re.match(r"(\d+)\s*-\s*(\d+)", score_str.strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def resolve_stadium_from_home_team(conn, home_team_id):
    """Resolve stadium_id from the home team's FK."""
    cur = conn.cursor()
    cur.execute("SELECT stadium_id FROM Teams WHERE id = ?", (home_team_id,))
    row = cur.fetchone()
    if row and row["stadium_id"]:
        return row["stadium_id"]
    return None


def find_or_create_match(conn, data, home_team_id, away_team_id, competition_id):
    """Find existing match by date + team ids, or create a new one."""
    cur = conn.cursor()
    match_date = data["matchDate"]

    cur.execute(
        """SELECT id FROM Matches
           WHERE match_date = ? AND home_team_id = ? AND away_team_id = ?""",
        (match_date, home_team_id, away_team_id),
    )
    row = cur.fetchone()
    if row:
        stats["matches_existing"] += 1
        logger.debug("Match already exists: id=%d (%s)", row["id"], match_date)
        return row["id"]

    home_score, away_score = parse_score(data.get("score"))
    stadium_id = resolve_stadium_from_home_team(conn, home_team_id)

    cur.execute(
        """INSERT INTO Matches
           (home_team_id, away_team_id, competition_id, match_date,
            home_score, away_score, stadium_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            home_team_id, away_team_id, competition_id, match_date,
            home_score, away_score, stadium_id,
        ),
    )
    match_id = cur.lastrowid
    stats["matches_created"] += 1
    logger.info(
        "CREATED match: id=%d  %s  %s vs %s  (%s)",
        match_id, match_date,
        data["homeTeam"]["name"], data["awayTeam"]["name"],
        data.get("competition", ""),
    )
    return match_id


def process_file(conn, filepath, competition_id):
    """Process a single match JSON file."""
    logger.debug("Processing: %s", filepath)

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    home = data["homeTeam"]
    away = data["awayTeam"]
    home_team_id = resolve_team(conn, home["code"], home["name"])
    away_team_id = resolve_team(conn, away["code"], away["name"])

    find_or_create_match(conn, data, home_team_id, away_team_id, competition_id)
    stats["files_processed"] += 1


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print("Usage: python scripts/import-matches.py <competition-code> <season>")
        print("  e.g. python scripts/import-matches.py premier-league 2022-2023")
        sys.exit(1)

    competition_code = args[0]
    season = args[1]
    season_dir = MATCHES_DIR / competition_code / season

    if not season_dir.is_dir():
        logger.error("Directory not found: %s", season_dir)
        sys.exit(1)

    files = sorted(season_dir.glob("*.json"))
    if not files:
        logger.info("No match files found in %s", season_dir)
        return

    logger.info("=" * 60)
    logger.info("Starting import: %s / %s  (%d file(s))", competition_code, season, len(files))
    logger.info("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    load_caches(conn)
    logger.info("Loaded %d competitions, %d teams into cache",
                len(_competition_cache), len(_team_cache))

    # Resolve competition from the code — look up by bbc_code first, then by name from the JSON
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM Competitions WHERE bbc_code = ?", (competition_code,))
    row = cur.fetchone()
    if row:
        competition_id = row["id"]
        _competition_cache[row["name"]] = row["id"]
        logger.info("Resolved competition: '%s' (id=%d) from code '%s'", row["name"], row["id"], competition_code)
    else:
        logger.error("Competition with bbc_code '%s' not found in DB", competition_code)
        conn.close()
        sys.exit(1)

    try:
        for filepath in files:
            try:
                process_file(conn, filepath, competition_id)
            except Exception:
                logger.exception("Error processing %s", filepath)
                stats["files_skipped"] += 1

        conn.commit()
        logger.info("=" * 60)
        logger.info("Import complete")
        logger.info("  Files processed:       %d", stats["files_processed"])
        logger.info("  Files skipped:         %d", stats["files_skipped"])
        logger.info("  Matches created:       %d", stats["matches_created"])
        logger.info("  Matches already exist: %d", stats["matches_existing"])
        logger.info("  Teams created:         %d", stats["teams_created"])
        logger.info("=" * 60)
    except Exception:
        conn.rollback()
        logger.exception("Fatal error — rolled back")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
