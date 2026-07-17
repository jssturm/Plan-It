-- ================================================================
-- US TOP TOURISM STATES - DATA POPULATION
-- 9 States, their venues, attractions, events
-- ================================================================

-- ============================================================
-- STATES
-- ============================================================
INSERT OR IGNORE INTO states (code, name, tourism_summary, tourism_economy_share) VALUES
('NV', 'Nevada', 'Las Vegas conventions, casinos, shows; repeat leisure travel', 'Very High'),
('HI', 'Hawaii', 'Destination beaches, resorts, volcanoes; very high tourism share of economy', 'Very High'),
('CA', 'California', 'LA/SF/San Diego, Disneyland, beaches, national parks; massive international + domestic traffic', 'High'),
('NY', 'New York', 'NYC global attractions + upstate; huge city tourism and business travel', 'High'),
('TX', 'Texas', 'Large cities, events, history (Alamo), space center; big domestic travel hub', 'High'),
('AZ', 'Arizona', 'Grand Canyon, desert scenery, warm-weather outdoor tourism', 'High'),
('TN', 'Tennessee', 'Nashville music + Great Smoky Mountains National Park', 'Moderate-High'),
('LA', 'Louisiana', 'New Orleans festivals (Mardi Gras), cuisine, culture', 'Moderate-High'),
('CO', 'Colorado', 'Skiing, hiking, Rockies; year-round outdoor destination', 'High');

-- ============================================================
-- NEVADA
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='NV'), 'The Venetian Resort', 'resort_casino', 'Las Vegas', 'Las Vegas Strip', 'VICI Properties', 1999, 'Venice-themed mega-resort with canals, gondola rides, luxury shopping at Grand Canal Shoppes, and a 120,000 sq ft casino floor.', 'https://www.venetianlasvegas.com/', 1),
((SELECT id FROM states WHERE code='NV'), 'Bellagio', 'resort_casino', 'Las Vegas', 'Las Vegas Strip', 'MGM Resorts', 1998, 'Lake Como-inspired luxury resort famous for the Fountains of Bellagio water show, conservatory, and fine art gallery.', 'https://bellagio.mgmresorts.com/', 1),
((SELECT id FROM states WHERE code='NV'), 'Caesars Palace', 'resort_casino', 'Las Vegas', 'Las Vegas Strip', 'Caesars Entertainment', 1966, 'Roman Empire-themed luxury casino resort with the Colosseum theater, Forum Shops, and Garden of the Gods pool complex.', 'https://www.caesars.com/caesars-palace', 1),
((SELECT id FROM states WHERE code='NV'), 'MGM Grand', 'resort_casino', 'Las Vegas', 'Las Vegas Strip', 'MGM Resorts', 1993, 'The largest single hotel in the US with 6,852 rooms, MGM Grand Garden Arena for boxing and concerts, and a massive casino.', 'https://mgmgrand.mgmresorts.com/', 1),
((SELECT id FROM states WHERE code='NV'), 'Wynn Las Vegas', 'resort_casino', 'Las Vegas', 'Las Vegas Strip', 'Wynn Resorts', 2005, 'Ultra-luxury resort with the Lake of Dreams show, designer boutiques, award-winning restaurants, and an 18-hole golf course.', 'https://www.wynnlasvegas.com/', 1),
((SELECT id FROM states WHERE code='NV'), 'Fremont Street Experience', 'entertainment_district', 'Las Vegas', 'Downtown', 'City of Las Vegas', 1995, 'Five-block pedestrian mall in historic downtown with a 1,500-foot Viva Vision LED canopy, zip line, free concerts, and vintage casinos.', 'https://vegasexperience.com/', 1),
((SELECT id FROM states WHERE code='NV'), 'AREA15', 'entertainment_complex', 'Las Vegas', 'Off-Strip', 'Private', 2020, 'Immersive art and entertainment district featuring Meow Wolf''s Omega Mart, virtual reality experiences, axe throwing, and interactive art installations.', 'https://area15.com/', 1),
((SELECT id FROM states WHERE code='NV'), 'Red Rock Canyon National Conservation Area', 'nature_park', 'Las Vegas', 'Southern Nevada', 'BLM', 1990, 'Stunning red sandstone formations with a 13-mile scenic drive, 26 hiking trails, rock climbing, and desert wildlife viewing just 15 miles from the Strip.', 'https://www.blm.gov/programs/national-conservation-lands/nevada/red-rock-canyon', 1),
((SELECT id FROM states WHERE code='NV'), 'Hoover Dam', 'historic_site', 'Boulder City', 'Southern Nevada', 'US Bureau of Reclamation', 1936, 'Engineering marvel of the world straddling the Nevada-Arizona border, an Art Deco concrete arch-gravity dam on the Colorado River with power plant tours.', 'https://www.usbr.gov/lc/hooverdam/', 1),
((SELECT id FROM states WHERE code='NV'), 'Lake Tahoe Nevada State Park', 'nature_park', 'Incline Village', 'Lake Tahoe', 'Nevada State Parks', 1963, 'Crystal-clear alpine lake with Sand Harbor beaches, kayaking, paddleboarding, hiking trails with panoramic Sierra Nevada views, and winter sports.', 'http://parks.nv.gov/parks/lake-tahoe-nevada-state-park', 1),
((SELECT id FROM states WHERE code='NV'), 'The Neon Museum', 'museum', 'Las Vegas', 'Downtown', 'Non-profit', 1996, 'Outdoor exhibition space preserving iconic Las Vegas neon signs from defunct casinos and businesses in the Neon Boneyard.', 'https://www.neonmuseum.org/', 0),
((SELECT id FROM states WHERE code='NV'), 'Mob Museum', 'museum', 'Las Vegas', 'Downtown', 'Non-profit', 2012, 'National Museum of Organized Crime and Law Enforcement housed in a historic courthouse with interactive exhibits on the Mob''s history.', 'https://themobmuseum.org/', 0),
((SELECT id FROM states WHERE code='NV'), 'Valley of Fire State Park', 'nature_park', 'Overton', 'Southern Nevada', 'Nevada State Parks', 1935, 'Nevada''s oldest state park featuring 40,000 acres of bright red Aztec sandstone formations, ancient petroglyphs, and stunning desert landscapes.', 'http://parks.nv.gov/parks/valley-of-fire', 1);

-- Nevada Venue Land Areas (Fremont St, Bellagio, Venetian)
INSERT OR IGNORE INTO venue_land_areas (venue_id, name, description, theme, opening_year) VALUES
((SELECT id FROM venues WHERE name='The Venetian Resort'), 'Grand Canal Shoppes', 'Indoor shopping promenade with a quarter-mile Grand Canal, singing gondoliers, and cobblestone walkways under a painted sky ceiling.', 'Venice canals', 1999),
((SELECT id FROM venues WHERE name='Bellagio'), 'Bellagio Conservatory & Botanical Gardens', 'Seasonally transformed 14,000 sq ft indoor garden with elaborate floral sculptures, fountains, and themed holiday displays.', 'Botanical garden', 1998),
((SELECT id FROM venues WHERE name='Bellagio'), 'Fountains of Bellagio', 'Iconic free aquatic show with 1,200 water nozzles shooting 460 feet high, choreographed to music spanning classical to pop.', 'Water fountain show', 1998),
((SELECT id FROM venues WHERE name='Caesars Palace'), 'The Colosseum', '4,296-seat entertainment venue purpose-built for Celine Dion''s residency, now hosting world-class headliners.', 'Roman amphitheater', 2003),
((SELECT id FROM venues WHERE name='Fremont Street Experience'), 'SlotZilla Zipline', '1,750-foot zipline launching from a 12-story slot-machine-themed tower, flying Superman-style above the Fremont Street crowd.', 'Adrenaline/zipline', 2014);

-- Nevada Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='NV'), 'CES (Consumer Electronics Show)', 'convention', 'Las Vegas', 1, 'The world''s largest technology trade show with 4,500+ exhibitors and 180,000 attendees showcasing consumer tech innovations.', 180000, 1),
((SELECT id FROM states WHERE code='NV'), 'Electric Daisy Carnival (EDC) Las Vegas', 'music_festival', 'Las Vegas', 5, 'The largest electronic dance music festival in North America spanning 3 nights at the Las Vegas Motor Speedway with carnival rides and art installations.', 500000, 1),
((SELECT id FROM states WHERE code='NV'), 'National Finals Rodeo', 'sporting_event', 'Las Vegas', 12, 'The Super Bowl of professional rodeo held at the Thomas & Mack Center, attracting the top 120 contestants across 7 events.', 170000, 1),
((SELECT id FROM states WHERE code='NV'), 'Life is Beautiful Festival', 'music_arts_festival', 'Las Vegas', 9, 'Three-day music, art, and culinary festival transforming 18 blocks of downtown Las Vegas with major headliners and mural installations.', 170000, 0),
((SELECT id FROM states WHERE code='NV'), 'Las Vegas Grand Prix (F1)', 'sporting_event', 'Las Vegas', 11, 'Formula 1 night race on the Las Vegas Strip Circuit passing iconic landmarks at speeds over 200 MPH.', 315000, 1);

-- ============================================================
-- HAWAII
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='HI'), 'Hawaii Volcanoes National Park', 'national_park', 'Hawaii National Park', 'Big Island', 'National Park Service', 1916, 'UNESCO World Heritage site with two active volcanoes, Kilauea and Mauna Loa, lava tubes, steam vents, and 150 miles of hiking trails.', 'https://www.nps.gov/havo/', 1),
((SELECT id FROM states WHERE code='HI'), 'Waikiki Beach', 'beach', 'Honolulu', 'Oahu', 'City & County of Honolulu', NULL, 'Iconic 2-mile crescent of white sand backed by Diamond Head crater, luxury resorts, surfing schools, and the historic Moana Surfrider hotel.', 'https://www.gohawaii.com/islands/oahu/regions/honolulu/waikiki', 1),
((SELECT id FROM states WHERE code='HI'), 'Pearl Harbor National Memorial', 'historic_site', 'Pearl Harbor', 'Oahu', 'National Park Service', 1962, 'Commemorates the December 7, 1941 attack, featuring the USS Arizona Memorial, Battleship Missouri, USS Bowfin submarine, and Pearl Harbor Aviation Museum.', 'https://www.nps.gov/perl/', 1),
((SELECT id FROM states WHERE code='HI'), 'Haleakala National Park', 'national_park', 'Makawao', 'Maui', 'National Park Service', 1916, 'Preserves the massive Haleakala volcanic crater (7 miles across) with sunrise viewing at 10,023 feet, endemic silversword plants, and the Kipahulu coastal area with waterfalls.', 'https://www.nps.gov/hale/', 1),
((SELECT id FROM states WHERE code='HI'), 'Road to Hana', 'scenic_drive', 'Hana', 'Maui', 'State of Hawaii', NULL, 'Legendary 64-mile winding coastal drive with 620 curves, 59 bridges, waterfalls, black sand beaches, bamboo forests, and tropical fruit stands.', 'https://www.gohawaii.com/islands/maui/regions/east-maui/hana', 1),
((SELECT id FROM states WHERE code='HI'), 'Na Pali Coast State Wilderness Park', 'nature_park', 'Hanalei', 'Kauai', 'Hawaii State Parks', 1983, 'Jaw-dropping 17-mile coastline with emerald 4,000-foot sea cliffs, accessible only by boat, helicopter, or the grueling 11-mile Kalalau Trail.', 'https://dlnr.hawaii.gov/dsp/parks/kauai/napali-coast-state-wilderness-park/', 1),
((SELECT id FROM states WHERE code='HI'), 'Polynesian Cultural Center', 'cultural_center', 'Laie', 'Oahu', 'LDS Church', 1963, '42-acre living museum with six recreated Polynesian villages (Hawaii, Samoa, Tonga, Fiji, Tahiti, Aotearoa), luau, and evening show Ha: Breath of Life.', 'https://www.polynesia.com/', 1),
((SELECT id FROM states WHERE code='HI'), 'Waimea Canyon State Park', 'nature_park', 'Waimea', 'Kauai', 'Hawaii State Parks', 1952, 'The Grand Canyon of the Pacific, 14 miles long and 3,600 feet deep with vibrant red and green layers, scenic lookouts, and hiking trails.', 'https://dlnr.hawaii.gov/dsp/parks/kauai/waimea-canyon-state-park/', 1),
((SELECT id FROM states WHERE code='HI'), 'Kona Coffee Living History Farm', 'historic_site', 'Captain Cook', 'Big Island', 'Kona Historical Society', 2000, 'Working 5.5-acre coffee farm preserving the 1920s Japanese-American coffee farming heritage with costumed interpreters and fresh-roasted samples.', 'https://www.konahistorical.org/', 0),
((SELECT id FROM states WHERE code='HI'), 'Molokini Crater', 'nature_site', 'Offshore Maui', 'Maui', 'State of Hawaii', NULL, 'Partially submerged crescent-shaped volcanic crater forming a world-class snorkeling marine sanctuary with 250 fish species and 40-foot visibility.', 'https://dlnr.hawaii.gov/dar/mlcd/molokini-shoal/', 1),
((SELECT id FROM states WHERE code='HI'), 'Iolani Palace', 'historic_site', 'Honolulu', 'Oahu', 'State of Hawaii', 1882, 'The only royal palace on US soil, home to Hawaiian monarchs King Kalakaua and Queen Liliuokalani, with restored throne room and royal artifacts from the kingdom era.', 'https://www.iolanipalace.org/', 1),
((SELECT id FROM states WHERE code='HI'), 'Aulani, A Disney Resort & Spa', 'resort', 'Kapolei', 'Oahu', 'The Walt Disney Company', 2011, 'Disney''s Hawaiian resort with family pools, a lazy river, snorkel lagoon, character experiences, and Hawaiian cultural programming on a beachfront lagoon.', 'https://www.disneyaulani.com/', 0),
((SELECT id FROM states WHERE code='HI'), 'Diamond Head State Monument', 'nature_park', 'Honolulu', 'Oahu', 'Hawaii State Parks', 1962, 'Iconic 300,000-year-old tuff cone crater with a 0.8-mile trail to the summit for 360-degree views of Waikiki and the Pacific.', 'https://dlnr.hawaii.gov/dsp/parks/oahu/diamond-head-state-monument/', 1);

-- Hawaii Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='HI'), 'Merrie Monarch Festival', 'cultural_festival', 'Hilo', 4, 'The Olympics of hula, a week-long competition attracting the finest halau (hula schools) from across Hawaii and the mainland to honor King David Kalakaua.', 10000, 1),
((SELECT id FROM states WHERE code='HI'), 'Aloha Festivals', 'cultural_festival', 'Honolulu', 9, 'Hawaii''s largest cultural celebration with floral parades, hula performances, royal court investiture, and block parties across all islands spanning the entire month.', 100000, 1),
((SELECT id FROM states WHERE code='HI'), 'Honolulu Festival', 'cultural_festival', 'Honolulu', 3, 'Three-day celebration of Pacific Rim cultures with performances, crafts, and a grand parade through Waikiki ending with a Nagaoka fireworks display.', 50000, 0),
((SELECT id FROM states WHERE code='HI'), 'Vans Triple Crown of Surfing', 'sporting_event', 'North Shore/Oahu', 11, 'The Super Bowl of professional surfing held across three iconic North Shore breaks: Haleiwa, Sunset Beach, and the Banzai Pipeline.', 20000, 1),
((SELECT id FROM states WHERE code='HI'), 'Maui Film Festival', 'film_festival', 'Wailea', 6, 'Open-air cinema under the stars at the Wailea Golf Course with ocean-view screens, culinary arts, and celebrity honorees receiving the Silversword award.', 15000, 0);

-- ============================================================
-- CALIFORNIA
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='CA'), 'Disneyland Resort', 'theme_park', 'Anaheim', 'Southern California', 'The Walt Disney Company', 1955, 'The original Disney theme park with Disneyland Park, Disney California Adventure, Downtown Disney, and three resort hotels; the Happiest Place on Earth.', 'https://disneyland.disney.go.com/', 1),
((SELECT id FROM states WHERE code='CA'), 'Universal Studios Hollywood', 'theme_park', 'Universal City', 'Southern California', 'NBCUniversal', 1964, 'Working film studio and theme park with the world-famous Studio Tour, The Wizarding World of Harry Potter, and Super Nintendo World.', 'https://www.universalstudioshollywood.com/', 1),
((SELECT id FROM states WHERE code='CA'), 'Yosemite National Park', 'national_park', 'Yosemite National Park', 'Sierra Nevada', 'National Park Service', 1890, 'UNESCO World Heritage site with granite cliffs of El Capitan and Half Dome, giant sequoias, and 800 miles of trails in the Yosemite Valley.', 'https://www.nps.gov/yose/', 1),
((SELECT id FROM states WHERE code='CA'), 'Golden Gate Bridge', 'landmark', 'San Francisco', 'Bay Area', 'Golden Gate Bridge District', 1937, 'Iconic 1.7-mile suspension bridge painted in International Orange connecting San Francisco to Marin County, with a welcome center and pedestrian/bike lanes.', 'https://www.goldengate.org/', 1),
((SELECT id FROM states WHERE code='CA'), 'San Diego Zoo', 'zoo_aquarium', 'San Diego', 'Southern California', 'San Diego Zoo Wildlife Alliance', 1916, '100-acre zoo in Balboa Park with 12,000+ animals of 650 species, famous for open-air cageless exhibits, giant panda conservation, and the Skyfari aerial tram.', 'https://zoo.sandiegozoo.org/', 1),
((SELECT id FROM states WHERE code='CA'), 'Sequoia & Kings Canyon National Parks', 'national_park', 'Three Rivers', 'Sierra Nevada', 'National Park Service', 1890, 'Home to General Sherman, the world''s largest tree by volume (275 ft tall), and the deep Kings Canyon carved by glaciers with towering granite walls.', 'https://www.nps.gov/seki/', 1),
((SELECT id FROM states WHERE code='CA'), 'Santa Monica Pier', 'entertainment_complex', 'Santa Monica', 'Southern California', 'City of Santa Monica', 1909, 'Historic double-jointed pier with Pacific Park amusement park, a 1922 carousel, an aquarium, food vendors, and the official end of Route 66.', 'https://www.santamonicapier.org/', 1),
((SELECT id FROM states WHERE code='CA'), 'Napa Valley Wine Country', 'wine_region', 'Napa Valley', 'Bay Area/North Coast', 'Various', NULL, 'World-renowned wine region with 400+ wineries, the Napa Valley Wine Train, Michelin-starred restaurants, and hot air balloon rides over rolling vineyards.', 'https://www.visitnapavalley.com/', 1),
((SELECT id FROM states WHERE code='CA'), 'Joshua Tree National Park', 'national_park', 'Joshua Tree', 'Southern California Desert', 'National Park Service', 1994, 'Desert wilderness where the Mojave and Colorado deserts meet, known for twisted Joshua trees, massive boulder formations, stargazing, and rock climbing.', 'https://www.nps.gov/jotr/', 1),
((SELECT id FROM states WHERE code='CA'), 'Alcatraz Island', 'historic_site', 'San Francisco', 'Bay Area', 'National Park Service', 1934, 'The infamous former federal penitentiary on an island in San Francisco Bay, accessed by ferry, with an award-winning audio tour of cell blocks and escape stories.', 'https://www.nps.gov/alca/', 1),
((SELECT id FROM states WHERE code='CA'), 'Disney California Adventure', 'theme_park', 'Anaheim', 'Southern California', 'The Walt Disney Company', 2001, 'Sister park to Disneyland themed to California with Pixar Pier, Cars Land, Avengers Campus, and the nighttime spectacular World of Color.', 'https://disneyland.disney.go.com/destinations/disney-california-adventure/', 1),
((SELECT id FROM states WHERE code='CA'), 'Knott''s Berry Farm', 'theme_park', 'Buena Park', 'Southern California', 'Cedar Fair', 1940, 'America''s first theme park grown from a berry farm and chicken dinner restaurant, with Old West Ghost Town, world-class coasters, and Knott''s Scary Farm.', 'https://www.knotts.com/', 0);

-- California Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='CA'), 'Rose Parade & Rose Bowl', 'parade_sporting', 'Pasadena', 1, 'New Year''s Day tradition since 1890 with elaborate flower-covered floats, marching bands, and the Rose Bowl college football game.', 700000, 1),
((SELECT id FROM states WHERE code='CA'), 'Coachella Valley Music and Arts Festival', 'music_festival', 'Indio', 4, 'The most influential music festival in the US spanning two weekends with A-list headliners, large-scale art installations, and celebrity attendees.', 250000, 1),
((SELECT id FROM states WHERE code='CA'), 'San Diego Comic-Con International', 'convention', 'San Diego', 7, 'The largest pop culture convention in the world with 135,000 attendees, major film/TV announcements, cosplay, and an exhibit hall of epic proportions.', 135000, 1),
((SELECT id FROM states WHERE code='CA'), 'Outside Lands Music Festival', 'music_festival', 'San Francisco', 8, 'Three-day music, food, wine, and art festival in Golden Gate Park with 80+ acts across multiple stages and a focus on Bay Area culinary talent.', 225000, 0),
((SELECT id FROM states WHERE code='CA'), 'Monterey Jazz Festival', 'music_festival', 'Monterey', 9, 'The world''s longest continuously running jazz festival, held at the Monterey County Fairgrounds since 1958.', 40000, 1);

-- ============================================================
-- NEW YORK
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='NY'), 'Times Square', 'entertainment_district', 'New York', 'Manhattan/NYC', 'City of New York', NULL, 'The Crossroads of the World at Broadway and 7th Avenue with giant digital billboards, Broadway theaters, flagship stores, and the New Year''s Eve Ball Drop.', 'https://www.timessquarenyc.org/', 1),
((SELECT id FROM states WHERE code='NY'), 'Statue of Liberty & Ellis Island', 'national_monument', 'New York', 'Manhattan/NYC', 'National Park Service', 1886, 'Universal symbol of freedom with ferry access to Liberty Island and the Ellis Island Immigration Museum documenting 12 million immigrant stories.', 'https://www.nps.gov/stli/', 1),
((SELECT id FROM states WHERE code='NY'), 'Central Park', 'urban_park', 'New York', 'Manhattan/NYC', 'Central Park Conservancy', 1858, '843-acre masterpiece of landscape architecture with the Central Park Zoo, Bethesda Terrace, Strawberry Fields, boating lake, and 58 miles of paths.', 'https://www.centralparknyc.org/', 1),
((SELECT id FROM states WHERE code='NY'), 'Empire State Building', 'landmark_observatory', 'New York', 'Manhattan/NYC', 'Empire State Realty Trust', 1931, 'Art Deco 102-story skyscraper with open-air 86th-floor and enclosed 102nd-floor observatories offering 360-degree views 1,250 feet above NYC.', 'https://www.esbnyc.com/', 1),
((SELECT id FROM states WHERE code='NY'), 'The Metropolitan Museum of Art', 'museum', 'New York', 'Manhattan/NYC', 'Non-profit', 1870, 'The largest art museum in the Americas with 2 million works spanning 5,000 years, including the Temple of Dendur and the Costume Institute.', 'https://www.metmuseum.org/', 1),
((SELECT id FROM states WHERE code='NY'), 'Broadway Theater District', 'entertainment_district', 'New York', 'Manhattan/NYC', 'Various', NULL, '41 professional theaters near Times Square staging world-famous musicals and plays, from long-running hits like The Lion King to cutting-edge new productions.', 'https://www.broadway.org/', 1),
((SELECT id FROM states WHERE code='NY'), 'Niagara Falls State Park', 'nature_park', 'Niagara Falls', 'Upstate/Western NY', 'New York State Parks', 1885, 'America''s oldest state park featuring three thundering waterfalls (American Falls, Bridal Veil Falls, Horseshoe Falls) with the Maid of the Mist boat experience.', 'https://www.niagarafallsstatepark.com/', 1),
((SELECT id FROM states WHERE code='NY'), 'American Museum of Natural History', 'museum', 'New York', 'Manhattan/NYC', 'Non-profit', 1869, 'One of the world''s largest natural history museums with the Rose Center for Earth and Space, dinosaur halls, the 94-foot blue whale model, and 34 million specimens.', 'https://www.amnh.org/', 1),
((SELECT id FROM states WHERE code='NY'), 'Brooklyn Bridge', 'landmark', 'New York', 'Brooklyn/Manhattan', 'NYC DOT', 1883, 'Iconic 1.1-mile Gothic-style suspension bridge with a dedicated pedestrian walkway offering stunning skyline views of Lower Manhattan.', 'https://www1.nyc.gov/html/dot/html/infrastructure/brooklyn-bridge.shtml', 1),
((SELECT id FROM states WHERE code='NY'), 'Adirondack Park', 'nature_park', 'Lake Placid', 'Upstate/Adirondacks', 'NYS Adirondack Park Agency', 1892, 'The largest publicly protected area in the contiguous US at 6 million acres, larger than Yellowstone, with 46 High Peaks, 3,000 lakes, and Lake Placid Olympic sites.', 'https://www.visitadirondacks.com/', 1),
((SELECT id FROM states WHERE code='NY'), 'Museum of Modern Art (MoMA)', 'museum', 'New York', 'Manhattan/NYC', 'Non-profit', 1929, 'World''s foremost modern art museum with Van Gogh''s Starry Night, Warhol''s Campbell''s Soup Cans, Picasso''s Les Demoiselles d''Avignon, and a sculpture garden.', 'https://www.moma.org/', 0),
((SELECT id FROM states WHERE code='NY'), 'One World Observatory', 'landmark_observatory', 'New York', 'Manhattan/NYC', 'Legends Hospitality', 2015, 'Observatory atop One World Trade Center on floors 100-102 with the Sky Pod elevator experience and 360-degree views of NYC and beyond.', 'https://www.oneworldobservatory.com/', 1);

-- New York Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='NY'), 'Times Square New Year''s Eve Ball Drop', 'celebration', 'New York', 12, 'The world''s most famous New Year''s Eve celebration with the Waterford Crystal ball descending at midnight before an in-person crowd of 1 million.', 1000000, 1),
((SELECT id FROM states WHERE code='NY'), 'Macy''s Thanksgiving Day Parade', 'parade', 'New York', 11, 'Iconic holiday parade since 1924 with giant character balloons, elaborate floats, marching bands, and Santa Claus through Manhattan.', 3500000, 1),
((SELECT id FROM states WHERE code='NY'), 'Tribeca Film Festival', 'film_festival', 'New York', 6, 'Founded by Robert De Niro, a premier film festival showcasing independent films, immersive experiences, and Tribeca Talks with industry legends.', 150000, 1),
((SELECT id FROM states WHERE code='NY'), 'New York Fashion Week', 'fashion', 'New York', 2, 'Bi-annual event where top designers showcase collections to global buyers, media, and celebrities, setting fashion trends for the season.', 100000, 1),
((SELECT id FROM states WHERE code='NY'), 'US Open Tennis Championships', 'sporting_event', 'New York', 8, 'One of tennis''s four Grand Slam tournaments held at the USTA Billie Jean King National Tennis Center in Flushing Meadows, Queens.', 700000, 1);

-- ============================================================
-- TEXAS
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='TX'), 'The Alamo', 'historic_site', 'San Antonio', 'Central Texas', 'Texas General Land Office', 1724, 'The most visited historic landmark in Texas, site of the 1836 battle for Texas independence, with a museum, living history demonstrations, and beautiful gardens.', 'https://www.thealamo.org/', 1),
((SELECT id FROM states WHERE code='TX'), 'San Antonio River Walk', 'entertainment_district', 'San Antonio', 'Central Texas', 'City of San Antonio', 1941, '15-mile network of stone walkways along the San Antonio River one level below downtown, lined with restaurants, shops, hotels, and tour barges.', 'https://www.thesanantonioriverwalk.com/', 1),
((SELECT id FROM states WHERE code='TX'), 'Space Center Houston', 'museum', 'Houston', 'Gulf Coast', 'Non-profit', 1992, 'Official visitor center of NASA Johnson Space Center with the Apollo 17 command module, Independence shuttle replica, mission control tours, and astronaut encounters.', 'https://spacecenter.org/', 1),
((SELECT id FROM states WHERE code='TX'), 'Big Bend National Park', 'national_park', 'Big Bend National Park', 'West Texas', 'National Park Service', 1944, 'Remote 801,163-acre park along the Rio Grande with Chisos Mountains, Santa Elena Canyon, dark-sky stargazing, and the Chihuahuan Desert ecosystem.', 'https://www.nps.gov/bibe/', 1),
((SELECT id FROM states WHERE code='TX'), 'Six Flags Over Texas', 'theme_park', 'Arlington', 'DFW Metroplex', 'Six Flags', 1961, 'The original Six Flags park with 13 roller coasters, including the Titan hypercoaster and Texas Giant hybrid, plus Hurricane Harbor water park.', 'https://www.sixflags.com/overtexas', 0),
((SELECT id FROM states WHERE code='TX'), 'The Sixth Floor Museum at Dealey Plaza', 'museum', 'Dallas', 'DFW Metroplex', 'Non-profit', 1989, 'Museum in the former Texas School Book Depository examining the life, death, and legacy of President John F. Kennedy from the sniper''s perch.', 'https://www.jfk.org/', 1),
((SELECT id FROM states WHERE code='TX'), 'Padre Island National Seashore', 'beach_nature', 'Corpus Christi', 'Gulf Coast', 'National Park Service', 1962, 'Longest stretch of undeveloped barrier island in the world at 70 miles, known for sea turtle release programs, windsurfing, and pristine beaches.', 'https://www.nps.gov/pais/', 1),
((SELECT id FROM states WHERE code='TX'), 'State Fair of Texas', 'fairground', 'Dallas', 'DFW Metroplex', 'State Fair of Texas', 1886, '24-day annual fair at Fair Park featuring the 55-foot Big Tex icon, fried food innovations, the Texas Star Ferris wheel, auto show, and college football rivalry games.', 'https://bigtex.com/', 1),
((SELECT id FROM states WHERE code='TX'), 'Hamilton Pool Preserve', 'nature_park', 'Dripping Springs', 'Central Texas', 'Travis County', 1990, 'Natural collapsed grotto with a 50-foot waterfall into a jade-green pool, a stunning swimming hole surrounded by limestone and lush ferns (reservations required).', 'https://parks.traviscountytx.gov/parks/hamilton-pool-preserve', 0),
((SELECT id FROM states WHERE code='TX'), 'Fort Worth Stockyards', 'historic_district', 'Fort Worth', 'DFW Metroplex', 'Various', 1866, 'National Historic District honoring the cowboy heritage of the Chisholm Trail with the world''s only twice-daily cattle drive, rodeo, western shops, and honky-tonks.', 'https://www.fortworthstockyards.com/', 1),
((SELECT id FROM states WHERE code='TX'), 'Guadalupe Mountains National Park', 'national_park', 'Salt Flat', 'West Texas', 'National Park Service', 1972, 'Rugged wilderness with the four highest peaks in Texas, including Guadalupe Peak (8,751 ft), ancient Permian fossil reef, and stunning fall foliage in McKittrick Canyon.', 'https://www.nps.gov/gumo/', 0),
((SELECT id FROM states WHERE code='TX'), 'NASA Johnson Space Center', 'government_facility', 'Houston', 'Gulf Coast', 'NASA', 1963, 'Active spaceflight hub: Mission Control for ISS operations, astronaut training facility, and the home base of the US human spaceflight program.', 'https://www.nasa.gov/johnson/', 1);

-- Texas Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='TX'), 'South by Southwest (SXSW)', 'conference_festival', 'Austin', 3, 'Global convergence of film, interactive media, music, and culture with 400,000+ attendees across 10 days of keynotes, showcases, and networking throughout downtown Austin.', 400000, 1),
((SELECT id FROM states WHERE code='TX'), 'Austin City Limits Music Festival', 'music_festival', 'Austin', 10, 'Two-weekend mega music festival in Zilker Park with 130+ bands across 8 stages, an art market, and Austin food vendors, drawing from the legacy of the ACL TV show.', 450000, 1),
((SELECT id FROM states WHERE code='TX'), 'Houston Livestock Show and Rodeo', 'rodeo_sporting', 'Houston', 3, 'The world''s largest livestock show and rodeo spanning 3 weeks at NRG Stadium with nightly A-list concerts, carnival, and championship rodeo competitions.', 2500000, 1),
((SELECT id FROM states WHERE code='TX'), 'Fiesta San Antonio', 'cultural_festival', 'San Antonio', 4, '10-day citywide celebration commemorating the Alamo and San Jacinto with 100+ events including parades, the River Parade, and Oyster Bake.', 3500000, 1),
((SELECT id FROM states WHERE code='TX'), 'Dallas International Film Festival', 'film_festival', 'Dallas', 4, 'Week-long festival celebrating independent filmmaking with premieres, retrospectives, and Q&As.', 40000, 0);

-- ============================================================
-- ARIZONA
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='AZ'), 'Grand Canyon National Park - South Rim', 'national_park', 'Grand Canyon Village', 'Northern Arizona', 'National Park Service', 1919, 'One of the Seven Natural Wonders of the World, a mile-deep gorge carved by the Colorado River with Mather Point, Desert View Watchtower, and Bright Angel Trail.', 'https://www.nps.gov/grca/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Sedona Red Rock Country', 'nature_region', 'Sedona', 'Northern Arizona', 'US Forest Service', NULL, 'Stunning red sandstone formations with vortex energy sites, Cathedral Rock, Chapel of the Holy Cross, and 200+ miles of hiking/biking trails in Oak Creek Canyon.', 'https://visitsedona.com/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Monument Valley Navajo Tribal Park', 'nature_park', 'Oljato-Monument Valley', 'Northern Arizona', 'Navajo Nation', 1958, 'Iconic sandstone buttes rising 400-1,000 feet from the desert floor, famous from countless Western films, with a 17-mile scenic drive through the Mittens and Merrick Butte.', 'https://navajonationparks.org/tribal-parks/monument-valley/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Antelope Canyon', 'nature_site', 'Page', 'Northern Arizona', 'Navajo Nation', 1997, 'Slot canyon famous for its wave-like sandstone walls and light beams piercing the narrow passages; accessible only by guided tour with Navajo operators.', 'https://navajonationparks.org/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Horseshoe Bend', 'nature_site', 'Page', 'Northern Arizona', 'City of Page', NULL, 'Dramatic 270-degree horseshoe-shaped meander of the Colorado River 1,000 feet below a sheer cliff overlook, accessible by a 1.5-mile roundtrip trail.', 'https://www.visitpageaz.com/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Saguaro National Park', 'national_park', 'Tucson', 'Southern Arizona', 'National Park Service', 1994, 'Preserves the giant saguaro cactus forests of the Sonoran Desert split into two districts (East and West) with scenic drives, hiking, and spectacular sunsets.', 'https://www.nps.gov/sagu/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Desert Botanical Garden', 'garden', 'Phoenix', 'Greater Phoenix', 'Non-profit', 1939, '140-acre garden in Papago Park with 50,000+ desert plants, seasonal butterfly exhibit, and Las Noches de las Luminarias holiday event.', 'https://www.dbg.org/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Meteor Crater Natural Landmark', 'nature_site', 'Winslow', 'Northern Arizona', 'Private', 1903, 'Best-preserved meteorite impact site on Earth at 550 feet deep and 1 mile across, formed 50,000 years ago with an interactive discovery center.', 'https://www.meteorcrater.com/', 0),
((SELECT id FROM states WHERE code='AZ'), 'Petrified Forest National Park', 'national_park', 'Petrified Forest', 'Northern Arizona', 'National Park Service', 1962, 'Triassic-period fossilized trees turned to colorful quartz crystal, plus the Painted Desert badlands, ancient petroglyphs, and Route 66 history.', 'https://www.nps.gov/pefo/', 1),
((SELECT id FROM states WHERE code='AZ'), 'Taliesin West', 'historic_site', 'Scottsdale', 'Greater Phoenix', 'Frank Lloyd Wright Foundation', 1937, 'Frank Lloyd Wright''s winter home and architectural school in the Sonoran Desert, a UNESCO World Heritage site offering guided tours of the campus.', 'https://franklloydwright.org/taliesin-west/', 0),
((SELECT id FROM states WHERE code='AZ'), 'Camelback Mountain', 'nature_site', 'Paradise Valley', 'Greater Phoenix', 'City of Phoenix', NULL, 'One of the most popular urban hiking destinations in the US with two challenging summit trails (Echo Canyon and Cholla) offering 360-degree valley views.', 'https://www.phoenix.gov/parks/trails/locations/camelback-mountain', 0);

-- Arizona Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='AZ'), 'Waste Management Phoenix Open', 'sporting_event', 'Scottsdale', 2, 'The Greatest Show on Grass, the best-attended PGA Tour event with 700,000+ fans and the famously raucous 16th hole stadium.', 700000, 1),
((SELECT id FROM states WHERE code='AZ'), 'Arizona State Fair', 'state_fair', 'Phoenix', 10, 'Annual state fair with carnival rides, concerts, livestock exhibitions, fried food, and a midway at the Arizona State Fairgrounds since 1884.', 1100000, 1),
((SELECT id FROM states WHERE code='AZ'), 'Tucson Gem & Mineral Show', 'convention', 'Tucson', 2, 'World''s largest gem, mineral, and fossil marketplace with 65,000+ guests and 40+ individual shows across the city.', 65000, 1),
((SELECT id FROM states WHERE code='AZ'), 'Scottsdale Culinary Festival', 'food_festival', 'Scottsdale', 4, 'Week-long celebration of Arizona''s culinary scene with chef demonstrations, tastings, and the Great Arizona Picnic.', 35000, 0);

-- ============================================================
-- TENNESSEE
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='TN'), 'Great Smoky Mountains National Park', 'national_park', 'Gatlinburg', 'East Tennessee', 'National Park Service', 1934, 'America''s most-visited national park with 14 million annual visitors, 800+ miles of trails, Cades Cove historic valley, Clingmans Dome, and world-class biodiversity.', 'https://www.nps.gov/grsm/', 1),
((SELECT id FROM states WHERE code='TN'), 'Dollywood', 'theme_park', 'Pigeon Forge', 'East Tennessee', 'Herschend Family Entertainment', 1961, 'Dolly Parton''s Appalachian-themed park with 9 coasters, including Lightning Rod, craft demonstrations, gospel music, and the adjoining Splash Country water park.', 'https://www.dollywood.com/', 1),
((SELECT id FROM states WHERE code='TN'), 'Country Music Hall of Fame and Museum', 'museum', 'Nashville', 'Middle Tennessee', 'Non-profit', 1967, 'The world''s largest popular music museum with 2.5 million artifacts chronicling country music history, the Taylor Swift Education Center, and Hatch Show Print.', 'https://countrymusichalloffame.org/', 1),
((SELECT id FROM states WHERE code='TN'), 'Graceland', 'historic_site', 'Memphis', 'West Tennessee', 'Authentic Brands Group', 1982, 'Elvis Presley''s 13.8-acre estate and mansion, the second most-visited home in America after the White House, with the Jungle Room, trophy building, and Meditation Garden.', 'https://www.graceland.com/', 1),
((SELECT id FROM states WHERE code='TN'), 'Ryman Auditorium', 'music_venue', 'Nashville', 'Middle Tennessee', 'Ryman Hospitality', 1892, 'The Mother Church of Country Music with legendary acoustics, former home of the Grand Ole Opry, now hosting concerts and the Rock Hall at the Ryman exhibit.', 'https://www.ryman.com/', 1),
((SELECT id FROM states WHERE code='TN'), 'Grand Ole Opry', 'music_venue', 'Nashville', 'Middle Tennessee', 'Ryman Hospitality', 1925, 'The longest-running radio broadcast in US history featuring country music''s biggest stars in a 4,400-seat venue, with backstage tours and the iconic circle of wood center stage.', 'https://www.opry.com/', 1),
((SELECT id FROM states WHERE code='TN'), 'Beale Street', 'entertainment_district', 'Memphis', 'West Tennessee', 'City of Memphis', 1841, 'Home of the Blues, a 1.8-mile National Historic Landmark district with legendary clubs like B.B. King''s Blues Club, live music, Southern soul food, and the Beale Street Flippers.', 'https://www.bealestreet.com/', 1),
((SELECT id FROM states WHERE code='TN'), 'Tennessee Aquarium', 'zoo_aquarium', 'Chattanooga', 'East Tennessee', 'Non-profit', 1992, 'Two-building aquarium on the Tennessee River with the world''s largest freshwater aquarium, an IMAX theater, and a River Gorge Explorer boat tour.', 'https://www.tnaqua.org/', 0),
((SELECT id FROM states WHERE code='TN'), 'Lookout Mountain', 'nature_site', 'Chattanooga', 'East Tennessee', 'Various', NULL, 'Scenic mountaintop with Rock City gardens, Ruby Falls underground waterfall, and the Incline Railway (steepest passenger railway in the world at 72.7% grade).', 'https://www.lookoutmountain.com/', 1),
((SELECT id FROM states WHERE code='TN'), 'Sun Studio', 'historic_site', 'Memphis', 'West Tennessee', 'Private', 1950, 'The birthplace of rock ''n'' roll where Elvis, Johnny Cash, Jerry Lee Lewis, and B.B. King first recorded, still a working recording studio by night.', 'https://www.sunstudio.com/', 0),
((SELECT id FROM states WHERE code='TN'), 'National Civil Rights Museum', 'museum', 'Memphis', 'West Tennessee', 'Non-profit', 1991, 'Museum built around the Lorraine Motel where Dr. Martin Luther King Jr. was assassinated in 1968, tracing the civil rights movement from slavery to today.', 'https://www.civilrightsmuseum.org/', 1);

-- Tennessee Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='TN'), 'Bonnaroo Music and Arts Festival', 'music_festival', 'Manchester', 6, 'Four-day camping festival on a 700-acre farm with 150+ acts, comedy, cinema, art installations, and the famous arch entrance on What Stage.', 80000, 1),
((SELECT id FROM states WHERE code='TN'), 'CMA Music Festival', 'music_festival', 'Nashville', 6, 'Four-day fan-focused country music event with hundreds of artists performing across multiple stages, meet-and-greets, and the nightly Nissan Stadium shows.', 80000, 1),
((SELECT id FROM states WHERE code='TN'), 'Memphis in May International Festival', 'cultural_festival', 'Memphis', 5, 'Month-long celebration with the World Championship Barbecue Cooking Contest, Beale Street Music Festival, and honoring a different country each year.', 200000, 1),
((SELECT id FROM states WHERE code='TN'), 'National Storytelling Festival', 'cultural_festival', 'Jonesborough', 10, 'The oldest and largest storytelling festival in the US, with 10,000 attendees gathering in tents to hear master storytellers from around the world.', 10000, 0);

-- ============================================================
-- LOUISIANA
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='LA'), 'French Quarter (Vieux Carre)', 'historic_district', 'New Orleans', 'Greater New Orleans', 'City of New Orleans', 1718, 'The oldest neighborhood in New Orleans with Bourbon Street nightlife, Jackson Square, St. Louis Cathedral, Cafe Du Monde, and Spanish-French colonial architecture with wrought-iron balconies.', 'https://www.frenchquarter.com/', 1),
((SELECT id FROM states WHERE code='LA'), 'Mardi Gras World', 'museum_working', 'New Orleans', 'Greater New Orleans', 'Kern Studios', 1947, 'Working studio where Mardi Gras floats are designed and built year-round, offering behind-the-scenes tours of float construction and prop sculpting since 1947.', 'https://www.mardigrasworld.com/', 0),
((SELECT id FROM states WHERE code='LA'), 'National WWII Museum', 'museum', 'New Orleans', 'Greater New Orleans', 'Non-profit', 2000, 'Top-rated attraction in New Orleans and one of the world''s best military museums, with immersive galleries, 4D cinematic experience, restored aircraft, and the final mission of the USS Tang submarine experience.', 'https://www.nationalww2museum.org/', 1),
((SELECT id FROM states WHERE code='LA'), 'Audubon Zoo', 'zoo_aquarium', 'New Orleans', 'Greater New Orleans', 'Audubon Nature Institute', 1914, '58-acre zoo in historic Uptown with the Louisiana Swamp exhibit, white alligators, a Mayan-themed jaguar jungle, and the Cool Zoo splash park.', 'https://audubonnatureinstitute.org/zoo', 0),
((SELECT id FROM states WHERE code='LA'), 'Audubon Aquarium of the Americas', 'zoo_aquarium', 'New Orleans', 'Greater New Orleans', 'Audubon Nature Institute', 1990, '400,000-gallon Gulf of Mexico exhibit, a 30-foot Great Maya Reef tunnel, penguin colony, sea otters, and the Parakeet Pointe interactive aviary.', 'https://audubonnatureinstitute.org/aquarium', 0),
((SELECT id FROM states WHERE code='LA'), 'Oak Alley Plantation', 'historic_site', 'Vacherie', 'River Parishes', 'Non-profit', 1920, 'Most photographed plantation in Louisiana with a quarter-mile alley of 300-year-old live oaks leading to a Greek Revival mansion, with slavery memorial exhibit and restaurant.', 'https://www.oakalleyplantation.org/', 1),
((SELECT id FROM states WHERE code='LA'), 'New Orleans City Park', 'urban_park', 'New Orleans', 'Greater New Orleans', 'Non-profit', 1854, '1,300-acre urban park (50% larger than Central Park) with the New Orleans Museum of Art, Besthoff Sculpture Garden, Botanical Garden, Storyland, and the oldest grove of mature live oaks in the world.', 'https://neworleanscitypark.com/', 0),
((SELECT id FROM states WHERE code='LA'), 'Atchafalaya Basin', 'nature_region', 'Breaux Bridge', 'Cajun Country', 'State of Louisiana', NULL, 'The largest wetland and swamp in the US covering nearly 1 million acres, with airboat swamp tours, paddling trails, and world-famous crawfish and Cajun culture.', 'https://www.louisianatravel.com/nature/atchafalaya-basin', 1),
((SELECT id FROM states WHERE code='LA'), 'St. Louis Cathedral', 'historic_site', 'New Orleans', 'Greater New Orleans', 'Archdiocese of New Orleans', 1794, 'Oldest continuously active Catholic cathedral in the US overlooking Jackson Square with triple steeples, stunning stained glass, and a nightly free concert series.', 'https://www.stlouiscathedral.org/', 1),
((SELECT id FROM states WHERE code='LA'), 'Whitney Plantation', 'historic_site', 'Wallace', 'River Parishes', 'Non-profit', 2014, 'A plantation museum focused exclusively on slavery, with first-person slave narratives, memorials, restored slave cabins, and the Wall of Honor listing 350+ enslaved people.', 'https://www.whitneyplantation.org/', 1);

-- Louisiana Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='LA'), 'Mardi Gras', 'cultural_festival', 'New Orleans', 2, 'The world''s largest free party spanning weeks of parades from 60+ krewes, elaborate floats, masquerade balls, king cake, and the culminating Fat Tuesday celebration.', 1400000, 1),
((SELECT id FROM states WHERE code='LA'), 'New Orleans Jazz & Heritage Festival', 'music_festival', 'New Orleans', 4, 'Seven-day festival across two weekends celebrating the music and culture of New Orleans and Louisiana across 12 stages with A-list headliners and local legends.', 475000, 1),
((SELECT id FROM states WHERE code='LA'), 'Essence Festival of Culture', 'cultural_music_festival', 'New Orleans', 7, 'The largest African American cultural and music event in the US, with three nights of concerts at the Superdome and daytime empowerment programming.', 500000, 1),
((SELECT id FROM states WHERE code='LA'), 'French Quarter Festival', 'music_food_festival', 'New Orleans', 4, 'Free four-day festival showcasing local music on 20+ stages throughout the French Quarter with the world''s largest jazz brunch from 60+ food vendors.', 700000, 1),
((SELECT id FROM states WHERE code='LA'), 'Festival International de Louisiane', 'cultural_festival', 'Lafayette', 4, 'Five-day free international music and arts festival celebrating Francophone heritage with artists from 20+ countries across downtown Lafayette.', 300000, 0);

-- ============================================================
-- COLORADO
-- ============================================================
INSERT OR IGNORE INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature) VALUES
((SELECT id FROM states WHERE code='CO'), 'Rocky Mountain National Park', 'national_park', 'Estes Park', 'Front Range', 'National Park Service', 1915, '415-square-mile alpine wonderland with Trail Ridge Road (highest continuous paved road in the US at 12,183 ft), 355 miles of trails, Longs Peak, and abundant elk herds.', 'https://www.nps.gov/romo/', 1),
((SELECT id FROM states WHERE code='CO'), 'Vail Ski Resort', 'ski_resort', 'Vail', 'Colorado Rockies', 'Vail Resorts', 1962, 'One of the world''s largest single-mountain ski resorts with 5,317 acres, legendary Back Bowls, Blue Sky Basin, pedestrian village, and summer activities in the White River National Forest.', 'https://www.vail.com/', 1),
((SELECT id FROM states WHERE code='CO'), 'Aspen Snowmass', 'ski_resort', 'Aspen', 'Colorado Rockies', 'Aspen Skiing Company', 1946, 'Four mountains (Snowmass, Aspen Mountain, Aspen Highlands, Buttermilk) with 5,527 skiable acres, the X Games venue, and the iconic Maroon Bells wilderness backdrop.', 'https://www.aspensnowmass.com/', 1),
((SELECT id FROM states WHERE code='CO'), 'Red Rocks Park and Amphitheatre', 'music_venue', 'Morrison', 'Front Range', 'City of Denver', 1941, 'Geologically formed open-air amphitheater flanked by 300-foot red sandstone monoliths, with near-perfect acoustics, a museum, and the most iconic concert venue in America.', 'https://www.redrocksonline.com/', 1),
((SELECT id FROM states WHERE code='CO'), 'Garden of the Gods', 'nature_park', 'Colorado Springs', 'Front Range', 'City of Colorado Springs', 1909, 'Free public park with dramatic 300-foot red rock formations against a Pikes Peak backdrop, 21 miles of trails, rock climbing, and a visitor and nature center.', 'https://www.gardenofgods.com/', 1),
((SELECT id FROM states WHERE code='CO'), 'Mesa Verde National Park', 'national_park', 'Mancos', 'Southwest Colorado', 'National Park Service', 1906, 'UNESCO World Heritage site protecting 5,000 Ancestral Puebloan archaeological sites including the famous Cliff Palace cliff dwellings built into sandstone alcoves from 1190-1300 AD.', 'https://www.nps.gov/meve/', 1),
((SELECT id FROM states WHERE code='CO'), 'Breckenridge Ski Resort', 'ski_resort', 'Breckenridge', 'Colorado Rockies', 'Vail Resorts', 1961, 'World-class ski resort with Five Peaks offering 2,908 acres of terrain, the highest chairlift in North America (Imperial Express at 12,840 ft), and a charming Victorian-era downtown.', 'https://www.breckenridge.com/', 0),
((SELECT id FROM states WHERE code='CO'), 'Pikes Peak - America''s Mountain', 'nature_site', 'Cascade', 'Front Range', 'City of Colorado Springs', NULL, '14,115-foot summit inspiring ''America the Beautiful'' with the Pikes Peak Highway (19 miles of scenic driving), the Broadmoor Manitou Railway cog train, and donuts at the summit house.', 'https://www.pikespeakcolorado.com/', 1),
((SELECT id FROM states WHERE code='CO'), 'Denver Art Museum', 'museum', 'Denver', 'Front Range', 'Non-profit', 1893, 'One of the largest art museums between Chicago and the West Coast, with the Hamilton Building designed by Daniel Libeskind, housing 70,000 works across 12 collections.', 'https://www.denverartmuseum.org/', 0),
((SELECT id FROM states WHERE code='CO'), 'Great Sand Dunes National Park and Preserve', 'national_park', 'Mosca', 'Southern Colorado', 'National Park Service', 2004, 'The tallest dunes in North America at 750 feet against the Sangre de Cristo Mountains, with Medano Creek beach, sandboarding, and dark-sky stargazing.', 'https://www.nps.gov/grsa/', 1),
((SELECT id FROM states WHERE code='CO'), 'Telluride Ski Resort', 'ski_resort', 'Telluride', 'Southwest Colorado', 'Various', 1972, 'Box-canyon ski resort in the San Juan Mountains with 2,000+ acres, a free gondola connecting town to Mountain Village, and the legendary Revelation Bowl hike-to terrain.', 'https://www.tellurideskiresort.com/', 0);

-- Colorado Events
INSERT OR IGNORE INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature) VALUES
((SELECT id FROM states WHERE code='CO'), 'Telluride Film Festival', 'film_festival', 'Telluride', 9, 'Prestigious Labor Day weekend film festival launching major Oscar contenders with no paparazzi, intimate venues, and surprise sneak previews in a stunning mountain setting.', 5000, 1),
((SELECT id FROM states WHERE code='CO'), 'Aspen Food & Wine Classic', 'food_festival', 'Aspen', 6, 'The premier culinary event in America with cooking demonstrations, wine tastings, and seminars from world-renowned chefs and sommeliers.', 5000, 1),
((SELECT id FROM states WHERE code='CO'), 'Great American Beer Festival', 'food_festival', 'Denver', 9, 'The largest commercial beer competition and public tasting event in the US with 500 breweries pouring 2,000+ beers across 3 days at the Colorado Convention Center.', 60000, 1),
((SELECT id FROM states WHERE code='CO'), 'X Games Aspen', 'sporting_event', 'Aspen', 1, 'Premier winter action sports competition at Buttermilk Mountain with skiing and snowboarding SuperPipe, Big Air, and Slopestyle events.', 50000, 1),
((SELECT id FROM states WHERE code='CO'), 'Telluride Bluegrass Festival', 'music_festival', 'Telluride', 6, 'Legendary 4-day bluegrass and roots music festival in Town Park, surrounded by 13,000-foot peaks, known for impromptu collaborations and the band contest.', 12000, 0);

-- ============================================================
-- VIEWS for cross-state analytics
-- ============================================================

CREATE VIEW IF NOT EXISTS v_tourism_by_state AS
SELECT s.code, s.name AS state_name, s.tourism_summary, s.tourism_economy_share,
    COUNT(v.id) AS total_venues,
    COUNT(DISTINCT CASE WHEN v.is_signature = 1 THEN v.id END) AS signature_venues
FROM states s
LEFT JOIN venues v ON s.id = v.state_id
WHERE s.is_top_tourism = 1
GROUP BY s.id
ORDER BY total_venues DESC;

CREATE VIEW IF NOT EXISTS v_national_parks AS
SELECT s.code AS state, v.name AS park_name, v.description, v.opening_year
FROM venues v
JOIN states s ON v.state_id = s.id
WHERE v.category IN ('national_park', 'national_monument')
ORDER BY v.opening_year;

CREATE VIEW IF NOT EXISTS v_signature_events AS
SELECT s.name AS state_name, e.name AS event_name, e.event_type, e.city, e.month_of_year, e.annual_attendance
FROM state_events e
JOIN states s ON e.state_id = s.id
WHERE e.is_signature = 1
ORDER BY e.month_of_year, s.name;

CREATE VIEW IF NOT EXISTS v_venue_categories AS
SELECT s.code, s.name AS state, v.category,
    COUNT(v.id) AS venue_count
FROM venues v
JOIN states s ON v.state_id = s.id
GROUP BY s.code, s.name, v.category
ORDER BY s.name, venue_count DESC;

SELECT 'Tourism database for 9 states populated successfully' AS status;