/**
 * export-clubs.mjs
 *
 * Reads Teams and Stadiums from football-vault.db and writes
 * src/data/clubs.json in the shape expected by the Keepsake app.
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
const OUTPUT_PATH = resolve(OUTPUT_DIR, 'clubs.json');
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Parse a coordinates value from the DB into { latitude, longitude }.
 * The DB stores coordinates as a JSON string: {"latitude": 54.5826, "longitude": -5.9553}
 */
function parseCoordinates(coordStr) {
    if (!coordStr) return null;
    try {
        const parsed = JSON.parse(coordStr);
        const latitude  = parseFloat(parsed.latitude);
        const longitude = parseFloat(parsed.longitude);
        if (isNaN(latitude) || isNaN(longitude)) return null;
        return { latitude, longitude };
    } catch {
        return null;
    }
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
        s.coordinates         AS stadium_coordinates,
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
    const stadiumCoords = parseCoordinates(row.stadium_coordinates);

    // Fall back to null coords rather than silently emit {0,0}
    const clubCoordinates = stadiumCoords ?? null;

    const stadium = row.stadium_id
        ? {
            id:          String(row.stadium_id),
            name:        row.stadium_name,
            city:        row.stadium_city  ?? '',
            country:     row.stadium_country ?? row.team_country ?? '',
            ...(stadiumCoords   && { coordinates: stadiumCoords }),
            ...(row.stadium_capacity != null && { capacity: row.stadium_capacity }),
            clubs: [String(row.team_id)],
          }
        : undefined;

    return {
        id:             String(row.team_id),
        name:           row.team_name,
        normalizedName: row.team_normalized_name ?? row.team_name.toUpperCase(),
        country:        row.team_country ?? '',
        city:           row.stadium_city ?? '',
        ...(stadium       && { stadium }),
        ...(clubCoordinates && { coordinates: clubCoordinates }),
        ...(row.year_founded != null && { founded: row.year_founded }),
        colors,
    };
});

// Populate shared-stadium clubs arrays (e.g. AC Milan & Inter at San Siro)
const stadiumClubs = new Map();
for (const club of clubs) {
    if (!club.stadium) continue;
    const sid = club.stadium.id;
    if (!stadiumClubs.has(sid)) stadiumClubs.set(sid, []);
    stadiumClubs.get(sid).push(club.id);
}
for (const club of clubs) {
    if (club.stadium && stadiumClubs.has(club.stadium.id)) {
        club.stadium.clubs = stadiumClubs.get(club.stadium.id);
    }
}

// Warn about any clubs with no coordinates (they'll be missing from the map)
const missing = clubs.filter(c => !c.coordinates);
if (missing.length) {
    console.warn(`⚠️  ${missing.length} club(s) have no parseable coordinates and will be omitted from the map:`);
    missing.forEach(c => console.warn(`   - ${c.name} (id: ${c.id})`));
}

mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(OUTPUT_PATH, JSON.stringify(clubs, null, 2), 'utf-8');
console.log(`✅  Exported ${clubs.length} clubs → ${OUTPUT_PATH}`);
