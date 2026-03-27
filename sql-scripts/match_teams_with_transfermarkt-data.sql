CREATE TABLE IF NOT EXISTS match_candidates (
    team_id                  INTEGER PRIMARY KEY,
    transfermarkt_club_id    INTEGER,
    transfermarkt_club_code  TEXT,
    domestic_competition_id  TEXT,
    stadium_name             TEXT,
    stadium_seats            INTEGER,
    match_tier               INTEGER,
    confidence               TEXT
);

-- TIER 0: transfermarkt_code already stored
INSERT OR IGNORE INTO match_candidates
SELECT t.id, c.club_id, c.club_code, c.domestic_competition_id, c.stadium_name, c.stadium_seats, 0, 'exact-code'
FROM teams t
JOIN TeamsTransfermarktDetails c ON t.transfermarkt_code = c.club_code
WHERE t.transfermarkt_code IS NOT NULL;

-- TIER 1a: normalized t.name = normalized c.name
INSERT OR IGNORE INTO match_candidates
SELECT t.id, c.club_id, c.club_code, c.domestic_competition_id, c.stadium_name, c.stadium_seats, 1, 'norm-name'
FROM vw_normalise_teams t
JOIN vw_normalise_transfermarkt_teams c ON t.norm_name = c.norm
WHERE t.id NOT IN (SELECT team_id FROM match_candidates);

-- TIER 1b: normalized t.full_name = normalized c.name
INSERT OR IGNORE INTO match_candidates
SELECT t.id, c.club_id, c.club_code, c.domestic_competition_id, c.stadium_name, c.stadium_seats, 2, 'norm-fullname'
FROM vw_normalise_teams t
JOIN vw_normalise_transfermarkt_teams c ON t.norm_full = c.norm
WHERE t.id NOT IN (SELECT team_id FROM match_candidates);

-- TIER 2: containment — c.norm contains t.norm_name (unique matches only)
INSERT OR IGNORE INTO match_candidates
SELECT team_id, transfermarkt_club_id, transfermarkt_club_code, domestic_competition_id, stadium_name, stadium_seats, 3, 'contains'
FROM (
    SELECT t.id AS team_id, c.club_id AS transfermarkt_club_id, c.club_code AS transfermarkt_club_code,
           c.domestic_competition_id, c.stadium_name, c.stadium_seats,
           count(*) OVER (PARTITION BY t.id) AS cnt
    FROM vw_normalise_teams t
    JOIN vw_normalise_transfermarkt_teams c ON c.norm LIKE '%' || t.norm_name || '%'
    WHERE t.id NOT IN (SELECT team_id FROM match_candidates)
      AND length(t.norm_name) >= 4
) sub
WHERE cnt = 1;

-- TIER 3: bbc_code matches transfermarkt club_code
insert or ignore into match_candidates
select
    t.id,
    tt.club_id,
    tt.club_code,
    tt.domestic_competition_id,
    tt.stadium_name,
    tt.stadium_seats,
    5,
    'bbc-code'
from Teams t
join TeamsTransfermarktDetails tt on t.bbc_code = tt.club_code
where t.id not in (select team_id from match_candidates)
  and t.transfermarkt_id is null;