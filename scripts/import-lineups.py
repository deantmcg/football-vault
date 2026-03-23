"""
import-lineups.py

Imports lineup JSON files from lineups/ into the Matches and LineupPlayers
tables in football-vault.db.

Usage:
    python scripts/import-lineups.py                  # import all
    python scripts/import-lineups.py 2025-2026        # import one season
    python scripts/import-lineups.py --file lineups/2025-2026/20250913-arsenal-vs-nottingham-forest.json
"""

import json
import logging
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "football-vault.db"
LINEUPS_DIR = ROOT_DIR / "lineups"

LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"import-lineups-{datetime.now().strftime('%d%m%Y%H%M%S')}.log"

# ── Logging ─────────────────────────────────────────────────────────────────
logger = logging.getLogger("import-lineups")
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
_stadium_cache = {}       # name -> id

# ── Counters ────────────────────────────────────────────────────────────────
stats = {
    "files_processed": 0,
    "files_skipped": 0,
    "matches_created": 0,
    "matches_existing": 0,
    "lineup_players_created": 0,
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

    cur.execute("SELECT id, name FROM Stadiums")
    for row in cur.fetchall():
        _stadium_cache[row["name"]] = row["id"]


def resolve_competition(conn, name):
    """Get competition id by name. Logs a warning if not found."""
    if name in _competition_cache:
        return _competition_cache[name]
    # Try case-insensitive fallback
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
    """
    Get team id by bbc_code. Creates a new team if not found.
    """
    if code in _team_cache:
        return _team_cache[code]

    # Try DB lookup (maybe added since cache load)
    cur = conn.cursor()
    cur.execute("SELECT id FROM Teams WHERE bbc_code = ?", (code,))
    row = cur.fetchone()
    if row:
        _team_cache[code] = row["id"]
        return row["id"]

    # Create new team
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


def extract_bbc_id(url):
    """Extract the BBC live page id from the URL, e.g. 'ce9nz4kly4kt'."""
    if not url:
        return None
    m = re.search(r"/live/([a-z0-9]+)", url)
    return m.group(1) if m else None


def resolve_stadium(conn, stadium_name, home_team_id):
    """
    Resolve stadium_id: first try matching by name, then fall back to the
    home team's stadium_id FK.
    """
    if stadium_name and stadium_name in _stadium_cache:
        return _stadium_cache[stadium_name]

    # Try case-insensitive DB lookup
    if stadium_name:
        cur = conn.cursor()
        cur.execute("SELECT id FROM Stadiums WHERE name = ? COLLATE NOCASE", (stadium_name,))
        row = cur.fetchone()
        if row:
            _stadium_cache[stadium_name] = row["id"]
            return row["id"]
        logger.debug("Stadium not found by name: '%s', falling back to home team stadium", stadium_name)

    # Fallback: home team's stadium_id
    cur = conn.cursor()
    cur.execute("SELECT stadium_id FROM Teams WHERE id = ?", (home_team_id,))
    row = cur.fetchone()
    if row and row["stadium_id"]:
        logger.debug("Using home team stadium_id=%d for '%s'", row["stadium_id"], stadium_name or "(none)")
        return row["stadium_id"]

    logger.warning("No stadium resolved for '%s' (home_team_id=%d)", stadium_name or "(none)", home_team_id)
    return None


def find_or_create_match(conn, data, home_team_id, away_team_id, competition_id, stadium_id):
    """
    Find existing match by date + team ids, or create a new one.
    Returns match_id.
    """
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
    bbc_url = data.get("matchUrl")
    bbc_id = extract_bbc_id(bbc_url)
    # Strip the #Line-ups fragment from the URL
    if bbc_url and "#" in bbc_url:
        bbc_url = bbc_url.split("#")[0]

    home_formation = data.get("homeTeam", {}).get("formation")
    away_formation = data.get("awayTeam", {}).get("formation")

    cur.execute(
        """INSERT INTO Matches
           (home_team_id, away_team_id, competition_id, match_date,
            home_score, away_score, home_formation, away_formation,
            stadium_id, bbc_url, bbc_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            home_team_id, away_team_id, competition_id, match_date,
            home_score, away_score, home_formation, away_formation,
            stadium_id, bbc_url, bbc_id,
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


def insert_lineup(conn, match_id, team_id, players):
    """Insert lineup players for one side of a match."""
    cur = conn.cursor()

    # Check if lineup already exists for this match+team
    cur.execute(
        "SELECT COUNT(*) AS cnt FROM LineupPlayers WHERE match_id = ? AND team_id = ?",
        (match_id, team_id),
    )
    if cur.fetchone()["cnt"] > 0:
        logger.debug("Lineup already exists for match=%d team=%d, skipping", match_id, team_id)
        return

    for player in players:
        cur.execute(
            """INSERT INTO LineupPlayers (match_id, team_id, player_name, position, number)
               VALUES (?, ?, ?, ?, ?)""",
            (match_id, team_id, player["name"], player.get("position"), player.get("number")),
        )
        stats["lineup_players_created"] += 1


def process_file(conn, filepath):
    """Process a single lineup JSON file."""
    logger.debug("Processing: %s", filepath)

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    # Resolve competition
    comp_name = data.get("competition")
    competition_id = resolve_competition(conn, comp_name) if comp_name else None
    if not competition_id:
        logger.warning("Skipping %s — unknown competition '%s'", filepath.name, comp_name)
        stats["files_skipped"] += 1
        return

    # Resolve teams
    home = data["homeTeam"]
    away = data["awayTeam"]
    home_team_id = resolve_team(conn, home["code"], home["name"])
    away_team_id = resolve_team(conn, away["code"], away["name"])

    # Resolve stadium
    stadium_name = data.get("stadiumName")
    stadium_id = resolve_stadium(conn, stadium_name, home_team_id)

    # Find or create match
    match_id = find_or_create_match(conn, data, home_team_id, away_team_id, competition_id, stadium_id)

    # Insert lineups
    insert_lineup(conn, match_id, home_team_id, home["players"])
    insert_lineup(conn, match_id, away_team_id, away["players"])

    stats["files_processed"] += 1


def main():
    # Determine which files to process
    args = sys.argv[1:]

    if args and args[0] == "--file":
        files = [Path(a) for a in args[1:]]
    elif args:
        # Treat as season folder name(s)
        files = []
        for season in args:
            season_dir = LINEUPS_DIR / season
            if not season_dir.is_dir():
                logger.error("Season folder not found: %s", season_dir)
                continue
            files.extend(sorted(season_dir.glob("*.json")))
    else:
        # All seasons
        files = sorted(LINEUPS_DIR.rglob("*.json"))

    if not files:
        logger.info("No lineup files found.")
        return

    logger.info("=" * 60)
    logger.info("Starting import: %d file(s)", len(files))
    logger.info("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    load_caches(conn)
    logger.info("Loaded %d competitions, %d teams, %d stadiums into cache",
                 len(_competition_cache), len(_team_cache), len(_stadium_cache))

    try:
        for filepath in files:
            try:
                process_file(conn, filepath)
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
        logger.info("  Lineup players added:  %d", stats["lineup_players_created"])
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
