-- select
-- 	coordinates,
--     '{"latitude":' || 
--     trim(substr(coordinates, 1, instr(coordinates, ',') - 1)) || 
--     ',"longitude":' || 
--     trim(substr(coordinates, instr(coordinates, ',') + 1)) || 
--     '}' as converted
-- from
-- 	Stadiums
-- where
-- 	coordinates not like '{%'

update Stadiums
set coordinates = 
    '{"latitude":' || 
    trim(substr(coordinates, 1, instr(coordinates, ',') - 1)) || 
    ',"longitude":' || 
    trim(substr(coordinates, instr(coordinates, ',') + 1)) || 
    '}'
where coordinates not like '{%'