/**
 * export-clubs.mjs
 *
 * Reads Teams and Stadiums from football-vault.db and writes
 * src/data/clubs.json and src/data/stadiums.json.
 *
 * Usage:
 *   node scripts/export-clubs.mjs
 *
 * Or add to package.json scripts:
 *   "export-clubs": "node scripts/export-clubs.mjs"
 */

import Database from 'better-sqlite3';
import { writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Config ────────────────────────────────────────────────────────────────────
const DB_PATH    = 'C:\\repos\\football-vault\\football-vault.db';
const OUTPUT_DIR = resolve(__dirname, '..', 'src', 'data');
const CLUBS_PATH    = resolve(OUTPUT_DIR, 'clubs.json');
const STADIUMS_PATH = resolve(OUTPUT_DIR, 'stadiums.json');
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Build a coordinates object from separate latitude/longitude values.
 * Returns null if either value is missing or not a valid number.
 */
function buildCoordinates(lat, lng) {
    if (lat == null || lng == null) return null;
    const latitude  = parseFloat(lat);
    const longitude = parseFloat(lng);
    if (isNaN(latitude) || isNaN(longitude)) return null;
    return { latitude, longitude };
}

const db = new Database(DB_PATH, { readonly: true });

const rows = db.prepare(`
    SELECT
        t.id                  AS team_id,
        t.name                AS team_name,
        t.normalized_name     AS team_normalized_name,
        t.year_founded,
        t.colour1,
        t.colour2,
        t.colour3,
        tc.name               AS team_country,

        s.id                  AS stadium_id,
        s.name                AS stadium_name,
        s.city                AS stadium_city,
        s.latitude            AS stadium_latitude,
        s.longitude           AS stadium_longitude,
        s.capacity            AS stadium_capacity,
        sc.name               AS stadium_country
    FROM Teams t
    LEFT JOIN Countries tc ON t.country_id   = tc.id
    LEFT JOIN Stadiums  s  ON t.stadium_id   = s.id
    LEFT JOIN Countries sc ON s.country_id   = sc.id
    ORDER BY t.id
`).all();

db.close();

const clubs = rows.map((row) => {
    const colors = [row.colour1, row.colour2, row.colour3].filter(Boolean);
    const stadiumCoords = buildCoordinates(row.stadium_latitude, row.stadium_longitude);
    const clubCoordinates = stadiumCoords ?? null;

    return {
        id:             String(row.team_id),
        name:           row.team_name,
        normalizedName: row.team_normalized_name ?? row.team_name.toUpperCase(),
        country:        row.team_country ?? '',
        city:           row.stadium_city ?? '',
        ...(row.stadium_id != null && { stadiumId: String(row.stadium_id) }),
        ...(clubCoordinates && { coordinates: clubCoordinates }),
        ...(row.year_founded != null && { founded: row.year_founded }),
        colors,
    };
});

// ── Build stadiums, collecting clubs per stadium ──────────────────────────────
const stadiumMap = new Map();
for (const row of rows) {
    if (row.stadium_id == null) continue;
    const sid = String(row.stadium_id);
    if (!stadiumMap.has(sid)) {
        const coords = buildCoordinates(row.stadium_latitude, row.stadium_longitude);
        stadiumMap.set(sid, {
            id:      sid,
            name:    row.stadium_name,
            city:    row.stadium_city  ?? '',
            country: row.stadium_country ?? row.team_country ?? '',
            ...(coords && { coordinates: coords }),
            ...(row.stadium_capacity != null && { capacity: row.stadium_capacity }),
            clubs: [],
        });
    }
    stadiumMap.get(sid).clubs.push(String(row.team_id));
}
const stadiums = [...stadiumMap.values()];

// Warn about any clubs with no coordinates (they'll be missing from the map)
const missing = clubs.filter(c => !c.coordinates);
if (missing.length) {
    console.warn(`⚠️  ${missing.length} club(s) have no parseable coordinates and will be omitted from the map:`);
    missing.forEach(c => console.warn(`   - ${c.name} (id: ${c.id})`));
}

mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(CLUBS_PATH, JSON.stringify(clubs, null, 2), 'utf-8');
writeFileSync(STADIUMS_PATH, JSON.stringify(stadiums, null, 2), 'utf-8');
console.log(`✅  Exported ${clubs.length} clubs → ${CLUBS_PATH}`);
console.log(`✅  Exported ${stadiums.length} stadiums → ${STADIUMS_PATH}`);
