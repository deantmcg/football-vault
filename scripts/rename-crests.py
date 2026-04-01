import os

# Path to crests directory
CRESTS_DIR = r"c:\repos\football-vault\crests"

# Paste your club data here as a multiline string
CLUB_DATA = '''team_id	bbc_code	country_code	team_name
team_id	bbc_code	country_code	team_name	file_name
1	crystal-palace	gb-eng	Crystal Palace	0
2	everton	gb-eng	Everton	0
3	sheffield-united	gb-eng	Sheffield United	0
4	manchester-united	gb-eng	Manchester United	0
5	aston-villa	gb-eng	Aston Villa	0
6	tottenham-hotspur	gb-eng	Tottenham Hotspur	0
7	wolverhampton-wanderers	gb-eng	Wolverhampton Wanderers	0
8	norwich-city	gb-eng	Norwich City	0
9	west-ham-united	gb-eng	West Ham United	0
10	manchester-city	gb-eng	Manchester City	0
11	arsenal	gb-eng	Arsenal	0
12	leicester-city	gb-eng	Leicester City	0
13	chelsea	gb-eng	Chelsea	0
16	liverpool	gb-eng	Liverpool	0
17	burnley	gb-eng	Burnley	0
18	afc-bournemouth	gb-eng	Bournemouth	0
19	newcastle-united	gb-eng	Newcastle United	0
20	brighton-and-hove-albion	gb-eng	Brighton & Hove Albion	0
21	watford	gb-eng	Watford	0
30	southampton	gb-eng	Southampton	0
32	valencia	es	Valencia	0
33	lille	fr	Lille	0
38	bayern-munich	de	Bayern Munich	0
42	napoli	it	Napoli	0
45	atletico-madrid	es	Atlético Madrid	0
50	atalanta	it	Atalanta	0
79	leipzig	de	RB Leipzig	0
98	leganes	es	Leganés	0
99	villarreal	es	Villarreal	0
100	real-valladolid	es	Valladolid	0
101	barcelona	es	Barcelona	0
102	mallorca	es	Mallorca	0
103	sevilla	es	Sevilla	0
104	espanyol	es	Espanyol	0
105		es	Eibar	
106	athletic-bilbao	es	Athletic Club	0
107	real-madrid	es	Real Madrid	0
114	paris-st-germain	fr	Paris Saint-Germain	0
125	eintracht-frankfurt	de	Eintracht Frankfurt	0
126	werder-bremen	de	Werder Bremen	0
127		de	Schalke 04	
128	bayer-leverkusen	de	Bayer Leverkusen	0
129	wolfsburg	de	Wolfsburg	0
130	freiburg	de	Freiburg	0
131		de	Hertha BSC	
132	koeln	de	Köln	0
133		de	Paderborn 07	
134	hoffenheim	de	Hoffenheim	0
135		de	Düsseldorf	
136	borussia-dortmund	de	Dortmund	0
137	augsburg	de	Augsburg	0
231	torino	it	Torino	0
248	deportivo-alaves	es	Alavés	0
249	levante	es	Levante	0
250	real-sociedad	es	Real Sociedad	0
251	osasuna	es	Osasuna	0
252		es	Granada	
253	getafe	es	Getafe	0
254	real-betis	es	Real Betis	0
257	lyon	fr	Lyon	0
266	fiorentina	it	Fiorentina	0
267		it	SPAL	
268	genoa	it	Genoa	0
269	inter-milan	it	Internazionale	0
270	juventus	it	Juventus	0
271	milan	it	Milan	0
272	udinese	it	Udinese	0
273		it	Brescia	
274	lazio	it	Lazio	0
275	sassuolo	it	Sassuolo	0
276	parma	it	Parma	0
277	cagliari	it	Cagliari	0
278	hellas-verona	it	Hellas Verona	0
279	lecce	it	Lecce	0
280	roma	it	Roma	0
281	bologna	it	Bologna	0
295	mainz	de	Mainz 05	0
303		it	Sampdoria	
333	celta-vigo	es	Celta Vigo	0
366	borussia-moenchengladbach	de	Mönchengladbach	0
474	union-berlin	de	Union Berlin	0
488	monaco	fr	Monaco	0
489	marseille	fr	Marseille	0
490	reims	fr	Reims	0
491	nice	fr	Nice	0
492	st-etienne	fr	Saint-Étienne	0
493		fr	Dijon	
494		fr	Bordeaux	
495	toulouse	fr	Toulouse	0
496	amiens	fr	Amiens	0
511	strasbourg	fr	Strasbourg	0
514	metz	fr	Metz	0
515	rennes	fr	Rennes	0
516	nantes	fr	Nantes	0
517	montpellier	fr	Montpellier	0
518	brest	fr	Brest	0
620	angers	fr	Angers	0
621	nimes	fr	Nîmes	0
622		gb-nir	Linfield	
623		gb-nir	Glentoran	
624	larne	gb-nir	Larne	0
625		gb-nir	Cliftonville	
626		gb-nir	Crusaders	
627		gb-nir	Coleraine	
628		gb-nir	Ballymena United	
629		gb-nir	Portadown	
630		gb-nir	Dundela	
631		gb-nir	Bangor	
632		no	Bodø/Glimt	
633		no	Molde	
634		no	Rosenborg	
635		no	Viking	
636		no	Brann	
637		fi	HJK Helsinki	
638		fi	KuPS	
639		is	Víkingur Reykjavík	
640		is	Valur	
641		is	KR Reykjavík	
642		ru	Zenit Saint Petersburg	
643		ru	Spartak Moscow	
644		ua	Shakhtar Donetsk	
645		ua	Dynamo Kyiv	
646		ro	FCSB	
647		ro	CFR Cluj	
648		bg	Ludogorets Razgrad	
649		bg	CSKA Sofia	
650		hu	Ferencváros	
651		hu	MOL Fehérvár	
652	olympiakos	gr	Olympiacos	0
653	panathinaikos	gr	Panathinaikos	0
654		gr	AEK Athens	
655	paok-thessaloniki	gr	PAOK	0
656		at	RB Salzburg	
657		at	Sturm Graz	
658		at	Rapid Wien	
659		ch	Young Boys	
660		ch	FC Basel	
661		ch	FC Zürich	
662	dinamo-zagreb	hr	Dinamo Zagreb	0
663		hr	Hajduk Split	
664		cz	Sparta Prague	
665		cz	Slavia Prague	
666		cz	Viktoria Plzeň	
667		sb	Red Star Belgrade	
668		sb	Partizan Belgrade	
670		gr	Aris Thessaloniki	
671		eg	Al Ahly	
672		eg	Zamalek	
673		ma	Wydad AC	
674		ma	Raja SC	
675		tn	Esperance de Tunis	
676		cd	TP Mazembe	
677		za	Mamelodi Sundowns	
678		dz	JS Kabylie	
679		gh	Hearts of Oak	
680		ng	Enyimba FC	
681		dz	USM Alger	
682		dz	MC Alger	
683		dz	ASO Chlef	
684		ao	Petro de Luanda	
685		ao	Primeiro de Agosto	
686		ci	ASEC Mimosas	
687		eg	Pyramids FC	
688		sd	Al-Hilal Omdurman	
689		sd	Al-Merreikh SC	
690		tz	Young Africans SC	
691		tz	Simba SC	
692		gh	Asante Kotoko	
693		ke	Gor Mahia	
694		mr	FC Nouadhibou	
695		zm	ZESCO United	
696		dz	CR Belouizdad	
697		zw	Dynamos FC	
698		dz	USM Khenchela	
699		dz	JS Saoura	
700		dz	ES Sétif	
701		dz	Paradou AC	
702		dz	CS Constantine	
703		ma	Mouloudia d'Oujda	
704		ma	Renaissance de Berkane	
705		ma	Fath Union Sport	
706		ma	ASFAR	
707		ma	Moghreb Tétouan	
708		ma	Difaâ Hassani El Jadidi	
709		tn	Monastir	
710		tn	CS Sfaxien	
711		tn	Club Africain	
712		eg	Al Masry SC	
713		eg	Al Ittihad Alexandria	
714		eg	Ismaily SC	
715		ng	Abia Warriors F.C.	
716		ng	Akwa United F.C.	
717		ng	Bayelsa United F.C.	
718		ng	Bendel Insurance	
719		ng	El-Kanemi Warriors F.C.	
720		ng	Enugu Rangers	
721		ng	Enyimba	
722		ng	Heartland F.C.	
723		ng	Ikorodu City	
724		ng	Kano Pillars F.C.	
725		ng	Katsina United	
726		ng	Kwara United	
727		ng	Lobi Stars F.C.	
728		ng	Nasarawa United F.C.	
729		ng	Niger Tornadoes	
730		ng	Plateau United	
731		ng	Remo Stars	
732		ng	Rivers United	
733		ng	Shooting Stars	
734		ng	Sunshine Stars F.C.	
735		gh	Accra Lions	
736		gh	Aduana FC	
737		gh	Basake Holy Stars	
738		gh	Bechem United FC	
739		gh	Berekum Chelsea F.C.	
740		gh	Dreams	
741		gh	Heart of Lions F.C.	
742		gh	Hearts of Oak SC	
743		gh	Karela United	
744		gh	Legon Cities FC	
745		gh	Medeama SC	
746		gh	Nations FC	
747		gh	Nsoatreman	
748		gh	Samartex	
749		gh	Vision FC	
750		gh	Young Apostles FC	
751		za	AmaZulu F.C.	
752		za	Chippa United	
753		za	Durban City	
754		za	Lamontville Golden Arrows	
755		za	Magesi	
756		za	Marumo Gallants	
757		za	Polokwane City	
758		za	Richards Bay	
759		za	Orbit College F.C.	
760		za	Sekhukhune United	
761		za	Siwelele	
762		za	Stellenbosch	
763		za	TS Galaxy F.C.	
764		tz	Azam F.C.	
765		tz	Coastal Union F.C.	
766		tz	Dodoma Jiji	
767		tz	JKT Tanzania	
768		tz	Kagera Sugar F.C.	
769		tz	KenGold	
770		tz	Kinondoni MC	
771		tz	Mashujaa	
772		tz	Namungo	
773		tz	Pamba Jiji	
774		tz	Prisons	
775		tz	Singida Black Stars	
776		tz	Singida Fountain Gate	
777		tz	Tabora United	
778		ke	AFC Leopards	
779		ke	APS Bomet	
780		ke	Bandari F.C.	
781		ke	Bidco United	
782		ke	Kakamega Homeboyz	
783		ke	Kariobangi Sharks	
784		ke	KCB	
785		ke	Kenya Police	
786		ke	Mara Sugar	
787		ke	Mathare United	
788		ke	Murang'a SEAL	
789		ke	Nairobi United	
790		ke	Posta Rangers	
791		ke	Shabana	
792		ke	Sofapaka F.C.	
793		ke	Tusker F.C.	
794		ke	Ulinzi Stars F.C.	
795		cm	Aigle Royal Menoua	
796		cm	Bamboutos	
797		cm	Canon Yaounde	
798		cm	Colombe Sportive	
799		cm	Coton Sport FC	
800		cm	Dynamo de Douala	
801		cm	Fauve Azur Elite	
802		cm	Fortuna	
803		cm	Gazelle	
804		cm	Les Astres FC	
805		cm	Panthere du Nde	
806		cm	PWD Bamenda	
807		cm	Stade Renard de Melong	
808		cm	US Douala	
809		cm	Victoria United	
810		cm	YOSA	
811	vfb-stuttgart	de	Stuttgart	0
812	benfica	pt	Benfica	0
813	fc-porto	pt	Porto	0
814	sporting-lisbon	pt	Sporting CP	0
815		pt	Braga	
816		pt	Vitória SC	
817	ajax	nl	Ajax	0
818		nl	PSV Eindhoven	
819	feyenoord	nl	Feyenoord	0
820	az-alkmaar	nl	AZ Alkmaar	0
821		nl	FC Utrecht	
822		be	Club Brugge	
823		be	Anderlecht	
824		be	Standard Liège	
825		be	KRC Genk	
826		be	KAA Gent	
827		be	Royal Antwerp	
828		us	LA Galaxy	
829		us	Seattle Sounders	
830		us	Inter Miami	
831	galatasaray	tr	Galatasaray	0
832	fenerbahce	tr	Fenerbahçe	0
833	besiktas	tr	Beşiktaş	0
834		tr	Trabzonspor	
835		ar	Boca Juniors	
836		ar	River Plate	
837		ar	Racing Club	
838		br	Flamengo	
839		br	Fluminense	
840		br	Palmeiras	
841		br	São Paulo	
842		mx	Club América	
843		mx	Chivas Guadalajara	
844		mx	Cruz Azul	
845		jp	Urawa Red Diamonds	
846		jp	Yokohama F. Marinos	
847		jp	Kawasaki Frontale	
848	celtic	gb-sct	Celtic	0
849	rangers	gb-sct	Rangers	0
850	aberdeen	gb-sct	Aberdeen	0
851		sa	Al Hilal	
852		sa	Al Nassr	
853		sa	Al Ittihad	
854		dk	FC Copenhagen	
855		dk	Brøndby	
856		se	Malmö FF	
857		se	AIK	
858		at	Red Bull Salzburg	
859		ch	Basel	
860		pl	Legia Warsaw	
861		pl	Lech Poznań	
862		ec	Barcelona SC	
863		ec	LDU Quito	
864		cy	APOEL	
865		cy	Omonia	
866		co	Millonarios	
867		co	Atlético Nacional	
868	cremonese	it	Cremonese	0
869		it	Palermo	
870		uy	Peñarol	
871		uy	Nacional	
872		il	Maccabi Tel Aviv	
873		il	Maccabi Haifa	
874		cl	Colo-Colo	
875		cl	Universidad de Chile	
876		cr	Saprissa	
877		cr	Alajuelense	
878		sk	Slovan Bratislava	
879		sk	Spartak Trnava	
880		si	Maribor	
881		si	Olimpija Ljubljana	
882		ir	Persepolis	
883		ir	Esteghlal	
884		bo	Bolívar	
885		bo	The Strongest	
886		ae	Al Ain	
887		ae	Al Wahda	
888		za	Kaizer Chiefs	
889		za	Orlando Pirates	
890		au	Sydney FC	
891		au	Melbourne Victory	
892		pe	Universitario	
893		pe	Alianza Lima	
894	vitoria-guimaraes	pt	Vitória Guimarães	0
895		pt	Rio Ave	
896		sb	Partizan	
897		ba	FK Sarajevo	
898		ba	Zrinjski Mostar	
899		pt	Vitória Setúbal	
900		pt	Boavista	
901		pt	Moreirense	
902		pt	Paços de Ferreira	
903		pt	Belenenses	
904		pt	Marítimo	
905		pt	Santa Clara	
906		pt	Arouca	
907		nl	FC Twente	
908		nl	Vitesse	
909		nl	SC Heerenveen	
910		nl	FC Groningen	
911		nl	Sparta Rotterdam	
912		nl	Go Ahead Eagles	
913		nl	PEC Zwolle	
914		be	Genk	
915		be	Cercle Brugge	
916		be	Union Saint-Gilloise	
917		be	KV Mechelen	
918		be	KV Kortrijk	
919		be	OH Leuven	
920		us	Atlanta United	
921		us	LAFC	
922		us	Portland Timbers	
923		us	Sporting Kansas City	
924		us	New York Red Bulls	
925		ca	Toronto FC	
926		ca	CF Montréal	
927		ca	Vancouver Whitecaps	
928		us	Austin FC	
929		us	FC Cincinnati	
930		us	Columbus Crew	
931		us	Nashville SC	
932		us	Charlotte FC	
933		tr	Başakşehir	
934		tr	Sivasspor	
935		tr	Antalyaspor	
936		tr	Konyaspor	
937		tr	Alanyaspor	
938		tr	Kasımpaşa	
939		tr	Gaziantep FK	
940		ar	Independiente	
941		ar	San Lorenzo	
942		ar	Vélez Sarsfield	
943		ar	Newell's Old Boys	
944		ar	Rosario Central	
945		ar	Estudiantes	
946		ar	Gimnasia La Plata	
947		ar	Lanús	
948		br	Corinthians	
949		br	Santos	
950		br	Grêmio	
951		br	Internacional	
952		br	Atlético Mineiro	
953		br	Cruzeiro	
954		br	Botafogo	
955		br	Vasco da Gama	
956		br	Athletico Paranaense	
957		br	Bahia	
958		br	Fortaleza	
959		mx	Tigres UANL	
960		mx	CF Monterrey	
961		mx	Club León	
962		mx	Pumas UNAM	
963		mx	Santos Laguna	
964		mx	CF Pachuca	
965		mx	Toluca	
966		mx	Atlas	
967		jp	Cerezo Osaka	
968		jp	Gamba Osaka	
969		jp	Kashima Antlers	
970		jp	FC Tokyo	
971		jp	Nagoya Grampus	
972		jp	Vissel Kobe	
973		jp	Sanfrecce Hiroshima	
974		jp	Consadole Sapporo	
975	heart-of-midlothian	gb-sct	Heart of Midlothian	0
976	hibernian	gb-sct	Hibernian	0
977	motherwell	gb-sct	Motherwell	0
978	dundee-united	gb-sct	Dundee United	0
979	kilmarnock	gb-sct	Kilmarnock	0
980	st-mirren	gb-sct	St Mirren	0
981		gb-sct	St Johnstone	
982		gb-sct	Ross County	
983		sa	Al Ahli	
984		sa	Al Ettifaq	
985		sa	Al Fayha	
986		sa	Al Shabab	
987		sa	Al Fateh	
988		sa	Al Taawoun	
989		sa	Abha	
990		sa	Damac FC	
991		hr	Rijeka	
992		hr	Osijek	
993		hr	Lokomotiva Zagreb	
994		hr	Istra 1961	
995		hr	Gorica	
996		hr	Varaždin	
997		pl	Wisła Kraków	
998		pl	Raków Częstochowa	
999		pl	Cracovia	
1000		pl	Pogoń Szczecin	
1001		pl	Jagiellonia Białystok	
1002		pl	Górnik Zabrze	
1003		pl	Śląsk Wrocław	
1004		pl	Zagłębie Lubin	
1005		dk	Midtjylland	
1006		dk	AGF	
1007		dk	Nordsjælland	
1008		dk	Silkeborg	
1009		dk	Randers	
1010		dk	Viborg	
1011		dk	Aalborg BK	
1012		dk	Odense BK	
1013		se	IFK Göteborg	
1014		se	Djurgårdens IF	
1015		se	IF Elfsborg	
1016		se	Hammarby IF	
1017		se	BK Häcken	
1018		se	IFK Norrköping	
1019		se	IK Sirius	
1020		se	Kalmar FF	
1021		at	Austria Wien	
1022		at	LASK	
1023		at	Wolfsberger AC	
1024		at	TSV Hartberg	
1025		at	WSG Tirol	
1026		at	Rheindorf Altach	
1027		at	SK Austria Klagenfurt	
1028		ch	Grasshopper Club Zürich	
1029		ch	Servette	
1030		ch	FC Lugano	
1031		ch	FC St. Gallen	
1032		ch	FC Sion	
1033		ch	FC Winterthur	
1034		ch	Yverdon-Sport	
1035		ie	Bohemians	
1036		ie	Derry City	
1037		ie	Drogheda United	
1038		ie	Dundalk	
1039		ie	Galway United	
1040		ie	St Patrick's Athletic	
1041	shamrock-rovers	ie	Shamrock Rovers	0
1042		ie	Shelbourne	
1043		ie	Sligo Rovers	
1044		ie	Waterford	
1045		ie	Athlone Town	
1046		ie	Bray Wanderers	
1047		ie	Cobh Ramblers	
1048		ie	Cork City	
1049		ie	Finn Harps	
1050		ie	Kerry	
1051		ie	Longford Town	
1052		ie	Treaty United	
1053		ie	UCD	
1054		ie	Wexford	
1055	sunderland	gb-eng	Sunderland	0
1056	fulham	gb-eng	Fulham	0
1057	ipswich-town	gb-eng	Ipswich Town	0
1058	brentford	gb-eng	Brentford	0
1059	reading	gb-eng	Reading	0
1060	nottingham-forest	gb-eng	Nottingham Forest	0
1061		de	VfL Bochum	
1062	fc-st-pauli	de	St. Pauli	0
1063		de	Kiel	
1064		it	FC Empoli	
1065		it	Venezia	
1066	afc-bournemouth	gb-eng	AFC Bournemouth	0
1067	leeds-united	gb-eng	Leeds United	0
1068	coventry-city	gb-eng	Coventry City	0
1069	middlesbrough	gb-eng	Middlesbrough	0
1070	millwall	gb-eng	Millwall	0
1071	hull-city	gb-eng	Hull City	0
1072	wrexham	gb-eng	Wrexham	0
1073	derby-county	gb-eng	Derby County	0
1074	bristol-city	gb-eng	Bristol City	0
1075	birmingham-city	gb-eng	Birmingham City	0
1076	preston-north-end	gb-eng	Preston North End	0
1077	swansea-city	gb-eng	Swansea City	0
1078	stoke-city	gb-eng	Stoke City	0
1079	queens-park-rangers	gb-eng	Queens Park Rangers	0
1080	charlton-athletic	gb-eng	Charlton Athletic	0
1081	portsmouth	gb-eng	Portsmouth	0
1082	blackburn-rovers	gb-eng	Blackburn Rovers	0
1083	west-bromwich-albion	gb-eng	West Bromwich Albion	0
1084	oxford-united	gb-eng	Oxford United	0
1085	sheffield-wednesday	gb-eng	Sheffield Wednesday	0
1086	lincoln-city	gb-eng	Lincoln City	0
1087	cardiff-city	gb-eng	Cardiff City	0
1088	bolton-wanderers	gb-eng	Bolton Wanderers	0
1089	bradford-city	gb-eng	Bradford City	0
1090	stockport-county	gb-eng	Stockport County	0
1091	huddersfield-town	gb-eng	Huddersfield Town	0
1092	stevenage	gb-eng	Stevenage	0
1093	wycombe-wanderers	gb-eng	Wycombe Wanderers	0
1094	plymouth-argyle	gb-eng	Plymouth Argyle	0
1095	luton-town	gb-eng	Luton Town	0
1096	barnsley	gb-eng	Barnsley	0
1097	peterborough-united	gb-eng	Peterborough United	0
1098	afc-wimbledon	gb-eng	AFC Wimbledon	0
1099	exeter-city	gb-eng	Exeter City	0
1100	mansfield-town	gb-eng	Mansfield Town	0
1101	burton-albion	gb-eng	Burton Albion	0
1102	doncaster-rovers	gb-eng	Doncaster Rovers	0
1103	wigan-athletic	gb-eng	Wigan Athletic	0
1104	blackpool	gb-eng	Blackpool	0
1105	leyton-orient	gb-eng	Leyton Orient	0
1106	rotherham-united	gb-eng	Rotherham United	0
1107	northampton-town	gb-eng	Northampton Town	0
1108	port-vale	gb-eng	Port Vale	0
1109	bromley	gb-eng	Bromley	0
1110	milton-keynes-dons	gb-eng	Milton Keynes Dons	0
1111	cambridge-united	gb-eng	Cambridge United	0
1112	notts-county	gb-eng	Notts County	0
1113	swindon-town	gb-eng	Swindon Town	0
1114	salford-city	gb-eng	Salford City	0
1115	grimsby-town	gb-eng	Grimsby Town	0
1116	chesterfield	gb-eng	Chesterfield	0
1117	crewe-alexandra	gb-eng	Crewe Alexandra	0
1118	barnet	gb-eng	Barnet	0
1119	walsall	gb-eng	Walsall	0
1120	colchester-united	gb-eng	Colchester United	0
1121	oldham-athletic	gb-eng	Oldham Athletic	0
1122	fleetwood-town	gb-eng	Fleetwood Town	0
1123	accrington-stanley	gb-eng	Accrington Stanley	0
1124	gillingham	gb-eng	Gillingham	0
1125	shrewsbury-town	gb-eng	Shrewsbury Town	0
1126	cheltenham-town	gb-eng	Cheltenham Town	0
1127	tranmere-rovers	gb-eng	Tranmere Rovers	0
1128	bristol-rovers	gb-eng	Bristol Rovers	0
1129	crawley-town	gb-eng	Crawley Town	0
1130	barrow	gb-eng	Barrow	0
1131	newport-county	gb-eng	Newport County	0
1132	harrogate-town	gb-eng	Harrogate Town	0
1133	rochdale	gb-eng	Rochdale	0
1134	carlisle-united	gb-eng	Carlisle United	0
1135	boreham-wood	gb-eng	Boreham Wood	0
1136	forest-green-rovers	gb-eng	Forest Green Rovers	0
1137	scunthorpe-united	gb-eng	Scunthorpe United	0
1138	halifax	gb-eng	Halifax Town	0
1139	southend-united	gb-eng	Southend United	0
1140	hartlepool-united	gb-eng	Hartlepool United	0
1141	tamworth	gb-eng	Tamworth	0
1142	boston-united	gb-eng	Boston United	0
1143	solihull-moors	gb-eng	Solihull Moors	0
1144	altrincham	gb-eng	Altrincham	0
1145	woking	gb-eng	Woking	0
1146	aldershot-town	gb-eng	Aldershot Town	0
1147	wealdstone	gb-eng	Wealdstone	0
1148	yeovil-town	gb-eng	Yeovil Town	0
1149	sutton-united	gb-eng	Sutton United	0
1150	eastleigh	gb-eng	Eastleigh	0
1151	brackley-town	gb-eng	Brackley Town	0
1152	morecambe	gb-eng	Morecambe	0
1153	braintree-town	gb-eng	Braintree Town	0
1154	gateshead	gb-eng	Gateshead	0
1155	truro-city	gb-eng	Truro City	0
1156	falkirk	gb-sct	Falkirk	0
1157	dundee	gb-sct	Dundee	0
1158	livingston	gb-sct	Livingston	0
1159	rayo-vallecano	es	Rayo Vallecano	0
1160	girona	es	Girona	0
1161	elche	es	Elche	0
1162	real-oviedo	es	Real Oviedo	0
1163	borussia-dortmund	de	Borussia Dortmund	0
1164	hamburg	de	Hamburger SV	0
1165	borussia-moenchengladbach	de	Borussia M'gladbach	0
1166	heidenheim	de	Heidenheim	0
1167	lens	fr	Lens	0
1168	lyon	fr	Olympique Lyonnais	0
1169	lorient	fr	Lorient	0
1170	angers	fr	Angers SCO	0
1171	paris-fc	fr	Paris FC	0
1172	le-havre	fr	Le Havre	0
1173	auxerre	fr	Auxerre	0
1174	inter-milan	it	Inter Milan	0
1175	milan	it	AC Milan	0
1176	como	it	Como	0
1177	pisa	it	Pisa	0
1178	psv-eindhoven	nl	PSV	0
1179		nl	NEC	
1180	twente	nl	Twente	0
1182		nl	Heerenveen	
1183		nl	Utrecht	
1184		nl	Groningen	
1185		nl	Fortuna Sittard	
1186		nl	Volendam	
1187		nl	Excelsior	
1188		nl	Telstar	
1189		nl	NAC Breda	
1190		nl	Heracles	
1191	sporting-braga	pt	Sporting Braga	0
1192		pt	Gil Vicente	
1193		pt	Famalicão	
1194		pt	Estoril	
1195		pt	Alverca	
1196		pt	Estrela	
1197		pt	Casa Pia	
1198		pt	Tondela	
1199		pt	AVS	
1200	istanbul-basaksehir	tr	İstanbul Başakşehir	0
1201		tr	Göztepe	
1202		tr	Kocaelispor	
1203		tr	Samsunspor	
1204		tr	Rizespor	
1205		tr	Gençlerbirliği	
1206		tr	Eyüpspor	
1207		tr	Kayserispor	
1208		tr	Fatih Karagümrük	
1209		gr	Levadiakos	
1210		gr	Aris	
1211		gr	OFI	
1212		gr	Atromitos	
1213		gr	Volos NFC	
1214		gr	Panaitolikos	
1215		gr	Kifisia	
1216		gr	Larissa	
1217		gr	Asteras Tripolis	
1218		gr	Panserraikos	
1219		gb-nir	Dungannon Swifts	
1220		gb-nir	Carrick Rangers	
1221		gb-nir	Glenavon	
1222	york-city	gb-eng	York City	0
1223		hr	Slaven Koprivnica	
1224		hr	HNK Gorica	
1225		hr	Vukovar	
1226		gb-sct	Peterhead	
1227		gb-nir	Ards	
1228		gb-sct	East Fife	
1229		gb-sct	Elgin City	
1230		gb-nir	Institute	
1231		gb-nir	Knockbreda	
1232		gb-sct	Clyde	
1233		gb-sct	Greenock Morton	
1234		gb-sct	Cowdenbeath	
1235		gb-sct	Albion Rovers	
1236		gb-nir	Dergview	
1237		gb-nir	Ballyclare Comrades	
1238		gb-sct	Dumbarton	
1239		gb-sct	Dunfermline	
1240		gb-eng	Hereford United	
1241		gb-nir	Ballinamallard United	
1242		gb-eng	Mansfield Town	
1243		gb-sct	Partick Thistle	
1244		gb-sct	Stirling Albion	
1245		gb-sct	Annan Athletic	
1246		gb-sct	Arbroath	
1247		gb-eng	Bury	
1248		gb-sct	Brechin City	
1249		gb-sct	Queen's Park	
1250		gb-nir	Loughgall	
1251		gb-sct	Montrose	
1252		gb-nir	Warrenpoint Town	
1253		gb-eng	Wolverhampton Wanderers	
1254		gb-eng	Macclesfield Town	
1255		gb-sct	Airdrie United	
1256		gb-sct	Hamilton Academical	
1257		gb-nir	Newry City	
1258		gb-sct	Stenhousemuir, East Stirlingshire	
1259		gb-sct	Queen of the South	
1260		gb-eng	Torquay United	
1261		gb-eng	AFC Wimbledon	
1262		gb-sct	Alloa Athletic	
1263		gb-sct	Berwick Rangers	
1264		gb-sct	Ayr United	
1265		gb-sct	Stranraer	
1266		gb-sct	Raith Rovers	
1267		gb-sct	Forfar Athletic	
1268		gb-nir	Annagh United	
1269		gb-sct	Inverness Caledonian Thistle	
1270		gb-eng	Swindon Town	
1271		gb-nir	Queens University	
1272		gb-eng	Stevenage Borough	
1273		gb-nir	H & W Welders	
1274		gb-eng	Dagenham and Redbridge	
'''  # Truncated for brevity; paste full data as needed

# Parse club data into a dict {(country_code, bbc_code): team_id}
club_map = {}
for line in CLUB_DATA.splitlines():
    if not line.strip() or line.startswith('team_id'):
        continue
    parts = line.split('\t')
    if len(parts) < 4:
        continue
    team_id, bbc_code, country_code, _ = parts[:4]
    if bbc_code and country_code:
        club_map[(country_code.strip(), bbc_code.strip())] = team_id.strip()

# Build reverse lookup: expected filename -> team_id
filename_to_id = {
    f"{country_code}-{bbc_code}.svg": team_id
    for (country_code, bbc_code), team_id in club_map.items()
}

# Iterate crest files and rename
for fname in os.listdir(CRESTS_DIR):
    if not fname.lower().endswith(".svg"):
        continue
    if fname in filename_to_id:
        team_id = filename_to_id[fname]
        src = os.path.join(CRESTS_DIR, fname)
        dst = os.path.join(CRESTS_DIR, f"{team_id}.svg")
        print(f"Renaming {fname} -> {team_id}.svg")
        os.rename(src, dst)
    else:
        print(f"No match for {fname}")
