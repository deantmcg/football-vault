-- step 1: insert missing stadiums
insert into Stadiums (name, capacity)
select mc.stadium_name, mc.stadium_seats
from match_candidates mc
join Teams t on t.id = mc.team_id
left join Stadiums s on s.id = t.stadium_id
where s.id is null
  and mc.stadium_name is not null;

-- step 2: update Teams and Stadiums
update Teams
set
    transfermarkt_id   = mc.transfermarkt_club_id,
    transfermarkt_code = mc.transfermarkt_club_code,
    stadium_id         = coalesce(
                             t_existing.stadium_id,
                             (select s.id from Stadiums s
                              join match_candidates mc2 on s.name = mc2.stadium_name
                              where mc2.team_id = Teams.id)
                         )
from match_candidates mc
join Teams t_existing on t_existing.id = mc.team_id
where Teams.id = mc.team_id;

-- step 3: update capacity on existing stadiums
update Stadiums
set capacity = mc.stadium_seats
from match_candidates mc
join Teams t on t.id = mc.team_id
where Stadiums.id = t.stadium_id
  and mc.stadium_seats is not null;