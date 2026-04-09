update Teams
set
	wikidata_id = TeamsReep.key_wikidata,
	fbref_id = TeamsReep.key_fbref
from TeamsReep
where
	Teams.transfermarkt_id = TeamsReep.key_transfermarkt
	and TeamsReep.key_wikidata is not null
	and TeamsReep.key_fbref is not null