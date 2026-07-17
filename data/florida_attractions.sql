-- ================================================================
-- FLORIDA ATTRACTIONS DATABASE - COMPLETE CATALOG
-- Parks and their attractions/rides/exhibits
-- ================================================================

-- ============================================================
-- REMAINING PARKS (those not yet inserted)
-- ============================================================

INSERT OR IGNORE INTO fl_parks (name, category, city, region, parent_company, opening_year, description, website) VALUES

-- PANHANDLE REGION
('Emerald Coast Science Center', 'museum', 'Fort Walton Beach', 'Panhandle', 'Non-profit', 1989, 'A hands-on science discovery center with interactive STEM exhibits for families.', 'https://www.ecscience.org/'),
('ZooWorld Panama City Beach', 'zoo_aquarium', 'Panama City Beach', 'Panhandle', 'Private', 1976, 'A conservation-focused zoo with exotic animals and interactive encounters including giraffe feedings.', 'https://www.zooworldpcb.com/'),
('Pensacola Lighthouse', 'historic_site', 'Pensacola', 'Panhandle', 'Non-profit', 1859, 'A historic lighthouse still guiding ships into Pensacola Bay with 177 steps and paranormal history.', 'https://www.pensacolalighthouse.org/'),
('Man in the Sea Museum', 'museum', 'Panama City Beach', 'Panhandle', 'Non-profit', 1982, 'A museum dedicated to underwater exploration history featuring SEALAB submersibles.', 'https://www.maninthesea.org/'),
('Florida Caverns State Park', 'nature_park', 'Marianna', 'Panhandle', 'Florida State Parks', 1942, 'The only Florida state park with public cave tours in stunning limestone formations.', 'https://www.floridastateparks.org/FloridaCaverns'),
('Shipwreck Island Waterpark', 'water_park', 'Panama City Beach', 'Panhandle', 'Private', 1983, 'A family water park with the 500000-gallon wave pool and Tree Top Drop slides.', 'https://www.shipwreckisland.com/'),
('Gulf World Marine Park', 'zoo_aquarium', 'Panama City Beach', 'Panhandle', 'Private', 1969, 'Marine park with dolphin shows, stingray encounters, and tropical bird exhibits.', 'https://www.gulfworldmarinepark.com/'),

-- THE KEYS
('Dry Tortugas National Park', 'nature_park', 'Key West', 'Keys', 'National Park Service', 1992, 'A remote island paradise 70 miles west of Key West featuring Fort Jefferson, snorkeling, and pristine beaches.', 'https://www.nps.gov/drto/'),
('Key West Butterfly and Nature Conservatory', 'zoo_aquarium', 'Key West', 'Keys', 'Private', 2003, 'A glass-domed tropical butterfly habitat with 50-60 butterfly species and exotic birds.', 'https://www.keywestbutterfly.com/'),
('Key West Aquarium', 'zoo_aquarium', 'Key West', 'Keys', 'Private', 1934, 'One of Florida''s oldest aquariums featuring touch tanks, shark feedings, and native Keys marine life.', 'https://www.keywestaquarium.com/'),
('Ernest Hemingway Home and Museum', 'historic_site', 'Key West', 'Keys', 'Private', 1931, 'The legendary author''s residence featuring six-toed cats, tropical gardens, and Hemingway''s writing studio.', 'https://www.hemingwayhome.com/'),
('Truman Little White House', 'historic_site', 'Key West', 'Keys', 'Private', 1890, 'A historic presidential retreat used by Harry Truman and later presidents, now a museum.', 'https://www.trumanlittlewhitehouse.com/'),
('Theater of the Sea', 'zoo_aquarium', 'Islamorada', 'Keys', 'Private', 1946, 'A marine mammal park offering dolphin swims, sea lion shows, and bottomless boat rides.', 'https://theaterofthesea.com/'),
('John Pennekamp Coral Reef State Park', 'nature_park', 'Key Largo', 'Keys', 'Florida State Parks', 1963, 'The first undersea park in the US with a living coral reef, glass-bottom boats, and snorkeling.', 'https://pennekamppark.com/'),
('Mel Fisher Maritime Museum', 'museum', 'Key West', 'Keys', 'Non-profit', 1992, 'Home to treasures from the Spanish galleon Nuestra Senora de Atocha including gold and silver.', 'https://www.melfisher.org/'),
('Florida Keys Eco-Discovery Center', 'museum', 'Key West', 'Keys', 'NOAA', 2007, 'An interactive environmental education center exploring Keys habitats including coral reefs.', 'https://floridakeys.noaa.gov/eco_discovery.html'),

-- SPACE COAST
('Brevard Zoo', 'zoo_aquarium', 'Melbourne', 'Space_Coast', 'Non-profit', 1994, 'A community-built zoo featuring kayak tours through animal exhibits, a treetop trek, and hands-on encounters.', 'https://brevardzoo.org/'),
('Valiant Air Command Warbird Museum', 'museum', 'Titusville', 'Space_Coast', 'Non-profit', 1977, 'A museum with over 45 warbirds from WWI to present day, including aircraft restorations.', 'https://www.valiantaircommand.com/'),
('American Space Museum', 'museum', 'Titusville', 'Space_Coast', 'Non-profit', 2001, 'A walk through space history with artifacts from Mercury, Gemini, Apollo, and Space Shuttle programs.', 'https://www.spacewalkoffame.org/'),

-- CENTRAL FLORIDA (non-Orlando)
('Bok Tower Gardens', 'garden', 'Lake Wales', 'Central_Florida', 'Non-profit', 1929, 'A 250-acre contemplative garden and bird sanctuary featuring a 205-foot Singing Tower carillon.', 'https://boktowergardens.org/'),
('Weeki Wachee Springs State Park', 'nature_park', 'Weeki Wachee', 'Central_Florida', 'Florida State Parks', 1947, 'Home to the famous live underwater mermaid shows, buccaneer bay water park, and river boat rides.', 'https://www.floridastateparks.org/WeekiWachee'),
('Silver Springs State Park', 'nature_park', 'Silver Springs', 'Central_Florida', 'Florida State Parks', 1870, 'One of Florida''s first tourist attractions featuring glass-bottom boat tours over crystal-clear springs.', 'https://www.floridastateparks.org/SilverSprings'),
('Ellie Schiller Homosassa Springs Wildlife State Park', 'zoo_aquarium', 'Homosassa', 'Central_Florida', 'Florida State Parks', 1900, 'A wildlife state park with Florida species including manatees, alligators, and an underwater observatory.', 'https://www.floridastateparks.org/HomosassaSprings'),

-- SOUTHWEST FLORIDA
('Naples Zoo at Caribbean Gardens', 'zoo_aquarium', 'Naples', 'SW_Florida', 'Non-profit', 1919, 'A nationally accredited zoo set in a historic tropical garden with primate expedition cruises.', 'https://www.napleszoo.org/'),
('Edison and Ford Winter Estates', 'museum', 'Fort Myers', 'SW_Florida', 'Non-profit', 1886, 'The historic winter homes of Thomas Edison and Henry Ford with a museum of inventions and botanical gardens.', 'https://www.edisonfordwinterestates.org/'),
('Everglades Wonder Gardens', 'zoo_aquarium', 'Bonita Springs', 'SW_Florida', 'Private', 1936, 'An Old Florida roadside attraction with botanical gardens, flamingos, alligators, and rescued animals.', 'https://evergladeswondergardens.com/'),
('Golisano Childrens Museum of Naples', 'museum', 'Naples', 'SW_Florida', 'Non-profit', 2012, 'A hands-on children''s museum exploring science, nature, and art through interactive exhibits.', 'https://www.cmon.org/'),
('IMAG History and Science Center', 'museum', 'Fort Myers', 'SW_Florida', 'Non-profit', 1995, 'An interactive museum with aquarium touch tanks, a 3D theater, and hands-on science exhibits.', 'https://theimag.org/'),
('Seminole Ah-Tah-Thi-Ki Museum', 'museum', 'Big Cypress', 'SW_Florida', 'Seminole Tribe', 1997, 'A museum celebrating Seminole history and culture with artifacts and a ceremonial village exhibit.', 'https://www.ahtahthiki.com/'),

-- MIAMI / FORT LAUDERDALE (additional)
('Vizcaya Museum and Gardens', 'museum', 'Miami', 'Miami_Ft_Lauderdale', 'Miami-Dade County', 1916, 'An Italian Renaissance-style villa on Biscayne Bay with 10 acres of formal gardens and art collections.', 'https://vizcaya.org/'),
('Perez Art Museum Miami', 'museum', 'Miami', 'Miami_Ft_Lauderdale', 'Non-profit', 2013, 'A modern and contemporary art museum on Biscayne Bay with outdoor sculptures and hanging gardens.', 'https://www.pamm.org/'),
('Miami Childrens Museum', 'museum', 'Miami', 'Miami_Ft_Lauderdale', 'Non-profit', 1983, 'An interactive museum on Watson Island with bilingual exhibits focused on arts, culture, and community.', 'https://www.miamichildrensmuseum.org/'),
('Morikami Museum and Japanese Gardens', 'museum', 'Delray Beach', 'Miami_Ft_Lauderdale', 'Non-profit', 1977, 'A Japanese cultural center with two museum buildings and 16 acres of authentic Japanese gardens.', 'https://morikami.org/'),
('Loggerhead Marinelife Center', 'zoo_aquarium', 'Juno Beach', 'Miami_Ft_Lauderdale', 'Non-profit', 1983, 'A sea turtle hospital and marine conservation center on the beach with turtle rehabilitation viewing.', 'https://marinelife.org/'),
('Norton Museum of Art', 'museum', 'West Palm Beach', 'Miami_Ft_Lauderdale', 'Non-profit', 1941, 'An art museum with over 8200 works spanning European, American, Chinese, and contemporary art.', 'https://www.norton.org/'),
('Sawgrass Recreation Park', 'nature_park', 'Weston', 'Miami_Ft_Lauderdale', 'Private', 1966, 'An Everglades airboat and wildlife park with alligator shows, animal exhibits, and swamp tours.', 'https://www.evergladestours.com/'),

-- TAMPA BAY (additional)
('Great Explorations Childrens Museum', 'museum', 'St. Petersburg', 'Tampa_Bay', 'Non-profit', 1987, 'A hands-on children''s museum next to Sunken Gardens with interactive exhibits and play areas.', 'https://greatexplorations.org/'),
('Tampa Bay History Center', 'museum', 'Tampa', 'Tampa_Bay', 'Non-profit', 2009, 'A Smithsonian-affiliated museum exploring 12000 years of Florida history from native peoples to pirates.', 'https://tampabayhistorycenter.org/'),
('Glazer Childrens Museum', 'museum', 'Tampa', 'Tampa_Bay', 'Non-profit', 2010, 'A children''s museum in downtown Tampa with over 170 hands-on exhibits across multiple themed floors.', 'https://glazermuseum.org/'),
('Imagine Museum', 'museum', 'St. Petersburg', 'Tampa_Bay', 'Non-profit', 2018, 'A museum dedicated to contemporary studio glass art with over 500 pieces of American glass art.', 'https://www.imaginemuseum.com/'),
('Chihuly Collection', 'museum', 'St. Petersburg', 'Tampa_Bay', 'Morean Arts Center', 2010, 'A permanent collection of Dale Chihuly''s large-scale glass installations in a custom-designed space.', 'https://moreanartscenter.org/chihuly/'),

-- JACKSONVILLE / NORTH FLORIDA (additional)
('Museum of Science and History (MOSH)', 'museum', 'Jacksonville', 'Jacksonville', 'Non-profit', 1941, 'A science museum on the Southbank with planetarium shows, a native animal exhibit, and history galleries.', 'https://themosh.org/'),
('Fort Clinch State Park', 'historic_site', 'Fernandina Beach', 'North_Florida', 'Florida State Parks', 1938, 'A Civil War-era brick fort within a 1400-acre park with beaches, hiking, and living history reenactments.', 'https://www.floridastateparks.org/FortClinch'),
('World Golf Hall of Fame and Museum', 'museum', 'St. Augustine', 'Jacksonville', 'PGA Tour', 1998, 'A museum celebrating golf''s greatest players and history with interactive exhibits and a challenge hole.', 'https://www.worldgolfhalloffame.org/'),

-- EVERGLADES AND SOUTH FLORIDA NATURE
('Everglades National Park', 'nature_park', 'Homestead', 'Miami_Ft_Lauderdale', 'National Park Service', 1947, 'A 1.5-million-acre subtropical wilderness spanning mangroves, sawgrass marshes, and cypress domes.', 'https://www.nps.gov/ever/'),
('Biscayne National Park', 'nature_park', 'Homestead', 'Miami_Ft_Lauderdale', 'National Park Service', 1980, 'A marine national park protecting coral reefs, mangrove shorelines, and the northernmost Florida Keys.', 'https://www.nps.gov/bisc/'),
('Big Cypress National Preserve', 'nature_park', 'Ochopee', 'SW_Florida', 'National Park Service', 1974, 'A 729000-acre freshwater swamp ecosystem adjacent to the Everglades with cypress domes and wildlife.', 'https://www.nps.gov/bicy/'),

-- OTHER NOTABLE ATTRACTIONS
('Orlando Science Center', 'museum', 'Orlando', 'Orlando', 'Non-profit', 1955, 'A hands-on science museum with four floors of exhibits, a planetarium, and giant-screen theater.', 'https://www.osc.org/'),
('WonderWorks Orlando', 'museum', 'Orlando', 'Orlando', 'WonderWorks', 1998, 'An upside-down house on I-Drive with over 100 hands-on science exhibits, laser tag, and a 4D theater.', 'https://www.wonderworksonline.com/orlando/'),
('Crayola Experience Orlando', 'museum', 'Orlando', 'Orlando', 'Crayola', 2015, 'An interactive attraction at The Florida Mall where kids create colorful Crayola-themed art projects.', 'https://www.crayolaexperience.com/orlando/'),
('Museum of Illusions Orlando', 'museum', 'Orlando', 'Orlando', 'Private', 2021, 'An interactive visual and sensory museum with holograms, optical illusions, and photo-reactive rooms.', 'https://miamiorlando.museumofillusions.com/'),

-- SANFORD / CENTRAL FL
('Central Florida Zoo and Botanical Gardens', 'zoo_aquarium', 'Sanford', 'Central_Florida', 'Non-profit', 1975, 'A 116-acre zoo with over 400 animals, a splash ground, zip line adventures, and rope courses.', 'https://www.centralfloridazoo.org/'),
('DeLand Naval Air Station Museum', 'museum', 'DeLand', 'Central_Florida', 'Non-profit', 1995, 'A museum preserving naval aviation history in a restored 1940s barracks building.', 'https://www.delandnavalairmuseum.org/'),

-- TAMPA BAY BEACH
('Pier 60 Clearwater', 'entertainment_complex', 'Clearwater Beach', 'Tampa_Bay', 'City of Clearwater', 1989, 'A 1080-foot fishing pier with nightly sunset celebrations, street performers, and crafts.', 'https://www.visitclearwaterflorida.com/things-to-do/pier-60/');


-- ============================================================
-- LAND AREAS (Themed Sections of Major Parks)
-- ============================================================

-- First, get park IDs
-- We will reference parks by name for readability; use subqueries

-- MAGIC KINGDOM LAND AREAS
INSERT OR IGNORE INTO fl_land_areas (park_id, name, description, theme, opening_year) VALUES
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Main Street U.S.A.', 'Turn-of-the-century American small town entrance corridor inspired by Walt Disneys hometown of Marceline, Missouri.', 'Early 1900s Americana', 1971),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Adventureland', 'Exotic tropical locale evoking jungles of Africa, Asia, and the South Pacific.', 'Jungle exploration', 1971),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Frontierland', 'The American Old West with cowboys, pioneers, and river country.', 'Wild West frontier', 1971),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Liberty Square', 'Colonial America inspired by the American Revolution and 13 original colonies.', 'Colonial America', 1971),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Fantasyland', 'A fairy-tale realm where classic Disney animated stories come to life.', 'Disney fairy tales', 1971),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Tomorrowland', 'A retro-futuristic vision of the future with sci-fi theming.', 'Retro-futuristic sci-fi', 1971),

-- EPCOT LAND AREAS
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Celebration', 'The central spine with Spaceship Earth, Dreamers Point, and festival gardens.', 'Festival core', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Discovery', 'Science and technology hub featuring space and transportation innovations.', 'Science and exploration', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Nature', 'Land pavilion and sea pavilion exploring Earths natural systems.', 'Nature and conservation', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Mexico', 'Mexican pyramid with Gran Fiesta Tour boat ride.', 'Mexico', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Norway', 'Scandinavian village with Frozen Ever After attraction.', 'Norway', 1988),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - China', 'Chinese temple gardens with Reflections of China Circle-Vision film.', 'China', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Germany', 'Bavarian village plaza with clock tower and Biergarten.', 'Germany', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Italy', 'Venetian piazza with St. Marks Campanile recreation.', 'Italy', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - American Adventure', 'Colonial-style building hosting the American Adventure Audio-Animatronic show.', 'United States', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Japan', 'Japanese pagoda, gardens, and Mitsukoshi department store.', 'Japan', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Morocco', 'Moroccan medina with intricate tilework and a replica Koutoubia minaret.', 'Morocco', 1984),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - France', 'Parisian streetscape with Eiffel Tower view, bakery, and Remys Ratatouille Adventure.', 'France', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - United Kingdom', 'British village with cobblestone streets, pub, and Tudor-style architecture.', 'United Kingdom', 1982),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'World Showcase - Canada', 'Canadian Rockies-inspired canyon with waterfall and O Canada! film.', 'Canada', 1982),

-- HOLLYWOOD STUDIOS LAND AREAS
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Hollywood Boulevard', 'Golden Age of Hollywood entrance street lined with shops and streetmosphere performers.', '1930s-40s Hollywood', 1989),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Echo Lake', 'A lake area with diner-style eateries and documentary theming.', 'Mid-century Hollywood', 1989),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Grand Avenue', 'A contemporary city street themed to modern-day Los Angeles anchored by MuppetVision 3D.', 'Modern LA', 1989),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Star Wars: Galaxy''s Edge', 'The Black Spire Outpost village on the planet Batuu with Millennium Falcon and Rise of the Resistance.', 'Star Wars', 2019),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Toy Story Land', 'Andys backyard supersized with giant Tinkertoys and a family coaster.', 'Toy Story/Pixar', 2018),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Animation Courtyard', 'Disney animation celebration area with shows and character meet-and-greets.', 'Disney/Pixar animation', 1989),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Sunset Boulevard', 'Glamorous 1940s Hollywood leading to the Twilight Zone Tower of Terror and Rock n Roller Coaster.', '1940s Hollywood noir', 1994),

-- ANIMAL KINGDOM LAND AREAS
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Oasis', 'Tropical entry garden with animal exhibits leading to Discovery Island.', 'Tropical oasis', 1998),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Discovery Island', 'Central hub with the Tree of Life and surrounding animal trails.', 'Animal discovery hub', 1998),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Africa', 'The fictional Harambe village with Kilimanjaro Safaris and Gorilla Falls.', 'East Africa', 1998),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Asia', 'The fictional kingdom of Anandapur with Expedition Everest and Kali River Rapids.', 'South/SE Asia', 1999),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'DinoLand U.S.A.', 'A roadside dinosaur attraction and paleontology dig site with DINOSAUR dark ride.', 'Dinosaur Americana', 1998),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Pandora – The World of Avatar', 'Alien moon of Pandora with floating mountains, bioluminescent plants, and banshee flight.', 'Avatar/Pandora', 2017),

-- UNIVERSAL STUDIOS FLORIDA LAND AREAS
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Production Central', 'Front-of-park area featuring Despicable Me Minion Mayhem and Hollywood Rip Ride Rockit.', 'Modern film production', 1990),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'New York', 'A recreated New York City streetscape with The Blues Brothers show and Revenge of the Mummy.', 'New York City', 1990),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'San Francisco', 'San Francisco waterfront with Fishermans Wharf theming and Fast & Furious.', 'San Francisco', 1990),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'The Wizarding World of Harry Potter – Diagon Alley', 'London alley and shops leading to the hidden wizard shopping district with Gringotts bank.', 'Harry Potter', 2014),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'World Expo', 'International exposition area with Men in Black: Alien Attack.', 'World Expo', 1990),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Springfield: Home of the Simpsons', 'The Simpsons hometown with Kwik-E-Mart, Moes Tavern, and Krustyland.', 'The Simpsons', 2008),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Woody Woodpeckers KidZone', 'Childrens area with ET Adventure, Animal Actors show, and DreamWorks Destination.', 'Kids and animation', 1990),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Hollywood', 'Classic Hollywood themed area with Universal Orlandos Horror Make-Up Show.', 'Classic Hollywood', 1990),

-- ISLANDS OF ADVENTURE LAND AREAS
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Port of Entry', 'Arabian-inspired entrance portal with shops and guest services.', 'Port entry', 1999),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Marvel Super Hero Island', 'Comic-book cityscape with The Incredible Hulk Coaster and The Amazing Adventures of Spider-Man.', 'Marvel Comics', 1999),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Toon Lagoon', 'Classic cartoon theater with water rides based on Popeye and Dudley Do-Right.', 'Sunday comics', 1999),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Skull Island: Reign of Kong', 'Mysterious island expedition with a giant Kong animatronic encounter.', 'King Kong', 2016),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Jurassic Park', 'Isla Nublar recreated from the films featuring the Jurassic Park River Adventure and VelociCoaster.', 'Jurassic Park/World', 1999),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The Wizarding World of Harry Potter – Hogsmeade', 'The snowy village of Hogsmeade with Hogwarts Castle housing Harry Potter and the Forbidden Journey.', 'Harry Potter', 2010),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The Lost Continent', 'Mythic realm with Poseidons Fury walkthrough show and the Mystic Fountain.', 'Ancient mythologies', 1999),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Seuss Landing', 'Dr. Seuss books brought to life in whimsical colors with The Cat in the Hat ride.', 'Dr. Seuss', 1999),

-- EPIC UNIVERSE LAND AREAS
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Celestial Park', 'The central hub with astronomical theming, gardens, roller coaster, and the Luna hotel entrance.', 'Celestial/stars', 2025),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'The Wizarding World of Harry Potter – Ministry of Magic', '1920s Paris and the British Ministry of Magic from the Fantastic Beasts era.', 'Harry Potter/Fantastic Beasts', 2025),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Super Nintendo World', 'Mario Kart and Donkey Kong-themed lands from the Nintendo video game universe.', 'Nintendo/Super Mario', 2025),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'How to Train Your Dragon – Isle of Berk', 'Viking village with dragons from the DreamWorks franchise.', 'How to Train Your Dragon', 2025),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Dark Universe', 'Classic Universal Monsters reimagined in a Victorian-era village with Dracula, Frankenstein, and Wolfman.', 'Universal Monsters', 2025);

-- ============================================================
-- ATTRACTIONS: MAGIC KINGDOM
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
-- Main Street U.S.A.
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Walt Disney World Railroad', 'ride_family', 'Vintage steam train circling the park with views of all lands.', 'Main Street U.S.A.', 'mild', 0, 1971, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Town Square Theater', 'meet_greet', 'Meet Mickey Mouse in his magicians dressing room.', 'Main Street U.S.A.', 'none', 0, 2011, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Disney Festival of Fantasy Parade', 'show_parade', 'Daytime parade with elaborate floats of Disney characters, princesses, and a fire-breathing dragon.', 'Main Street U.S.A.', 'none', 0, 2014, 1, 12.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Happily Ever After', 'show_fireworks', 'Nighttime fireworks and projection show on Cinderella Castle with Tinker Bell flight.', 'Main Street U.S.A.', 'none', 0, 2017, 1, 18.0),

-- Adventureland
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Pirates of the Caribbean', 'ride_dark', 'Classic dark boat ride through pirate-infested Caribbean waters with Captain Jack Sparrow.', 'Adventureland', 'mild', 0, 1973, 1, 8.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Jungle Cruise', 'ride_family', 'Pun-filled boat tour through exotic rivers of Asia, Africa, and South America.', 'Adventureland', 'mild', 0, 1971, 1, 10.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'The Magic Carpets of Aladdin', 'ride_kids', 'Flying carpet spinner ride where riders control the height of their magic carpet.', 'Adventureland', 'mild', 0, 2001, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Swiss Family Treehouse', 'exhibit_interactive', 'Walk-through treehouse inspired by Swiss Family Robinson with water-powered inventions.', 'Adventureland', 'none', 0, 1971, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Walt Disneys Enchanted Tiki Room', 'show_live', 'Classic Audio-Animatronic musical revue with singing birds, flowers, and tiki gods.', 'Adventureland', 'none', 0, 1971, 0, 10.0),

-- Frontierland
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Big Thunder Mountain Railroad', 'ride_thrill', 'Runaway mine train roller coaster through a haunted Old West mountain town.', 'Frontierland', 'moderate', 40, 1980, 1, 3.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Splash Mountain / Tiana''s Bayou Adventure', 'ride_water', 'Log flume journey through Princess Tiana''s bayou celebration culminating in a 52.5-foot drop.', 'Frontierland', 'high', 40, 1992, 1, 10.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Country Bear Musical Jamboree', 'show_live', 'Reimagined Audio-Animatronic bear show singing reinterpreted Disney songs in country style.', 'Frontierland', 'none', 0, 1971, 0, 12.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Tom Sawyer Island', 'play_area', 'Walk-through island with Fort Langhorn, caves, barrel bridge, and a working windmill.', 'Frontierland', 'none', 0, 1973, 0, 30.0),

-- Liberty Square
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Haunted Mansion', 'ride_dark', 'Tour through a ghost-filled manor with 999 happy haunts, stretching rooms, and hitchhiking ghosts.', 'Liberty Square', 'mild', 0, 1971, 1, 7.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Hall of Presidents', 'show_live', 'Stage show featuring Audio-Animatronic figures of all US presidents with historical narration.', 'Liberty Square', 'none', 0, 1971, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Liberty Square Riverboat', 'ride_family', 'Authentic steam-powered riverboat cruise around Tom Sawyer Island on the Rivers of America.', 'Liberty Square', 'mild', 0, 1971, 0, 17.0),

-- Fantasyland
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Seven Dwarfs Mine Train', 'ride_thrill', 'Family coaster through the dwarf mines with swinging cars and a dark-ride show scene.', 'Fantasyland', 'moderate', 38, 2014, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Peter Pan''s Flight', 'ride_dark', 'Hang-glider suspended dark ride soaring over London and Neverland.', 'Fantasyland', 'mild', 0, 1971, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'it''s a small world', 'ride_dark', 'Iconic boat ride through a colorful world of singing dolls representing global unity.', 'Fantasyland', 'mild', 0, 1971, 1, 10.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Under the Sea – Journey of the Little Mermaid', 'ride_dark', 'Omnimover dark ride through Ariels underwater world with musical show scenes.', 'Fantasyland', 'mild', 0, 2012, 0, 6.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Dumbo the Flying Elephant', 'ride_kids', 'Classic spinner ride on Dumbos back with circus-themed interactive play queue.', 'Fantasyland', 'mild', 0, 1971, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'The Many Adventures of Winnie the Pooh', 'ride_dark', 'Hunny-pot ride through the Hundred Acre Wood with Pooh and friends.', 'Fantasyland', 'mild', 0, 1999, 0, 3.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Mad Tea Party', 'ride_kids', 'Classic teacup spinner where riders control their own spin speed.', 'Fantasyland', 'mild', 0, 1971, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Prince Charming Regal Carrousel', 'ride_kids', 'Hand-carved 1917 Cinderella-themed carousel with 90 horses.', 'Fantasyland', 'mild', 0, 1971, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Enchanted Tales with Belle', 'meet_greet', 'Interactive storytelling experience with Belle, Lumiere, and guest participation.', 'Fantasyland', 'none', 0, 2012, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Mickey''s PhilharMagic', 'show_live', '3D musical film with Donald Duck traveling through classic Disney animated sequences.', 'Fantasyland', 'none', 0, 2003, 0, 12.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Ariel''s Grotto', 'meet_greet', 'Meet Ariel in her treasure-filled grotto in mermaid form.', 'Fantasyland', 'none', 0, 2012, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Casey Jr. Splash ''N'' Soak Station', 'play_area', 'Circus-train themed water play area.', 'Fantasyland', 'none', 0, 2012, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Pete''s Silly Sideshow', 'meet_greet', 'Meet Minnie, Daisy, Donald, and Goofy dressed in circus costumes.', 'Fantasyland', 'none', 0, 2012, 0, 10.0),

-- Tomorrowland
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'TRON Lightcycle / Run', 'ride_thrill', 'High-speed motorcycle-style launched coaster inside the digital world of TRON with synchronized music.', 'Tomorrowland', 'extreme', 48, 2023, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Space Mountain', 'ride_thrill', 'Indoor roller coaster in near-complete darkness through the cosmos with sci-fi soundtrack.', 'Tomorrowland', 'high', 44, 1975, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Buzz Lightyear''s Space Ranger Spin', 'ride_dark', 'Interactive shooting dark ride where guests zap Emperor Zurg with laser cannons and track scores.', 'Tomorrowland', 'mild', 0, 1998, 0, 4.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Tomorrowland Speedway', 'ride_kids', 'Kids drive small gas-powered cars around a tracked roadway circuit.', 'Tomorrowland', 'mild', 32, 1971, 0, 4.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Astro Orbiter', 'ride_kids', 'Elevated spinning rocket ride high above Tomorrowland offering panoramic Magic Kingdom views.', 'Tomorrowland', 'moderate', 0, 1974, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Tomorrowland Transit Authority PeopleMover', 'ride_family', 'Elevated tram tour of Tomorrowland providing behind-the-scenes views of Space Mountain and Buzz Lightyear.', 'Tomorrowland', 'mild', 0, 1975, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Walt Disney''s Carousel of Progress', 'show_live', 'Rotating theater showing technological progress through four generations of an American family.', 'Tomorrowland', 'none', 0, 1975, 0, 21.0),
((SELECT id FROM fl_parks WHERE name='Magic Kingdom'), 'Monsters, Inc. Laugh Floor', 'show_live', 'Interactive comedy show where Mike Wazowski tells jokes with live audience participation.', 'Tomorrowland', 'none', 0, 2007, 0, 12.0);


-- ============================================================
-- ATTRACTIONS: EPCOT
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
-- World Celebration
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Spaceship Earth', 'ride_dark', 'Time-travel journey inside the parks iconic geodesic sphere following human communication from cave paintings to the digital age.', 'World Celebration', 'mild', 0, 1982, 1, 16.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Journey of Water, Inspired by Moana', 'exhibit_interactive', 'Interactive water trail where guests play with living water inspired by Moana.', 'World Celebration', 'none', 0, 2023, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Luminous The Symphony of Us', 'show_fireworks', 'Nighttime spectacle with lasers, fireworks, fountains, and original music on World Showcase Lagoon.', 'World Celebration', 'none', 0, 2023, 1, 17.0),

-- World Discovery
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Guardians of the Galaxy: Cosmic Rewind', 'ride_thrill', 'Story-coaster with rotating cars, reverse launch, and 360-degree storytelling set to the Awesome Mix playlist.', 'World Discovery', 'high', 42, 2022, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Mission: SPACE – Orange (Mars)', 'ride_simulator', 'Intense centrifuge-based simulated mission to Mars with G-force effects.', 'World Discovery', 'extreme', 44, 2003, 0, 5.5),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Mission: SPACE – Green (Earth)', 'ride_simulator', 'Milder simulation of Earth orbit without centrifuge spin.', 'World Discovery', 'mild', 40, 2003, 0, 5.5),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Test Track Presented by Chevrolet', 'ride_thrill', 'Design a virtual concept car then ride a test vehicle through high-speed automotive testing at 65 MPH.', 'World Discovery', 'high', 40, 1999, 1, 5.0),

-- World Nature
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Soarin'' Around the World', 'ride_simulator', 'Hang-gliding flight simulation over iconic global landmarks with wind, scents, and sweeping orchestral score.', 'World Nature', 'mild', 40, 2005, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'The Seas with Nemo & Friends', 'ride_dark', 'Dark ride through the underwater world of Finding Nemo ending at a massive 5.7-million-gallon saltwater aquarium.', 'World Nature', 'mild', 0, 2007, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Turtle Talk with Crush', 'show_live', 'Interactive real-time animated show where Crush the sea turtle converses live with audience members.', 'World Nature', 'none', 0, 2004, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Living with the Land', 'ride_family', 'Boat tour through innovative greenhouses showcasing future farming techniques and aquaculture.', 'World Nature', 'mild', 0, 1982, 0, 14.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Awesome Planet', 'show_live', '10-minute film about Earths natural beauty and conservation.', 'World Nature', 'none', 0, 2020, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'SeaBase Aquarium', 'exhibit_animal', '5.7-million-gallon saltwater aquarium with sharks, sea turtles, rays, and thousands of tropical fish.', 'World Nature', 'none', 0, 1986, 0, 25.0),

-- World Showcase
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Frozen Ever After', 'ride_dark', 'Boat voyage through Arendelle with Elsa, Anna, Olaf, and trolls, featuring the hit songs from Frozen.', 'World Showcase - Norway', 'mild', 0, 2016, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Gran Fiesta Tour Starring The Three Caballeros', 'ride_dark', 'Gentle boat tour through Mexico with Donald Duck, Jose Carioca, and Panchito.', 'World Showcase - Mexico', 'mild', 0, 2007, 0, 7.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Remy''s Ratatouille Adventure', 'ride_dark', '4D trackless dark ride shrinking guests to the size of a rat as they scurry through Gusteaus kitchen.', 'World Showcase - France', 'mild', 0, 2021, 1, 4.5),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Reflections of China', 'show_live', '360-degree Circle-Vision film showcasing Chinas landmarks and culture.', 'World Showcase - China', 'none', 0, 2016, 0, 12.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'The American Adventure', 'show_live', 'Audio-Animatronic stage show chronicling American history with Ben Franklin and Mark Twain as narrators.', 'World Showcase - American Adventure', 'none', 0, 1982, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Canada Far and Wide in Circle-Vision 360', 'show_live', 'Updated Circle-Vision film exploring Canadian landscapes and cities.', 'World Showcase - Canada', 'none', 0, 2020, 0, 12.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Impressions de France', 'show_live', 'Classical 18-minute film with sweeping views of Frances landscapes set to French classical music.', 'World Showcase - France', 'none', 0, 1982, 0, 18.0),
((SELECT id FROM fl_parks WHERE name='EPCOT'), 'Beauty and the Beast Sing-Along', 'show_live', 'Animated sing-along short film in the France pavilion with Madame Garderobe.', 'World Showcase - France', 'none', 0, 2020, 0, 15.0);

-- Wait, the France pavilion has two films but I don't want duplicate land area content. Let me leave the film references but note they're in France. Let me check what I have...

-- ============================================================
-- ATTRACTIONS: DISNEY'S HOLLYWOOD STUDIOS
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Star Wars: Rise of the Resistance', 'ride_dark', 'Multi-part dark ride experience with trackless vehicles, walkthrough segments, and a drop escape pod.', 'Star Wars: Galaxy''s Edge', 'moderate', 40, 2019, 1, 18.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Millennium Falcon: Smugglers Run', 'ride_simulator', 'Interactive flight simulator where crews of six pilot, shoot, and engineer the Millennium Falcon.', 'Star Wars: Galaxy''s Edge', 'moderate', 38, 2019, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Savi''s Workshop – Handbuilt Lightsabers', 'exhibit_interactive', 'Build-your-own custom lightsaber experience with a Gatherer guide in a secret workshop.', 'Star Wars: Galaxy''s Edge', 'none', 0, 2019, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Droid Depot', 'exhibit_interactive', 'Build a custom astromech droid unit from BB-series or R-series parts.', 'Star Wars: Galaxy''s Edge', 'none', 0, 2019, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'The Twilight Zone Tower of Terror', 'ride_thrill', 'Drop tower ride set in the haunted Hollywood Tower Hotel with randomized drop sequences.', 'Sunset Boulevard', 'extreme', 40, 1994, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Rock ''n'' Roller Coaster Starring Aerosmith', 'ride_thrill', 'Indoor launched coaster accelerating 0-57 MPH in 2.8 seconds with Aerosmith soundtrack.', 'Sunset Boulevard', 'high', 48, 1999, 1, 1.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Slinky Dog Dash', 'ride_thrill', 'Family launched coaster through Andys backyard on a track made of Tinkertoys and toys.', 'Toy Story Land', 'moderate', 38, 2018, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Toy Story Mania!', 'ride_dark', 'Interactive 4D carnival shooting gallery where riders compete in themed mini-games.', 'Toy Story Land', 'mild', 0, 2008, 1, 5.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Alien Swirling Saucers', 'ride_kids', 'Spinning whip ride themed to the Little Green Aliens from Toy Story.', 'Toy Story Land', 'mild', 32, 2018, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Mickey & Minnie''s Runaway Railway', 'ride_dark', 'Trackless dark ride through a cartoon short where guests step into the screen for a whimsical adventure.', 'Hollywood Boulevard', 'mild', 0, 2020, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Muppet*Vision 3D', 'show_live', '3D film featuring the Muppets in slapstick chaos with in-theater effects and live Audio-Animatronics.', 'Grand Avenue', 'none', 0, 1991, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Beauty and the Beast – Live on Stage', 'show_live', 'Broadway-style condensed stage show of Beauty and the Beast with live performers and choreography.', 'Animation Courtyard', 'none', 0, 1991, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Disney Junior Play & Dance!', 'show_live', 'Interactive show for preschoolers with Disney Junior characters, music, and dance.', 'Animation Courtyard', 'none', 0, 2018, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Lightning McQueen''s Racing Academy', 'show_live', 'Immersive show with a life-size animatronic Lightning McQueen and wraparound screen racing action.', 'Echo Lake', 'none', 0, 2019, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Indiana Jones Epic Stunt Spectacular!', 'show_live', 'Live stunt show recreating iconic scenes from Raiders of the Lost Ark with behind-the-scenes stunt reveals.', 'Echo Lake', 'none', 0, 1989, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'For the First Time in Forever: A Frozen Sing-Along Celebration', 'show_live', 'Comedy stage show retelling Frozen with live performers and audience sing-along.', 'Echo Lake', 'none', 0, 2014, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Star Wars Launch Bay', 'exhibit_interactive', 'Exhibit space with Star Wars movie props, costumes, character meet-and-greets, and replica ships.', 'Animation Courtyard', 'none', 0, 2015, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Hollywood Studios'), 'Fantasmic!', 'show_fireworks', 'Nighttime spectacular with water screens, pyrotechnics, lasers, and Mickey battling Disney villains in his dream.', 'Sunset Boulevard', 'none', 0, 1998, 1, 30.0);


-- ============================================================
-- ATTRACTIONS: DISNEY'S ANIMAL KINGDOM
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Avatar Flight of Passage', 'ride_simulator', '3D flight simulator where guests ride a banshee over the stunning landscape of Pandora.', 'Pandora – The World of Avatar', 'moderate', 44, 2017, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Na''vi River Journey', 'ride_dark', 'Peaceful boat ride through a bioluminescent Pandora rainforest with an animatronic Na''vi Shaman.', 'Pandora – The World of Avatar', 'mild', 0, 2017, 0, 4.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Expedition Everest – Legend of the Forbidden Mountain', 'ride_thrill', 'High-speed coaster through the Himalayas with a Yeti encounter, forward and backward sections.', 'Asia', 'extreme', 44, 2006, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Kali River Rapids', 'ride_water', 'Whitewater raft ride through a threatened jungle with a conservation message and significant splashing.', 'Asia', 'moderate', 38, 1999, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Maharajah Jungle Trek', 'trail', 'Walking trail through ancient ruins with tigers, Komodo dragons, bats, and exotic birds.', 'Asia', 'none', 0, 1999, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Kilimanjaro Safaris', 'ride_family', 'Open-air safari vehicle tour across 110 acres of African savanna with lions, elephants, giraffes, and more.', 'Africa', 'mild', 0, 1998, 1, 22.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Gorilla Falls Exploration Trail', 'trail', 'Walking trail through a research outpost with western lowland gorillas, hippos, and exotic birds.', 'Africa', 'none', 0, 1998, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Festival of the Lion King', 'show_live', 'Broadway-style celebration show with acrobatics, fire dancers, puppetry, and the music of The Lion King.', 'Africa', 'none', 0, 1998, 1, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'DINOSAUR', 'ride_dark', 'Dark thrill ride traveling back in time to rescue an Iguanodon from the asteroid extinction event.', 'DinoLand U.S.A.', 'high', 40, 1998, 0, 3.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'TriceraTop Spin', 'ride_kids', 'Kid-friendly spinner with flying dinosaur vehicles.', 'DinoLand U.S.A.', 'mild', 0, 2002, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'The Boneyard', 'play_area', 'Dinosaur-themed fossil dig playground with slides, bridges, and mammoth skeleton climbing structures.', 'DinoLand U.S.A.', 'none', 0, 1998, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Finding Nemo: The Big Blue… and Beyond!', 'show_live', 'Musical stage show retelling Finding Nemo with live performers, puppets, and original songs.', 'DinoLand U.S.A.', 'none', 0, 2022, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'It''s Tough to be a Bug!', 'show_live', '3D show inside the Tree of Life with Flik from A Bug''s Life using in-theater effects.', 'Discovery Island', 'mild', 0, 1998, 0, 8.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Tree of Life', 'exhibit_art', '145-foot artificial tree with 325 animal carvings in its trunk, the park''s iconic centerpiece.', 'Discovery Island', 'none', 0, 1998, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Discovery Island Trails', 'trail', 'Gentle walking path around the Tree of Life with animal exhibits.', 'Discovery Island', 'none', 0, 1998, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Wilderness Explorers', 'exhibit_interactive', 'Self-guided scavenger hunt activity where kids earn badges learning about animals and conservation.', 'Discovery Island', 'none', 0, 2013, 0, 60.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Animal Kingdom'), 'Oasis Exhibits', 'exhibit_animal', 'Entry garden pathways with anteaters, exotic birds, wallabies, and spoonbills.', 'Oasis', 'none', 0, 1998, 0, 10.0);


-- ============================================================
-- ATTRACTIONS: DISNEY WATER PARKS
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Summit Plummet', 'ride_water', 'One of the worlds tallest free-fall body water slides at 120 feet with a 360-foot near-vertical drop.', NULL, 'extreme', 48, 1995, 1, 0.2),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Slush Gusher', 'ride_water', 'High-speed body slide dropping guests over snow-banked curves and paths.', NULL, 'high', 48, 1995, 0, 0.2),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Teamboat Springs', 'ride_water', 'Family raft ride for up to six riders navigating twisting whitewater on a 1200-foot course.', NULL, 'moderate', 0, 1995, 1, 4.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Runoff Rapids', 'ride_water', 'Three inner-tube slides, including two enclosed and one open-air, accessible by climbing stairs or a chairlift.', NULL, 'moderate', 0, 1995, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Downhill Double Dipper', 'ride_water', 'Side-by-side racing tube slides with a speed timer at the finish line.', NULL, 'high', 48, 1995, 0, 0.3),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Snow Stormers', 'ride_water', 'Three mat slides named after ski courses winding down Mount Gushmore.', NULL, 'moderate', 0, 1995, 0, 0.3),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Tikes Peak', 'play_area', 'Kids water play area with small slides and wading pools designed for toddlers.', NULL, 'mild', 0, 1995, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Ski Patrol Training Camp', 'play_area', 'Interactive water play area for preteens with zip lines, ice flow walkways, and body slides.', NULL, 'moderate', 0, 1995, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Melt-Away Bay', 'ride_water', 'One-acre wave pool at the base of Mount Gushmore with gentle, rolling swells.', NULL, 'mild', 0, 1995, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Blizzard Beach'), 'Cross Country Creek', 'ride_water', 'Lazy river circling the entire park with warm water and scenic views.', NULL, 'mild', 0, 1995, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Crush ''n'' Gusher', 'ride_water', 'Water coaster using water jets to propel rafts uphill and through twisting curves over three tracks.', NULL, 'high', 48, 2005, 1, 1.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Humunga Kowabunga', 'ride_water', 'Five-story, near-vertical enclosed body slide in complete darkness.', NULL, 'extreme', 48, 1989, 0, 0.2),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Storm Slides', 'ride_water', 'Three twisting body slides through the caves of Mount Mayday.', NULL, 'moderate', 0, 1989, 0, 0.3),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Miss Adventure Falls', 'ride_water', 'Family raft ride past animatronic treasure-collecting scenes as you float through an abandoned shipwreck.', NULL, 'moderate', 0, 2017, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Mayday Falls', 'ride_water', 'Whitewater tube ride through a treacherous mountain river.', NULL, 'moderate', 0, 1989, 0, 0.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Keelhaul Falls', 'ride_water', 'A tamer inner-tube slide through tropical foliage.', NULL, 'mild', 0, 1989, 0, 0.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Gangplank Falls', 'ride_water', 'Four-person raft slide navigating twisting volcanic caverns.', NULL, 'mild', 0, 1989, 0, 0.5),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Ketchakiddee Creek', 'play_area', 'Aquatic playground for young children with small slides, fountains, and mini rapids.', NULL, 'mild', 0, 1989, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Typhoon Lagoon Surf Pool', 'ride_water', 'North Americas largest outdoor wave pool generating 6-foot swells every 90 seconds.', NULL, 'moderate', 0, 1989, 1, 30.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Castaway Creek', 'ride_water', 'Scenic lazy river winding through lush tropical landscaping around the entire park.', NULL, 'mild', 0, 1989, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Disney''s Typhoon Lagoon'), 'Shark Reef', 'exhibit_animal', 'Snorkeling pool with tropical fish, rays, and small sharks (snorkel gear provided).', NULL, 'none', 0, 1989, 0, 15.0);


-- ============================================================
-- ATTRACTIONS: UNIVERSAL STUDIOS FLORIDA
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
-- Diagon Alley
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Harry Potter and the Escape from Gringotts', 'ride_thrill', 'Multi-sensory indoor roller coaster through Gringotts bank vaults with Harry, Ron, and Hermione facing Bellatrix and Voldemort.', 'The Wizarding World of Harry Potter – Diagon Alley', 'moderate', 42, 2014, 1, 4.5),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Hogwarts Express – King''s Cross Station', 'ride_family', 'Train journey from London to Hogsmeade with window projection effects showing the Scottish Highlands.', 'The Wizarding World of Harry Potter – Diagon Alley', 'mild', 0, 2014, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Ollivanders Wand Shop', 'exhibit_interactive', 'Interactive wand ceremony where a wand chooses a wizard, performed by an Ollivanders wandkeeper.', 'The Wizarding World of Harry Potter – Diagon Alley', 'none', 0, 2014, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Knockturn Alley', 'exhibit_interactive', 'Dark witchcraft shopping street with Borgin and Burkes shop featuring Death Eater masks and the vanishing cabinet.', 'The Wizarding World of Harry Potter – Diagon Alley', 'none', 0, 2014, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Celestina Warbeck and the Banshees', 'show_live', 'Live musical performance of wizarding world songs in Diagon Alley.', 'The Wizarding World of Harry Potter – Diagon Alley', 'none', 0, 2014, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Tales of Beedle the Bard', 'show_live', 'Puppet show telling wizarding fairy tales using unique stagecraft in Diagon Alley.', 'The Wizarding World of Harry Potter – Diagon Alley', 'none', 0, 2014, 0, 10.0),

-- Production Central / Hollywood
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Despicable Me Minion Mayhem', 'ride_simulator', 'Motion-simulator ride transforming guests into Minions with Gru, the girls, and chaotic Minion antics.', 'Production Central', 'moderate', 40, 2012, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Hollywood Rip Ride Rockit', 'ride_thrill', 'Customizable music roller coaster with a vertical lift, multiple inversions, and on-ride video recording.', 'Production Central', 'extreme', 51, 2009, 1, 1.5),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'TRANSFORMERS: The Ride-3D', 'ride_simulator', 'High-intensity 3D motion simulator with Transformers battling the Decepticons to protect the AllSpark.', 'Production Central', 'moderate', 40, 2013, 1, 4.5),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Universal Orlando''s Horror Make-Up Show', 'show_live', 'Comedy show demonstrating horror movie makeup and special effects techniques.', 'Hollywood', 'none', 0, 1990, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'The Bourne Stuntacular', 'show_live', 'Live stunt show blending stage combat with massive LED screens tracking Jason Bourne chases across global locations.', 'Hollywood', 'none', 0, 2020, 1, 25.0),

-- New York
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Revenge of the Mummy', 'ride_thrill', 'Indoor psychological coaster racing through ancient Egyptian tomb with mummy warriors, scarab beetles, and fire effects.', 'New York', 'high', 48, 2004, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Race Through New York Starring Jimmy Fallon', 'ride_simulator', 'Flying theater race through New York City with Jimmy Fallon, the Roots, and cameo appearances.', 'New York', 'mild', 40, 2017, 0, 6.0),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'The Blues Brothers Show', 'show_live', 'Street performance with Jake and Elwood Blues singing classic R&B numbers.', 'New York', 'none', 0, 1991, 0, 10.0),

-- San Francisco
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Fast & Furious – Supercharged', 'ride_simulator', 'Immersive bus tour into the high-octane world of Fast & Furious with 360-degree screens and practical effects.', 'San Francisco', 'moderate', 40, 2018, 0, 5.0),

-- World Expo
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'MEN IN BLACK Alien Attack', 'ride_dark', 'Interactive dark ride where agents zap aliens with laser guns to earn points across a detailed alien invasion.', 'World Expo', 'mild', 42, 2000, 1, 4.5),

-- Springfield
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'The Simpsons Ride', 'ride_simulator', 'Giant-screen motion simulator racing through Krustyland and Springfield with the Simpson family.', 'Springfield: Home of the Simpsons', 'moderate', 40, 2008, 1, 4.5),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Kang & Kodos'' Twirl ''n'' Hurl', 'ride_kids', 'Classic spinning saucer ride with aliens from The Simpsons telling jokes overhead.', 'Springfield: Home of the Simpsons', 'mild', 0, 2013, 0, 1.5),

-- Woody Woodpecker''s KidZone
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'E.T. Adventure', 'ride_dark', 'Bicycle flying dark ride through the forest to E.T.''s Green Planet aboard iconic bicycle vehicles.', 'Woody Woodpeckers KidZone', 'mild', 34, 1990, 1, 4.5),
((SELECT id FROM fl_parks WHERE name='Universal Studios Florida'), 'Animal Actors On Location!', 'show_live', 'Live animal show demonstrating how animals are trained for movies and TV with audience participation.', 'Woody Woodpeckers KidZone', 'none', 0, 1990, 0, 20.0);


-- ============================================================
-- ATTRACTIONS: ISLANDS OF ADVENTURE
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
-- Marvel Super Hero Island
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The Incredible Hulk Coaster', 'ride_thrill', 'B&M launched coaster with gamma-radiation tunnel launch, zero-G roll, cobra roll, and seven inversions.', 'Marvel Super Hero Island', 'extreme', 54, 1999, 1, 2.25),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The Amazing Adventures of Spider-Man', 'ride_simulator', 'Groundbreaking 3D motion simulator dark ride swinging through New York with Spider-Man battling the Sinister Syndicate.', 'Marvel Super Hero Island', 'moderate', 40, 1999, 1, 4.5),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Doctor Doom''s Fearfall', 'ride_thrill', 'Space shot launch towers shooting riders 185 feet up in the air and back down.', 'Marvel Super Hero Island', 'extreme', 52, 1999, 0, 0.5),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Storm Force Accelatron', 'ride_kids', 'Mutant-power-generating teacup spinner with X-Men theming.', 'Marvel Super Hero Island', 'moderate', 0, 2000, 0, 1.5),

-- Toon Lagoon
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Dudley Do-Right''s Ripsaw Falls', 'ride_water', 'Themed log flume with multiple drops culminating in a 75-foot plunge into a dynamite shack.', 'Toon Lagoon', 'high', 44, 1999, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Popeye & Bluto''s Bilge-Rat Barges', 'ride_water', 'Whitewater rapids raft ride guaranteed to soak riders through twisting flumes and waterfalls.', 'Toon Lagoon', 'high', 42, 1999, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Me Ship, The Olive', 'play_area', 'Three-story interactive playground shaped like Popeye''s ship with water cannons.', 'Toon Lagoon', 'none', 0, 1999, 0, 15.0),

-- Skull Island
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Skull Island: Reign of Kong', 'ride_dark', 'Trackless expedition truck journey through Skull Island with a giant Kong animatronic and 3D screens.', 'Skull Island: Reign of Kong', 'moderate', 36, 2016, 1, 6.0),

-- Jurassic Park
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Jurassic World VelociCoaster', 'ride_thrill', 'Intamin launched coaster reaching 70 MPH with 155-foot top hat, zero-G stall, and near-miss raptor encounters.', 'Jurassic Park', 'extreme', 51, 2021, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Jurassic Park River Adventure', 'ride_water', 'Splashdown boat ride through Jurassic Park culminating in an 85-foot plunge away from a lunging T. rex.', 'Jurassic Park', 'high', 42, 1999, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Pteranodon Flyers', 'ride_kids', 'Suspended family ride where riders glide beneath pteranodon wings over Camp Jurassic.', 'Jurassic Park', 'mild', 56, 1999, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Camp Jurassic', 'play_area', 'Prehistoric-themed playground with caves, rope bridges, lava pit fountains, and slide scrambles.', 'Jurassic Park', 'none', 0, 1999, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Jurassic Park Discovery Center', 'exhibit_interactive', 'Interactive science center where you can see dinosaur DNA being sequenced and a raptor hatching.', 'Jurassic Park', 'none', 0, 1999, 0, 20.0),

-- Wizarding World – Hogsmeade
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Harry Potter and the Forbidden Journey', 'ride_dark', 'Robotic arm dark ride through Hogwarts Castle with Harry Potter, flying past dementors, dragons, and Quidditch.', 'The Wizarding World of Harry Potter – Hogsmeade', 'high', 48, 2010, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Hagrid''s Magical Creatures Motorbike Adventure', 'ride_thrill', 'Story-coaster through the Forbidden Forest with launches, a drop track, and encounters with magical creatures.', 'The Wizarding World of Harry Potter – Hogsmeade', 'high', 48, 2019, 1, 3.5),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Flight of the Hippogriff', 'ride_thrill', 'Family coaster past Hagrid''s hut with views of Hogsmeade and the Forbidden Forest.', 'The Wizarding World of Harry Potter – Hogsmeade', 'moderate', 36, 2010, 0, 1.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Hogwarts Express – Hogsmeade Station', 'ride_family', 'Train journey from Hogsmeade to London/Diagon Alley with window projection effects.', 'The Wizarding World of Harry Potter – Hogsmeade', 'mild', 0, 2014, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Frog Choir', 'show_live', 'Hogwarts student choir performance with croaking frog accompaniment on the bass notes.', 'The Wizarding World of Harry Potter – Hogsmeade', 'none', 0, 2010, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Triwizard Spirit Rally', 'show_live', 'Beauxbatons and Durmstrang student performances with ribbon dancing and martial arts.', 'The Wizarding World of Harry Potter – Hogsmeade', 'none', 0, 2010, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Ollivanders Wand Shop – Hogsmeade', 'exhibit_interactive', 'Second location of the wand ceremony experience where a wand chooses a wizard.', 'The Wizarding World of Harry Potter – Hogsmeade', 'none', 0, 2010, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The Nighttime Lights at Hogwarts Castle', 'show_fireworks', 'Projection mapping show on Hogwarts Castle celebrating each Hogwarts house with music.', 'The Wizarding World of Harry Potter – Hogsmeade', 'none', 0, 2017, 1, 8.0),

-- The Lost Continent
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Poseidon''s Fury', 'exhibit_interactive', 'Walkthrough show through ancient temple chambers with water vortex, fire effects, and battle between Poseidon and Lord Darkennon.', 'The Lost Continent', 'mild', 0, 1999, 0, 15.0),

-- Seuss Landing
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The Cat in the Hat', 'ride_dark', 'Dark ride through the chaos of Dr. Seuss''s classic book with Thing 1 and Thing 2.', 'Seuss Landing', 'mild', 36, 1999, 0, 4.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'The High in the Sky Seuss Trolley Train Ride!', 'ride_kids', 'Elevated monorail with two tracks telling different stories through Seuss Landing.', 'Seuss Landing', 'mild', 36, 2006, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'One Fish, Two Fish, Red Fish, Blue Fish', 'ride_kids', 'Spinning ride where following the rhyme determines whether riders get splashed.', 'Seuss Landing', 'mild', 0, 1999, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'Caro-Seuss-el', 'ride_kids', 'Whimsical carousel with creatures from Dr. Seuss''s imagination instead of traditional horses.', 'Seuss Landing', 'mild', 0, 1999, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Universal Islands of Adventure'), 'If I Ran the Zoo', 'play_area', 'Interactive Dr. Seuss-themed water play and exploration area.', 'Seuss Landing', 'none', 0, 1999, 0, 15.0);


-- ============================================================
-- ATTRACTIONS: SEaworld ORLANDO
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Mako', 'ride_thrill', 'B&M hypercoaster reaching 73 MPH with a 200-foot drop over a shipwreck-themed course, Orlandos tallest and fastest coaster.', NULL, 'extreme', 54, 2016, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Manta', 'ride_thrill', 'Flying coaster where riders face down like a manta ray gliding through water, with four inversions and a wing dip.', NULL, 'extreme', 54, 2009, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Kraken Unleashed', 'ride_thrill', 'Floorless B&M coaster with seven inversions, subterranean tunnels, and virtual reality option.', NULL, 'extreme', 54, 2000, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Pipeline: The Surf Coaster', 'ride_thrill', 'Standing coaster simulating surfing with seats that rise and fall matching wave pattern, launched at 60 MPH.', NULL, 'extreme', 54, 2023, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Ice Breaker', 'ride_thrill', 'Quad-launched coaster with a 93-foot spike, 100-degree beyond-vertical drop, and airtime hill.', NULL, 'high', 48, 2022, 1, 1.5),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Journey to Atlantis', 'ride_water', 'Hybrid water coaster/dark ride through the lost city of Atlantis with two drops including a 60-foot plunge.', NULL, 'moderate', 42, 1998, 1, 6.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Infinity Falls', 'ride_water', 'Whitewater raft ride through a jungle river with a record-setting 40-foot vertical elevator lift and drop.', NULL, 'high', 42, 2018, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Empire of the Penguin', 'ride_dark', 'Trackless dark ride through Antarctica with live penguin exhibit at the end, choose mild or wild ride experience.', NULL, 'mild', 0, 2013, 0, 6.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Antarctica: Empire of the Penguin', 'exhibit_animal', 'Walkthrough penguin colony kept at 30 degrees with five penguin species in a multi-level habitat.', NULL, 'none', 0, 2013, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Shark Encounter', 'exhibit_animal', 'Walkthrough tunnel through a 700,000-gallon shark habitat with sharks, rays, and predatory fish.', NULL, 'none', 0, 2007, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Dolphin Cove', 'exhibit_animal', 'Interactive bottlenose dolphin habitat with underwater viewing and scheduled feeding times.', NULL, 'none', 0, 1990, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Dolphin Adventures', 'show_live', 'Live dolphin show with acrobatics, education, and bird flight elements.', NULL, 'none', 0, 1973, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Orca Encounter', 'show_live', 'Educational presentation showcasing orca natural behaviors in a stadium with a massive screen backdrop.', NULL, 'none', 0, 2017, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Sea Lion & Otter Spotlight', 'show_live', 'Comedic sea lion and otter show with tricks and conservation messaging.', NULL, 'none', 0, 1973, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Stingray Lagoon', 'exhibit_animal', 'Touch tank where guests can feed and pet rays as they glide past.', NULL, 'none', 0, 2002, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Manatee Rehabilitation Area', 'exhibit_animal', 'Viewing area of rescued manatees being rehabilitated for return to the wild.', NULL, 'none', 0, 1976, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Wild Arctic', 'exhibit_animal', 'Exhibit with beluga whales, walruses, and harbor seals in a simulated Arctic research station.', NULL, 'none', 0, 1995, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'TurtleTrek', 'exhibit_animal', 'Sea turtle and manatee exhibit with a 360-degree dome theater show.', NULL, 'none', 0, 2012, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Flamingo Cove', 'exhibit_animal', 'Open habitat with Chilean and American flamingos.', NULL, 'none', 0, 2012, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Sesame Street Land', 'land_area', 'Interactive Sesame Street-themed kids area with six rides and a splash pad.', NULL, 'none', 0, 2019, 0, 60.0);

-- Sesame Street Land rides
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Super Grover''s Box Car Derby', 'ride_kids', 'Small family coaster with Grover driving a boxcar through Sesame Street.', 'Sesame Street Land', 'mild', 38, 2019, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Abby''s Flower Tower', 'ride_kids', 'Family drop tower with colorful flowers ascending to views of the area.', 'Sesame Street Land', 'mild', 42, 2019, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Elmo''s Choo Choo Train', 'ride_kids', 'Gentle train ride for toddlers with Elmo as conductor.', 'Sesame Street Land', 'mild', 0, 2019, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Big Bird''s Twirl ''n'' Whirl', 'ride_kids', 'Spinning teacup-style ride with Big Bird and his nest.', 'Sesame Street Land', 'mild', 0, 2019, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Cookie Drop!', 'ride_kids', 'Cookie Monster-themed mini drop tower for preschoolers.', 'Sesame Street Land', 'mild', 36, 2019, 0, 1.0),
((SELECT id FROM fl_parks WHERE name='SeaWorld Orlando'), 'Rubber Duckie Water Works', 'play_area', 'Sprayground splash pad with Big Bird umbrella fountains and rubber duckie theming.', 'Sesame Street Land', 'none', 0, 2019, 0, 20.0);


-- ============================================================
-- ATTRACTIONS: BUSCH GARDENS TAMPA BAY
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Iron Gwazi', 'ride_thrill', 'RMC hybrid coaster at 206 feet tall reaching 76 MPH with a 91-degree drop and 12 airtime moments.', NULL, 'extreme', 48, 2022, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'SheiKra', 'ride_thrill', 'Dive coaster with a 200-foot vertical face, 90-degree drop, splashdown, and floorless cars.', NULL, 'extreme', 54, 2005, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Montu', 'ride_thrill', 'Inverted coaster set in an Egyptian archaeological dig with seven inversions and pit trenches.', NULL, 'extreme', 54, 1996, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Kumba', 'ride_thrill', 'Classic B&M sit-down coaster featuring a 135-foot vertical loop, cobra roll, and interlocking corkscrews.', NULL, 'extreme', 54, 1993, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Cheetah Hunt', 'ride_thrill', 'Multi-launch LSM coaster reaching 60 MPH through cheetah habitat with a figure-8 inversion and overbanked turns.', NULL, 'high', 48, 2011, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Cobra''s Curse', 'ride_thrill', 'Spinning family coaster with a 70-foot vertical lift, forward, backward, and free-spinning sections.', NULL, 'moderate', 42, 2016, 1, 3.5),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Tigris', 'ride_thrill', 'Premier Sky Rocket II triple-launch coaster with a 150-foot barrel roll twist and 60 MPH launch.', NULL, 'extreme', 54, 2019, 0, 1.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Phoenix Rising', 'ride_thrill', 'B&M family inverted coaster swinging over the Serengeti Plain with animal views, reaching 44 MPH.', NULL, 'moderate', 42, 2024, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Scorpion', 'ride_thrill', 'Classic Schwarzkopf silver arrow looper coaster from 1980 with a 60-foot loop.', NULL, 'high', 42, 1980, 0, 1.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'SandSerpent', 'ride_thrill', 'Wild mouse coaster with spinning cars and tight hairpin turns.', NULL, 'moderate', 42, 1996, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Air Grover', 'ride_kids', 'Junior coaster themed to Grover from Sesame Street in the Sesame Street Safari of Fun area.', NULL, 'moderate', 38, 2010, 0, 1.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Congo River Rapids', 'ride_water', 'Whitewater rafting ride through the Congo themed area with waterfalls and turbulent currents.', NULL, 'high', 42, 1982, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Stanley Falls Flume', 'ride_water', 'Classic log flume ride with a 45-foot final splashdown into the Elephant Connection viewing area.', NULL, 'moderate', 42, 1973, 0, 3.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Serengeti Express Railroad', 'ride_family', 'Steam train circling the Serengeti Plain with views of free-roaming giraffes, zebras, and antelopes.', NULL, 'mild', 0, 1971, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Serengeti Safari', 'tour', 'Behind-the-scenes open truck tour across the Serengeti Plain where guests hand-feed giraffes.', NULL, 'mild', 0, 1980, 1, 30.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Edge of Africa', 'exhibit_animal', 'Walking tour through African habitats with lions, hyenas, meerkats, and hippopotamuses.', NULL, 'none', 0, 1997, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Myombe Reserve', 'exhibit_animal', 'Great ape exhibit with western lowland gorillas and chimpanzees in a natural jungle habitat.', NULL, 'none', 0, 1992, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Cheetah Run', 'exhibit_animal', 'Cheetah habitat with daily speed demonstrations showing a cheetah sprinting at full speed.', NULL, 'none', 0, 2011, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Lory Landing', 'exhibit_animal', 'Free-flight aviary where guests feed nectar to colorful lorikeets that land on their hands.', NULL, 'none', 0, 1990, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Jungala', 'play_area', 'Multi-level family area with Bengal tiger viewing, orangutans, and an interactive water play zone.', NULL, 'none', 0, 2008, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Busch Gardens Tampa Bay'), 'Elephant Presentation', 'show_live', 'Educational presentation with African elephants demonstrating natural behaviors.', NULL, 'none', 0, 1973, 0, 15.0);


-- ============================================================
-- ATTRACTIONS: LEGOLAND FLORIDA
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'The Dragon', 'ride_thrill', 'Indoor/outdoor family coaster with a dark-ride section through a LEGO castle and a moderate coaster finish.', NULL, 'moderate', 40, 2004, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'LEGO Technic Coaster / Test Track', 'ride_thrill', 'Wild mouse coaster with sharp turns and a 40-foot drop near the parks front entrance.', NULL, 'moderate', 42, 2011, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Flying School', 'ride_thrill', 'Suspended family coaster where riders legs dangle below mimicking the Wright Brothers flyer.', NULL, 'moderate', 44, 2011, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Coastersaurus', 'ride_thrill', 'Junior wooden coaster winding through a prehistoric LEGO dinosaur jungle with gentle dips and turns.', NULL, 'moderate', 42, 2011, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'The Great LEGO Race', 'ride_simulator', 'VR-enhanced indoor coaster racing through LEGO worlds including pirates, space, and fantasy.', NULL, 'moderate', 42, 2017, 1, 3.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Lost Kingdom Adventure', 'ride_dark', 'Interactive dark ride where guests shoot laser blasters at LEGO targets in an Egyptian tomb.', NULL, 'mild', 0, 2011, 0, 4.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Boating School', 'ride_kids', 'Kids drive their own LEGO-themed boats on a water track, earning a drivers license at the end.', NULL, 'mild', 34, 2011, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Ford Driving School', 'ride_kids', 'Kids navigate their own electric LEGO-styled car through a mini road course with traffic signs and lights.', NULL, 'mild', 0, 2011, 0, 7.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Ford Jr. Driving School', 'ride_kids', 'Smaller driving course for toddlers ages 3-5 with parents able to help steer.', NULL, 'mild', 0, 2011, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Mia''s Riding Adventure', 'ride_kids', 'Disk-O ride with a LEGO Friends theme spinning and rocking guests along a curved track.', NULL, 'moderate', 42, 2015, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Beetle Bounce', 'ride_kids', 'Kids drop tower with LEGO bumblebees that gently bounce riders up and down 15 feet.', NULL, 'mild', 36, 2011, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'DUPLO Train', 'ride_kids', 'Gentle train ride through a colorful DUPLO garden, perfect for toddlers and preschoolers.', NULL, 'mild', 0, 2011, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'DUPLO Playtown', 'play_area', 'Interactive playground with oversized DUPLO bricks, slides, and a small airplane ride.', NULL, 'none', 0, 2011, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Merlin''s Challenge', 'ride_kids', 'Small indoor family coaster themed to Merlin the wizard, ideal for first-time coaster riders.', NULL, 'mild', 36, 2011, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'MINILAND USA', 'exhibit_art', 'Incredible miniature LEGO recreations of US landmarks including Las Vegas strip, Washington DC, Kennedy Space Center, and Florida.', NULL, 'none', 0, 2011, 1, 30.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Pirate River Quest', 'ride_water', 'Outdoor boat ride through LEGO pirate scenes where guests use water cannons to battle pirate foes.', NULL, 'mild', 0, 2011, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Cypress Gardens', 'garden', 'Preserved section of the original Cypress Gardens with 100-year-old trees and southern botanical beauty.', NULL, 'none', 0, 1936, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Island in the Sky', 'ride_family', '300-foot rotating platform ride providing panoramic views of the park and surrounding lakes.', NULL, 'mild', 0, 2011, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Pharaoh''s Revenge', 'play_area', 'Indoor playground in a Pharaohs tomb where kids shoot soft foam balls from air cannons.', NULL, 'none', 0, 2011, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'NINJAGO The Ride', 'ride_dark', 'Interactive dark ride where guests use ninja hand gestures to throw fire, lightning, and ice at enemy screens.', NULL, 'mild', 0, 2017, 1, 4.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), 'Pirate''s Cove Live Water Ski Show', 'show_live', 'Live water ski stunt show with LEGO pirate characters performing tricks and comedy on the lake.', NULL, 'none', 0, 2011, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='LEGOLAND Florida'), '4D Theater', 'show_live', 'Cinema showing rotating LEGO 3D/4D films with wind, water, and bubble effects.', NULL, 'none', 0, 2011, 0, 15.0);


-- ============================================================
-- ATTRACTIONS: GATORLAND
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Screamin'' Gator Zipline', 'ride_thrill', '1,200-foot zip line over alligator breeding marsh with 65-foot towers and panoramic gator views.', NULL, 'high', 48, 2011, 1, 30.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Stompin'' Gator Off-Road Adventure', 'ride_family', 'Monster custom vehicle tour through rugged gator territory with bumpy terrain and close encounters.', NULL, 'moderate', 36, 2017, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Alligator Breeding Marsh', 'exhibit_animal', 'Expansive breeding marsh with hundreds of adult alligators visible from an observation tower walkway.', NULL, 'none', 0, 1949, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Gator Jumparoo Show', 'show_live', 'Live feeding show where alligators leap several feet out of the water to snatch food.', NULL, 'none', 0, 1949, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Gator Wrestlin'' Show', 'show_live', 'Alligator handling show with trainers demonstrating capture techniques and gator anatomy in the wrestling pit.', NULL, 'none', 0, 1960, 1, 15.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Up-Close Encounters Show', 'show_live', 'Interactive show with snakes, spiders, and other reptiles for brave guests to touch.', NULL, 'none', 0, 1990, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Very Merry Aviary', 'exhibit_animal', 'Free-flight bird aviary with hundreds of budgies that land on guests who offer seed sticks.', NULL, 'none', 0, 2015, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Panther Springs', 'exhibit_animal', 'Florida panther and bobcat viewing habitat.', NULL, 'none', 0, 2012, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Gatorland'), 'Swamp Walk', 'trail', 'Boardwalk nature trail through a natural cypress swamp ecosystem.', NULL, 'none', 0, 1949, 0, 20.0);


-- ============================================================
-- ATTRACTIONS: KENNEDY SPACE CENTER
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Space Shuttle Atlantis', 'exhibit_science', 'Display of the Space Shuttle Atlantis with 60 interactive exhibits and a ride simulating the shuttle launch experience.', NULL, 'none', 0, 2013, 1, 60.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Shuttle Launch Experience', 'ride_simulator', 'Motion simulator replicating the vertical launch and 17,500 MPH orbit insertion of a Space Shuttle launch.', NULL, 'moderate', 44, 2007, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Saturn V Center', 'exhibit_science', 'Home to one of three remaining Saturn V moon rockets suspended horizontally, with Apollo artifacts and mission simulation.', NULL, 'none', 0, 1996, 1, 60.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Heroes & Legends', 'exhibit_science', 'Holographic show celebrating the pioneers of space exploration with the US Astronaut Hall of Fame.', NULL, 'none', 0, 2016, 0, 45.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Gateway: The Deep Space Launch Complex', 'exhibit_science', 'Exhibit exploring the future of space travel with SpaceX Falcon 9 booster, Blue Origin, and flight simulator.', NULL, 'none', 0, 2022, 1, 45.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Apollo/Saturn V Center Moon Rock', 'exhibit_science', 'Touch an actual moon rock brought back by Apollo 17 astronauts.', NULL, 'none', 0, 1996, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Astronaut Encounter', 'meet_greet', 'Live Q&A presentations with veteran NASA astronauts who share their spaceflight experiences.', NULL, 'none', 0, 2000, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'KSC Bus Tour', 'tour', 'Behind-the-scenes bus tour of restricted areas including the Vehicle Assembly Building and launch pads.', NULL, 'none', 0, 1967, 1, 120.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Apollo 8 Firing Room', 'show_live', 'Recreated Apollo launch firing room with actual consoles showing the historic first lunar mission countdown.', NULL, 'none', 0, 2008, 0, 15.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'IMAX Theater', 'show_live', 'Two giant IMAX screens showing space exploration documentaries.', NULL, 'none', 0, 1984, 0, 45.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'Rocket Garden', 'exhibit_science', 'Outdoor garden displaying historic rockets from Mercury, Gemini, and Apollo programs including a Redstone and Atlas.', NULL, 'none', 0, 1967, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='Kennedy Space Center Visitor Complex'), 'U.S. Astronaut Hall of Fame', 'exhibit_science', 'Hall of Fame honoring American astronauts with their personal memorabilia and mission artifacts.', NULL, 'none', 0, 2016, 0, 30.0);


-- ============================================================
-- ATTRACTIONS: EPIC UNIVERSE (Key Rides)
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Stardust Racers', 'ride_thrill', 'Dual-launched racing coaster in Celestial Park with two tracks of inversions and near-miss effects at 62 MPH.', 'Celestial Park', 'extreme', 48, 2025, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Constellation Carousel', 'ride_family', 'Grand celestial-themed carousel as the centerpiece of Celestial Park with constellations and starry lights.', 'Celestial Park', 'mild', 0, 2025, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Mario Kart: Bowser''s Challenge', 'ride_dark', 'Augmented-reality racing dark ride through Bowsers Castle with AR visors showing targets and scoring.', 'Super Nintendo World', 'moderate', 40, 2025, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Mine-Cart Madness', 'ride_thrill', 'Donkey Kong coaster with a unique track-jumping mechanism where the cart appears to leap gaps in the rail.', 'Super Nintendo World', 'moderate', 40, 2025, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Yoshi''s Adventure', 'ride_family', 'Gentle omnimover ride on Yoshis back through Mushroom Kingdom landscapes with interactive features.', 'Super Nintendo World', 'mild', 36, 2025, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Harry Potter and the Battle at the Ministry', 'ride_dark', 'Lift-based dark ride through the British Ministry of Magic using new motion base technology through various magical chambers.', 'The Wizarding World of Harry Potter – Ministry of Magic', 'moderate', 40, 2025, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Hiccup''s Wing Gliders', 'ride_thrill', 'Family launched coaster soaring with dragons over the Isle of Berk with animatronic dragon encounters.', 'How to Train Your Dragon – Isle of Berk', 'moderate', 40, 2025, 1, 2.5),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Fyre Drill', 'ride_water', 'Interactive boat ride on Berk where Viking teams shoot water cannons at fire targets.', 'How to Train Your Dragon – Isle of Berk', 'mild', 0, 2025, 0, 5.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Dragon Racer''s Rally', 'ride_thrill', 'Dual swing ride where Vikings train their dragons on two giant swinging arms.', 'How to Train Your Dragon – Isle of Berk', 'high', 48, 2025, 0, 1.5),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Monsters Unchained: The Frankenstein Experiment', 'ride_dark', 'Advanced KUKA arm dark ride through Dr. Frankenstein''s laboratory encountering classic Universal Monsters.', 'Dark Universe', 'high', 48, 2025, 1, 4.0),
((SELECT id FROM fl_parks WHERE name='Universal Epic Universe'), 'Curse of the Werewolf', 'ride_thrill', 'Spinning family coaster in the Dark Universe village with a werewolf transformation theme.', 'Dark Universe', 'moderate', 42, 2025, 0, 2.0);


-- ============================================================
-- ATTRACTIONS: AQUATICA ORLANDO
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Dolphin Plunge', 'ride_water', 'Body slide that passes through a clear tube within a Commersons dolphin habitat.', NULL, 'high', 48, 2008, 1, 0.3),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Ihu''s Breakaway Falls', 'ride_water', 'The tallest multi-drop tower water slide in Florida, dropping through trapdoors from 80 feet.', NULL, 'extreme', 48, 2014, 1, 0.3),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Taumata Racer', 'ride_water', 'Eight-lane racing mat slide where riders compete head-first on a steep drop.', NULL, 'high', 42, 2008, 0, 0.3),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Omaka Rocka', 'ride_water', 'Bowl slide where riders careen up and down funnel walls with zero-gravity sensations.', NULL, 'high', 42, 2010, 0, 0.3),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Riptide Race', 'ride_water', 'Dueling racer slides where two rafts compete side by side through enclosed and open flumes.', NULL, 'moderate', 42, 2021, 0, 0.5),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Ray Rush', 'ride_water', 'Three-person raft slide with a massive water sphere, enclosed turns, and a splashdown wall.', NULL, 'moderate', 42, 2018, 0, 1.0),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Whanau Way', 'ride_water', 'Four-lane family raft slides with dual-winding enclosed and open tubes.', NULL, 'moderate', 0, 2008, 0, 0.5),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Kata''s Kookaburra Cove', 'play_area', 'Kids area with small slides, wading pools, and zero-depth entry splash pads.', NULL, 'mild', 0, 2018, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Walkabout Waters', 'play_area', 'Large multi-level interactive water playground with a giant tipping bucket and multiple slides.', NULL, 'mild', 0, 2008, 0, 25.0),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Cutback Cove and Big Surf Shores', 'ride_water', 'Dual side-by-side wave pools - one with gentle waves, one with intense surf swells.', NULL, 'moderate', 0, 2008, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Roa''s Rapids', 'ride_water', 'Fast-moving action river with varying depths and no tubes required - a thrilling swim-through current.', NULL, 'moderate', 0, 2008, 1, 10.0),
((SELECT id FROM fl_parks WHERE name='Aquatica Orlando'), 'Loggerhead Lane', 'ride_water', 'Slow-moving lazy river with Commerson''s dolphin viewing into the habitat.', NULL, 'mild', 0, 2008, 0, 20.0);


-- ============================================================
-- ATTRACTIONS: DISCOVERY COVE
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'Dolphin Lagoon', 'exhibit_animal', 'Deepwater dolphin swimming encounter where guests interact one-on-one with bottlenose dolphins.', NULL, 'mild', 0, 2000, 1, 30.0),
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'The Grand Reef', 'exhibit_animal', 'Massive saltwater reef for snorkeling with thousands of tropical fish, rays, and reef sharks behind glass.', NULL, 'mild', 0, 2011, 1, 60.0),
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'Serenity Bay', 'exhibit_animal', 'Shallow snorkeling lagoon with cownose rays and gentle tropical fish.', NULL, 'mild', 0, 2008, 0, 30.0),
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'Explorer''s Aviary', 'exhibit_animal', 'Free-flight aviary where guests hand-feed exotic birds including toucans and parrots.', NULL, 'mild', 0, 2000, 1, 20.0),
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'Freshwater Oasis', 'exhibit_animal', 'Shallow warm spring-fed pool with otters and marmosets in a lush rainforest setting.', NULL, 'mild', 0, 2012, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'Wind-Away River', 'ride_water', 'Lazy river winding through the tropical landscape past beaches, waterfalls, and animal exhibits.', NULL, 'mild', 0, 2000, 0, 20.0),
((SELECT id FROM fl_parks WHERE name='Discovery Cove'), 'Flamingo Point', 'exhibit_animal', 'Flamingo wading habitat where guests can observe these iconic pink birds up close.', NULL, 'mild', 0, 2014, 0, 10.0);


-- ============================================================
-- ATTRACTIONS: FUN SPOT AMERICA PARKS
-- ============================================================
INSERT OR IGNORE INTO fl_attractions (park_id, name, attraction_type, description, land_area, thrill_level, height_requirement_inches, opening_year, is_signature, duration_minutes) VALUES
-- Fun Spot Orlando
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Orlando'), 'White Lightning', 'ride_thrill', 'Wooden coaster with over 2,000 feet of track, steep drops, and airtime moments at 48 MPH.', NULL, 'high', 48, 2013, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Orlando'), 'Freedom Flyer', 'ride_thrill', 'Family inverted steel coaster swinging through banked turns at 34 MPH.', NULL, 'moderate', 44, 2013, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Orlando'), 'SkyCoaster', 'ride_thrill', '250-foot swing experience where riders are hoisted then released in a pendulum arc at 80 MPH.', NULL, 'extreme', 48, 2013, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Orlando'), 'Gator Spot', 'exhibit_animal', 'Gator exhibit within the park featuring adult alligators in a partnership with Gatorland.', NULL, 'none', 0, 2015, 0, 10.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Orlando'), 'Multi-Level Go-Kart Tracks', 'ride_thrill', 'Four unique multi-level go-kart tracks including the Vortex with banked turns and Conquest with spiral climbs.', NULL, 'moderate', 58, 1997, 1, 5.0),
-- Fun Spot Kissimmee
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Kissimmee'), 'Mine Blower', 'ride_thrill', 'Wooden coaster with a 360-degree barrel roll inversion at the top of an 80-foot drop reaching 48 MPH.', NULL, 'extreme', 48, 2017, 1, 2.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Kissimmee'), 'Rockstar Coaster', 'ride_thrill', 'Hurricane Model roller coaster with a vertical loop, multiple inversions, and 55 MPH speeds.', NULL, 'extreme', 48, 2011, 0, 2.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Kissimmee'), 'World''s Tallest SkyCoaster', 'ride_thrill', 'The tallest SkyCoaster in the world at 300 feet with 65 MPH free-fall swing.', NULL, 'extreme', 48, 2013, 1, 5.0),
((SELECT id FROM fl_parks WHERE name='Fun Spot America – Kissimmee'), 'Quad Helix Go-Kart Track', 'ride_thrill', 'Multi-level elevated go-kart track with spiraling climbs and banked turns.', NULL, 'moderate', 58, 2007, 1, 5.0);


-- Now let me create views for easy querying
CREATE VIEW IF NOT EXISTS v_florida_theme_parks AS
SELECT id, name, category, city, region, parent_company, opening_year, description
FROM fl_parks
WHERE category IN ('theme_park', 'water_park')
ORDER BY parent_company, name;

CREATE VIEW IF NOT EXISTS v_florida_zoos_aquariums AS
SELECT id, name, category, city, region, opening_year, description
FROM fl_parks
WHERE category IN ('zoo_aquarium', 'nature_park', 'garden')
ORDER BY region, name;

CREATE VIEW IF NOT EXISTS v_florida_museums AS
SELECT id, name, category, city, region, opening_year, description
FROM fl_parks
WHERE category IN ('museum', 'historic_site')
ORDER BY region, name;

CREATE VIEW IF NOT EXISTS v_park_attractions_by_thrill AS
SELECT p.name AS park_name, a.name AS attraction_name, a.attraction_type, a.thrill_level, a.height_requirement_inches, a.is_signature
FROM fl_parks p
JOIN fl_attractions a ON p.id = a.park_id
ORDER BY CASE a.thrill_level
  WHEN 'extreme' THEN 1
  WHEN 'high' THEN 2
  WHEN 'moderate' THEN 3
  WHEN 'mild' THEN 4
  WHEN 'none' THEN 5
END, p.name, a.name;

CREATE VIEW IF NOT EXISTS v_signature_attractions AS
SELECT p.name AS park_name, a.name AS attraction_name, a.attraction_type, a.thrill_level, a.land_area
FROM fl_parks p
JOIN fl_attractions a ON p.id = a.park_id
WHERE a.is_signature = 1
ORDER BY p.name, a.name;

CREATE VIEW IF NOT EXISTS v_orlando_attractions_summary AS
SELECT p.name AS park_name, p.category, p.parent_company,
  COUNT(a.id) AS total_attractions,
  SUM(CASE WHEN a.is_signature = 1 THEN 1 ELSE 0 END) AS signature_count
FROM fl_parks p
LEFT JOIN fl_attractions a ON p.id = a.park_id
WHERE p.region = 'Orlando'
GROUP BY p.id
ORDER BY p.parent_company, p.name;

SELECT 'Database populated successfully' AS status;