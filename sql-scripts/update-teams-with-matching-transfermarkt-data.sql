-- Insert stadiums for matched teams that don't have one yet
INSERT INTO Stadiums (name, capacity)
SELECT DISTINCT
    c.stadium_name,
    c.stadium_seats
FROM Teams t
LEFT JOIN temp_clubs c
    ON (
        t.name = c.name
        OR t.name = replace(replace(c.name, " FC", ""), " Football Club", "")
        OR replace(replace(t.name, " FC", ""), " Football Club", "") = replace(replace(c.name, " FC", ""), " Football Club", "")
        OR t.full_name = c.name
        OR t.full_name = replace(replace(c.name, " FC", ""), " Football Club", "")
        OR replace(replace(t.name, " FC", ""), " Football Club", "") = replace(replace(c.name, " FC", ""), " Football Club", "")
    )
LEFT JOIN Stadiums s ON t.stadium_id = s.id
WHERE c.club_id IS NOT NULL
  AND s.id IS NULL
  AND c.stadium_name IS NOT NULL;

-- Update Teams with transfermarkt data + newly created stadium_id
UPDATE Teams
SET 
    transfermarkt_id = c.club_id,
    transfermarkt_code = c.club_code,
    stadium_id = s.id
FROM temp_clubs c
JOIN Stadiums s ON s.name = c.stadium_name
WHERE 
    Teams.id IN (
        SELECT t.id
        FROM Teams t
        LEFT JOIN temp_clubs c
            ON (
                t.name = c.name
                OR t.name = replace(replace(c.name, " FC", ""), " Football Club", "")
                OR replace(replace(t.name, " FC", ""), " Football Club", "") = replace(replace(c.name, " FC", ""), " Football Club", "")
                OR t.full_name = c.name
                OR t.full_name = replace(replace(c.name, " FC", ""), " Football Club", "")
                OR replace(replace(t.name, " FC", ""), " Football Club", "") = replace(replace(c.name, " FC", ""), " Football Club", "")
            )
        LEFT JOIN Stadiums s ON t.stadium_id = s.id
        WHERE c.club_id IS NOT NULL
          AND s.id IS NULL
    )
    AND (
        Teams.name = c.name
        OR Teams.name = replace(replace(c.name, " FC", ""), " Football Club", "")
        OR replace(replace(Teams.name, " FC", ""), " Football Club", "") = replace(replace(c.name, " FC", ""), " Football Club", "")
        OR Teams.full_name = c.name
        OR Teams.full_name = replace(replace(c.name, " FC", ""), " Football Club", "")
        OR replace(replace(Teams.name, " FC", ""), " Football Club", "") = replace(replace(c.name, " FC", ""), " Football Club", "")
    );