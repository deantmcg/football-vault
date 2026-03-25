update
	Stadiums
set
	country_id = (
		select t.country_id
		from Teams t
		where
			t.stadium_id = Stadiums.id
			and t.country_id is not null
		limit 1
	)
where
	country_id is null;