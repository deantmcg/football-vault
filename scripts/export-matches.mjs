/**
 * export-matches.mjs
 *
 * Reads Matches and LineupPlayers from football-vault.db and writes
 * src/data/matches.json with resolved names for teams, competition, stadium.
 *
 * Usage:
 *   node scripts/export-matches.mjs
 *
 * Or add to package.json scripts:
 *   "export-matches": "node scripts/export-matches.mjs"
 */

import Database from 'better-sqlite3';
import { writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Config ────────────────────────────────────────────────────────────────────
const DB_PATH     = 'C:\\repos\\football-vault\\football-vault.db';
const OUTPUT_DIR  = resolve(__dirname, '..', 'data');
const OUTPUT_PATH = resolve(OUTPUT_DIR, 'matches.json');
// ─────────────────────────────────────────────────────────────────────────────

const db = new Database(DB_PATH, { readonly: true });

// ── Fetch matches with resolved names ─────────────────────────────────────────
const matchRows = db.prepare(`
    SELECT
        m.id,
        m.match_date,
        m.home_score,
        m.away_score,
        m.home_formation,
        m.away_formation,
        m.status,
        m.bbc_url,
        m.bbc_id,
        m.fbref_id,

        m.home_team_id,
        ht.name             AS home_team_name,
        ht.bbc_code         AS home_team_code,

        m.away_team_id,
        at.name             AS away_team_name,
        at.bbc_code         AS away_team_code,

        m.competition_id,
        c.name              AS competition_name,

        m.stadium_id,
        s.name              AS stadium_name,
        s.city              AS stadium_city
    FROM Matches m
    LEFT JOIN Teams        ht ON m.home_team_id   = ht.id
    LEFT JOIN Teams        at ON m.away_team_id   = at.id
    LEFT JOIN Competitions c  ON m.competition_id = c.id
    LEFT JOIN Stadiums     s  ON m.stadium_id     = s.id
    ORDER BY m.match_date, m.id
`).all();

// ── Fetch all lineup players, grouped by match ───────────────────────────────
const lineupRows = db.prepare(`
    SELECT
        lp.match_id,
        lp.team_id,
        lp.player_name,
        lp.position,
        lp.number
    FROM LineupPlayers lp
    ORDER BY lp.match_id, lp.team_id, lp.number
`).all();

db.close();

// Group lineups by match_id → team_id
const lineupsByMatch = new Map();
for (const lp of lineupRows) {
    if (!lineupsByMatch.has(lp.match_id)) lineupsByMatch.set(lp.match_id, new Map());
    const teamMap = lineupsByMatch.get(lp.match_id);
    if (!teamMap.has(lp.team_id)) teamMap.set(lp.team_id, []);
    teamMap.get(lp.team_id).push({
        name:     lp.player_name,
        position: lp.position,
        ...(lp.number != null && { number: lp.number }),
    });
}

// ── Build output ──────────────────────────────────────────────────────────────
const matches = matchRows.map((row) => {
    const teamLineups = lineupsByMatch.get(row.id);

    const homeLineup = teamLineups?.get(row.home_team_id) ?? [];
    const awayLineup = teamLineups?.get(row.away_team_id) ?? [];

    return {
        id:          String(row.id),
        date:        row.match_date,
        competition: row.competition_name ?? '',
        stadium:     row.stadium_name ?? '',
        stadiumCity: row.stadium_city ?? '',
        homeTeam: {
            id:        String(row.home_team_id),
            name:      row.home_team_name ?? '',
            code:      row.home_team_code ?? '',
            score:     row.home_score,
            formation: row.home_formation ?? '',
            lineup:    homeLineup,
        },
        awayTeam: {
            id:        String(row.away_team_id),
            name:      row.away_team_name ?? '',
            code:      row.away_team_code ?? '',
            score:     row.away_score,
            formation: row.away_formation ?? '',
            lineup:    awayLineup,
        },
        ...(row.bbc_url   && { bbcUrl:  row.bbc_url }),
        ...(row.bbc_id    && { bbcId:   row.bbc_id }),
        ...(row.fbref_id  && { fbrefId: row.fbref_id }),
        ...(row.status    && { status:  row.status }),
    };
});

mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(OUTPUT_PATH, JSON.stringify(matches, null, 2), 'utf-8');
console.log(`✅  Exported ${matches.length} matches → ${OUTPUT_PATH}`);
