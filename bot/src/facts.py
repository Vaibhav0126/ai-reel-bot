from __future__ import annotations

from typing import Any

# Curiosity facts. Each reel is 5–6 beats totaling ~80–100 spoken words (~30 seconds).
FACTS: list[dict[str, Any]] = [
    {
        "id": "octopus_three_hearts",
        "category": "animals",
        "title": "octopuses have three hearts",
        "beats": [
            {
                "spoken": "Do you know octopuses have three hearts?",
                "caption": "three hearts",
                "image_prompt": "cute cartoon octopus with three small red hearts floating beside it",
            },
            {
                "spoken": "Two pump blood to the gills. One pumps blood to the rest of the body.",
                "caption": "two for gills",
                "image_prompt": "simple cartoon octopus gills with two tiny hearts pumping",
            },
            {
                "spoken": "When it swims, the body heart actually stops. That is why they prefer crawling.",
                "caption": "heart stops swimming",
                "image_prompt": "cartoon octopus walking on ocean floor instead of swimming",
            },
            {
                "spoken": "Blue blood, three hearts, nine brains. Ocean goblin energy.",
                "caption": "blue blood",
                "image_prompt": "cartoon drop of blue blood next to a tiny octopus",
            },
        ],
    },
    {
        "id": "crows_remember_faces",
        "category": "animals",
        "title": "crows remember faces",
        "beats": [
            {
                "spoken": "Do you know crows can remember a human face for years?",
                "caption": "they remember you",
                "image_prompt": "cartoon crow staring at a simple human face mask",
            },
            {
                "spoken": "If you were mean, they tell their friends. The whole flock can hold a grudge.",
                "caption": "they tell friends",
                "image_prompt": "three cartoon crows whispering together on a wire",
            },
            {
                "spoken": "Be nice and they may even bring you shiny gifts.",
                "caption": "shiny gifts",
                "image_prompt": "cartoon crow dropping a shiny bottle cap as a gift",
            },
            {
                "spoken": "Never underestimate a bird with a vendetta.",
                "caption": "do not mess",
                "image_prompt": "cartoon crow giving a side-eye look",
            },
        ],
    },
    {
        "id": "sharks_older_than_trees",
        "category": "animals",
        "title": "sharks are older than trees",
        "beats": [
            {
                "spoken": "Do you know sharks are older than trees?",
                "caption": "older than trees",
                "image_prompt": "cartoon shark swimming past a tiny cartoon tree",
            },
            {
                "spoken": "Sharks showed up around four hundred million years ago. Trees came later.",
                "caption": "400 million years",
                "image_prompt": "simple prehistoric cartoon ocean with a primitive shark",
            },
            {
                "spoken": "They survived ice ages, extinction waves, and still look like a warning sticker.",
                "caption": "still here",
                "image_prompt": "cartoon shark silhouette like a warning sign",
            },
            {
                "spoken": "The ocean had apex predators before forests even existed.",
                "caption": "before forests",
                "image_prompt": "empty land with no trees next to a cartoon ocean shark",
            },
        ],
    },
    {
        "id": "axolotl_regrow",
        "category": "animals",
        "title": "axolotls can regenerate",
        "beats": [
            {
                "spoken": "Do you know axolotls can grow back entire limbs?",
                "caption": "grow limbs back",
                "image_prompt": "cute cartoon pink axolotl smiling",
            },
            {
                "spoken": "Legs, tails, parts of the heart and even bits of the brain. No scar drama.",
                "caption": "heart and brain",
                "image_prompt": "cartoon axolotl with a tiny regenerated glowing limb",
            },
            {
                "spoken": "Scientists study them hoping humans can steal that trick someday.",
                "caption": "science wants this",
                "image_prompt": "cartoon microscope looking at a smiling axolotl",
            },
            {
                "spoken": "Baby-faced salamander. Secret superhero.",
                "caption": "secret superhero",
                "image_prompt": "cartoon axolotl wearing a tiny superhero cape",
            },
        ],
    },
    {
        "id": "goat_pupils",
        "category": "animals",
        "title": "goats have rectangle pupils",
        "beats": [
            {
                "spoken": "Do you know goat pupils are rectangles, not circles?",
                "caption": "rectangle eyes",
                "image_prompt": "cartoon goat face with horizontal rectangle pupils",
            },
            {
                "spoken": "That shape gives them almost panoramic vision to spot predators.",
                "caption": "panoramic vision",
                "image_prompt": "cartoon wide landscape seen through goat eyes",
            },
            {
                "spoken": "When they put their head down to eat, the pupils rotate to stay level.",
                "caption": "pupils rotate",
                "image_prompt": "cartoon goat grazing with level rectangle pupils",
            },
            {
                "spoken": "Nature really said: install a security camera on a lawnmower.",
                "caption": "living camera",
                "image_prompt": "cartoon goat with a tiny security camera on its head",
            },
        ],
    },
    {
        "id": "wombat_cubes",
        "category": "animals",
        "title": "wombats poop cubes",
        "beats": [
            {
                "spoken": "Do you know wombats poop in cubes?",
                "caption": "cube poop",
                "image_prompt": "cartoon wombat next to a few neat brown cubes",
            },
            {
                "spoken": "The cubes stack so they can mark territory without rolling downhill.",
                "caption": "they stack",
                "image_prompt": "cartoon cube poops stacked on a hillside that does not roll",
            },
            {
                "spoken": "Their intestines vary in stiffness. Geometry as a flex.",
                "caption": "geometry flex",
                "image_prompt": "simple cartoon intestine making cube shapes",
            },
            {
                "spoken": "Nature invented Minecraft droppings first.",
                "caption": "minecraft irl",
                "image_prompt": "cartoon wombat proud of a tiny cube tower",
            },
        ],
    },
    {
        "id": "honey_never_spoils",
        "category": "food",
        "title": "honey does not spoil",
        "beats": [
            {
                "spoken": "Do you know honey basically never spoils?",
                "caption": "never spoils",
                "image_prompt": "cartoon jar of golden honey with a bee",
            },
            {
                "spoken": "Low water, high sugar, and a little hydrogen peroxide. Bacteria hate that combo.",
                "caption": "bacteria hate it",
                "image_prompt": "cartoon bacteria running away from a honey jar",
            },
            {
                "spoken": "Archaeologists found thousand-year-old honey that was still edible.",
                "caption": "1000 year honey",
                "image_prompt": "cartoon ancient pot of honey in a tomb",
            },
            {
                "spoken": "If it crystallizes, warm it. It is not dead. It is napping.",
                "caption": "just napping",
                "image_prompt": "cartoon honey jar with a sleepy face",
            },
        ],
    },
    {
        "id": "chili_is_pain",
        "category": "food",
        "title": "chili heat is pain not taste",
        "beats": [
            {
                "spoken": "Do you know spicy is not a flavor? It is your nerves yelling.",
                "caption": "not a flavor",
                "image_prompt": "cartoon red chili pepper with a warning sign",
            },
            {
                "spoken": "Capsaicin tricks pain receptors that also detect heat.",
                "caption": "pain receptors",
                "image_prompt": "cartoon tongue with little alarm bells",
            },
            {
                "spoken": "Your brain thinks you are on fire. You are not. You just ate a plant's defense system.",
                "caption": "plant defense",
                "image_prompt": "cartoon plant spraying tiny chili flames",
            },
            {
                "spoken": "Milk helps. Water just spreads the chaos.",
                "caption": "milk not water",
                "image_prompt": "cartoon glass of milk next to a chili vs a water glass",
            },
        ],
    },
    {
        "id": "banana_berry",
        "category": "food",
        "title": "bananas are berries",
        "beats": [
            {
                "spoken": "Do you know bananas are berries, but strawberries are not?",
                "caption": "banana is a berry",
                "image_prompt": "cartoon banana wearing a berry name tag",
            },
            {
                "spoken": "Botany says a berry is fruit from one flower with seeds inside the flesh.",
                "caption": "seeds inside",
                "image_prompt": "simple cartoon cross section of a banana",
            },
            {
                "spoken": "Strawberries wear their seeds on the outside. That makes them a fake-out.",
                "caption": "strawberry fake-out",
                "image_prompt": "cartoon strawberry with seeds on the outside looking sneaky",
            },
            {
                "spoken": "The grocery aisle is lying to you politely.",
                "caption": "grocery lies",
                "image_prompt": "cartoon fruit aisle with a banana and strawberry arguing",
            },
        ],
    },
    {
        "id": "wasabi_not_wasabi",
        "category": "food",
        "title": "most wasabi is not wasabi",
        "beats": [
            {
                "spoken": "Do you know most sushi wasabi is not wasabi?",
                "caption": "fake wasabi",
                "image_prompt": "cartoon green sushi paste dollop",
            },
            {
                "spoken": "It is usually horseradish, mustard, and green coloring.",
                "caption": "horseradish mix",
                "image_prompt": "cartoon horseradish root with green paint bucket",
            },
            {
                "spoken": "Real wasabi is pricey, fussy, and loses punch in minutes.",
                "caption": "real is rare",
                "image_prompt": "cartoon fresh wasabi rhizome on a grater",
            },
            {
                "spoken": "That sinus punch? A costume.",
                "caption": "a costume",
                "image_prompt": "cartoon wasabi blob wearing a tiny disguise mask",
            },
        ],
    },
    {
        "id": "pineapple_eats_you",
        "category": "food",
        "title": "pineapple eats you back",
        "beats": [
            {
                "spoken": "Do you know pineapple tries to digest you while you eat it?",
                "caption": "it eats you",
                "image_prompt": "cartoon pineapple with tiny teeth smiling",
            },
            {
                "spoken": "It has bromelain, an enzyme that breaks down protein. Including your tongue.",
                "caption": "bromelain enzyme",
                "image_prompt": "cartoon enzyme Pac-Man eating protein shapes",
            },
            {
                "spoken": "That tingly mouth is not just juice. It is a tiny science fight.",
                "caption": "tingly science fight",
                "image_prompt": "cartoon tongue with sparkles after pineapple",
            },
            {
                "spoken": "Cooking shuts the enzyme off. Fresh is the chaotic one.",
                "caption": "fresh is chaos",
                "image_prompt": "cartoon fresh pineapple vs cooked pineapple slices",
            },
        ],
    },
    {
        "id": "vanilla_orchid",
        "category": "food",
        "title": "vanilla is an orchid",
        "beats": [
            {
                "spoken": "Do you know vanilla comes from an orchid, not a bean farm cartoon?",
                "caption": "it is an orchid",
                "image_prompt": "cartoon vanilla orchid flower with a long pod",
            },
            {
                "spoken": "Each flower is pollinated by hand in most farms. One blossom, one shot.",
                "caption": "hand pollinated",
                "image_prompt": "cartoon hand pollinating a tiny orchid flower",
            },
            {
                "spoken": "That is why real vanilla is expensive and fake vanilla is everywhere.",
                "caption": "that is why pricey",
                "image_prompt": "cartoon expensive vanilla bottle vs cheap bottle",
            },
            {
                "spoken": "Your ice cream is wearing a luxury flower.",
                "caption": "luxury flower",
                "image_prompt": "cartoon ice cream scoop with an orchid on top",
            },
        ],
    },
    {
        "id": "dark_triad",
        "category": "psychology",
        "title": "the dark triad",
        "beats": [
            {
                "spoken": "Do you know the dark triad is three personality traits that cluster together?",
                "caption": "three dark traits",
                "image_prompt": "three simple cartoon masks: charming, calculating, cold",
            },
            {
                "spoken": "Narcissism, Machiavellianism, and psychopathy. Charm, strategy, and low empathy.",
                "caption": "charm strategy ice",
                "image_prompt": "cartoon chess piece, mirror, and ice cube icons",
            },
            {
                "spoken": "Not a movie villain checklist. Everyday people can score high on pieces of it.",
                "caption": "not just villains",
                "image_prompt": "cartoon ordinary coffee cup next to a tiny villain cape",
            },
            {
                "spoken": "Curiosity is fine. Diagnosing your group chat is not.",
                "caption": "do not diagnose",
                "image_prompt": "cartoon phone group chat with question marks",
            },
        ],
    },
    {
        "id": "narcissism_mirror",
        "category": "psychology",
        "title": "narcissism needs supply",
        "beats": [
            {
                "spoken": "Do you know narcissism is less about loving yourself and more about needing applause?",
                "caption": "needs applause",
                "image_prompt": "cartoon mirror reflecting a trophy instead of a face",
            },
            {
                "spoken": "The ego looks shiny. Under it is a tank that runs on attention.",
                "caption": "runs on attention",
                "image_prompt": "cartoon fuel tank labeled attention",
            },
            {
                "spoken": "Criticism can feel like an attack, not feedback.",
                "caption": "critique feels attack",
                "image_prompt": "cartoon speech bubble bouncing off a shield",
            },
            {
                "spoken": "Confidence shares the room. Narcissism rents the spotlight.",
                "caption": "rents the spotlight",
                "image_prompt": "cartoon stage spotlight with one chair",
            },
        ],
    },
    {
        "id": "machiavelli_chess",
        "category": "psychology",
        "title": "Machiavellianism is strategy",
        "beats": [
            {
                "spoken": "Do you know Machiavellianism is the chess-player trait of the dark triad?",
                "caption": "chess player trait",
                "image_prompt": "cartoon chessboard with a sly smile pawn",
            },
            {
                "spoken": "It is planning, manipulation, and treating people like pieces.",
                "caption": "people as pieces",
                "image_prompt": "cartoon chess pieces with simple human faces",
            },
            {
                "spoken": "Not loud chaos. Quiet calculation. Long game.",
                "caption": "quiet long game",
                "image_prompt": "cartoon hourglass next to a chess king",
            },
            {
                "spoken": "If every kindness has a receipt, that is the vibe.",
                "caption": "kindness with receipts",
                "image_prompt": "cartoon gift box with a tiny receipt attached",
            },
        ],
    },
    {
        "id": "gossip_glue",
        "category": "psychology",
        "title": "gossip is social glue",
        "beats": [
            {
                "spoken": "Do you know gossip probably evolved as social glue, not just meanness?",
                "caption": "social glue",
                "image_prompt": "cartoon two faces whispering with a glue bottle",
            },
            {
                "spoken": "It spreads who is safe, who cheats, who shares. Fast group intel.",
                "caption": "who is safe",
                "image_prompt": "cartoon village of simple faces with rumor arrows",
            },
            {
                "spoken": "Your brain treats a juicy story like a survival update.",
                "caption": "survival update",
                "image_prompt": "cartoon brain wearing headphones listening to gossip",
            },
            {
                "spoken": "Still. Being interesting is not the same as being kind.",
                "caption": "interesting vs kind",
                "image_prompt": "cartoon scales balancing a sparkle and a heart",
            },
        ],
    },
    {
        "id": "negativity_bias",
        "category": "psychology",
        "title": "brains love bad news",
        "beats": [
            {
                "spoken": "Do you know your brain weighs one insult heavier than many compliments?",
                "caption": "insults weigh more",
                "image_prompt": "cartoon scale with one dark comment outweighing hearts",
            },
            {
                "spoken": "Negativity bias. Bad news kept ancestors alive. Miss a tiger, you are lunch.",
                "caption": "miss a tiger",
                "image_prompt": "cartoon tiger silhouette in tall grass",
            },
            {
                "spoken": "That is why comments sections feel like a swamp.",
                "caption": "comment swamp",
                "image_prompt": "cartoon phone sinking into a swamp of comments",
            },
            {
                "spoken": "Your brain is not broken. It is just still camping in 10,000 BC.",
                "caption": "still camping",
                "image_prompt": "cartoon caveman brain in a tiny tent",
            },
        ],
    },
    {
        "id": "default_mode_mind",
        "category": "psychology",
        "title": "your mind wanders on purpose",
        "beats": [
            {
                "spoken": "Do you know your brain has a default mode that daydreams when you are idle?",
                "caption": "default daydream",
                "image_prompt": "cartoon brain sitting on a cloud daydreaming",
            },
            {
                "spoken": "It replays people, plans, and awkward moments on loop.",
                "caption": "awkward replay",
                "image_prompt": "cartoon film reel of an embarrassing moment",
            },
            {
                "spoken": "That network is useful for meaning. It is also why showers invent lore.",
                "caption": "shower lore",
                "image_prompt": "cartoon shower with thought bubbles",
            },
            {
                "spoken": "You are not lazy. Your mind is drafting.",
                "caption": "mind is drafting",
                "image_prompt": "cartoon notebook writing itself",
            },
        ],
    },
    {
        "id": "cannot_tickle_self",
        "category": "body",
        "title": "you cannot tickle yourself",
        "beats": [
            {
                "spoken": "Do you know you usually cannot tickle yourself?",
                "caption": "cannot self-tickle",
                "image_prompt": "cartoon hand trying to tickle a cartoon foot unsuccessfully",
            },
            {
                "spoken": "Your cerebellum predicts your own touch and cancels the surprise.",
                "caption": "brain predicts it",
                "image_prompt": "cartoon cerebellum with a cancel stamp",
            },
            {
                "spoken": "Tickling needs unpredictability. That is why someone else works.",
                "caption": "needs surprise",
                "image_prompt": "cartoon two people, one surprising the other with a tickle",
            },
            {
                "spoken": "Your body refuses to prank the owner.",
                "caption": "no self pranks",
                "image_prompt": "cartoon body with a tiny security guard",
            },
        ],
    },
    {
        "id": "yawning_contagious",
        "category": "body",
        "title": "yawns are contagious",
        "beats": [
            {
                "spoken": "Do you know yawns can jump from brain to brain?",
                "caption": "yawns jump brains",
                "image_prompt": "cartoon yawn spreading between two simple faces",
            },
            {
                "spoken": "Seeing, hearing, even reading about yawning can set one off.",
                "caption": "even reading",
                "image_prompt": "cartoon book with a giant yawn coming out",
            },
            {
                "spoken": "It links to empathy circuits. Dogs can catch them from humans too.",
                "caption": "dogs catch them",
                "image_prompt": "cartoon dog yawning next to a human",
            },
            {
                "spoken": "If you just yawned, congratulations. You are extremely online.",
                "caption": "you just yawned",
                "image_prompt": "cartoon phone with a yawning emoji",
            },
        ],
    },
    {
        "id": "stomach_more_neurons",
        "category": "body",
        "title": "your gut has a second brain",
        "beats": [
            {
                "spoken": "Do you know your gut has its own nervous system with hundreds of millions of neurons?",
                "caption": "second brain",
                "image_prompt": "cartoon stomach wearing tiny glasses like a brain",
            },
            {
                "spoken": "It can keep working even if the main brain connection is cut.",
                "caption": "works on its own",
                "image_prompt": "cartoon intestine with a little independent control panel",
            },
            {
                "spoken": "That is why feelings hit the stomach first. Butterflies are wiring.",
                "caption": "butterflies are wiring",
                "image_prompt": "cartoon butterflies inside a stomach outline",
            },
            {
                "spoken": "Trust your gut is not just a poster. It is anatomy being dramatic.",
                "caption": "anatomy drama",
                "image_prompt": "cartoon gut sending a text to the brain",
            },
        ],
    },
    {
        "id": "fingerprints_unique",
        "category": "body",
        "title": "fingerprints form in the womb",
        "beats": [
            {
                "spoken": "Do you know fingerprints form in the womb from tiny skin stress patterns?",
                "caption": "formed in womb",
                "image_prompt": "cartoon baby hand with swirl fingerprints",
            },
            {
                "spoken": "Even identical twins do not match. Same DNA, different swirls.",
                "caption": "twins still differ",
                "image_prompt": "two cartoon twin faces with different fingerprint icons",
            },
            {
                "spoken": "They help grip wet objects, not just catch criminals.",
                "caption": "for grip too",
                "image_prompt": "cartoon wet glass being held by a fingerprint hand",
            },
            {
                "spoken": "You had a unique ID before you had a name.",
                "caption": "ID before a name",
                "image_prompt": "cartoon ID card with a fingerprint instead of a photo",
            },
        ],
    },
    {
        "id": "bones_rebuild",
        "category": "body",
        "title": "your skeleton rebuilds",
        "beats": [
            {
                "spoken": "Do you know your skeleton is constantly being torn down and rebuilt?",
                "caption": "bones rebuild",
                "image_prompt": "cartoon bone with tiny construction workers",
            },
            {
                "spoken": "About every ten years you are basically on a new frame.",
                "caption": "new frame",
                "image_prompt": "cartoon calendar flipping ten years next to a bone",
            },
            {
                "spoken": "Lift weights and bones get the memo to thicken. Sit forever and they slack.",
                "caption": "use it or lose",
                "image_prompt": "cartoon dumbbell next to a strong bone",
            },
            {
                "spoken": "You are a renovation project that never files permits.",
                "caption": "endless renovation",
                "image_prompt": "cartoon house made of bones under renovation",
            },
        ],
    },
    {
        "id": "taste_smell",
        "category": "body",
        "title": "flavor is mostly smell",
        "beats": [
            {
                "spoken": "Do you know most of flavor is smell, not the tongue?",
                "caption": "flavor is smell",
                "image_prompt": "cartoon nose bigger than a cartoon tongue",
            },
            {
                "spoken": "Hold your nose and an onion can fake as apple. Chaos.",
                "caption": "onion fake apple",
                "image_prompt": "cartoon onion wearing an apple costume",
            },
            {
                "spoken": "The tongue handles basic tastes. The nose handles the movie.",
                "caption": "nose does the movie",
                "image_prompt": "cartoon popcorn and a film reel coming from a nose",
            },
            {
                "spoken": "That is why colds make food taste like sad cardboard.",
                "caption": "colds kill flavor",
                "image_prompt": "cartoon tissue box next to bland toast",
            },
        ],
    },
    {
        "id": "trees_talk",
        "category": "nature",
        "title": "trees share through fungi",
        "beats": [
            {
                "spoken": "Do you know trees can share food and warnings through underground fungi?",
                "caption": "trees share",
                "image_prompt": "cartoon trees connected by glowing underground threads",
            },
            {
                "spoken": "The wood wide web. Not Wi-Fi. Mycelium.",
                "caption": "wood wide web",
                "image_prompt": "cartoon Wi-Fi symbol made of mushroom threads",
            },
            {
                "spoken": "A mother tree can send extra sugar to shaded seedlings.",
                "caption": "sugar to kids",
                "image_prompt": "cartoon big tree passing a sugar cube to a sapling",
            },
            {
                "spoken": "Forests are gossip networks with roots.",
                "caption": "root gossip",
                "image_prompt": "cartoon trees whispering via root phones",
            },
        ],
    },
    {
        "id": "rain_smell",
        "category": "nature",
        "title": "that rain smell has a name",
        "beats": [
            {
                "spoken": "Do you know the smell after rain has a name? Petrichor.",
                "caption": "petrichor",
                "image_prompt": "cartoon rain hitting dry earth with little scent swirls",
            },
            {
                "spoken": "Oils from plants plus a bacteria perfume get kicked into the air.",
                "caption": "plant oils plus germs",
                "image_prompt": "cartoon soil, plant, and tiny bacteria making perfume",
            },
            {
                "spoken": "Humans are weirdly good at detecting it. Ancient water-finding skill.",
                "caption": "water-finding skill",
                "image_prompt": "cartoon nose following rain scent to a puddle",
            },
            {
                "spoken": "That cozy rain smell is dirt doing a product launch.",
                "caption": "dirt product launch",
                "image_prompt": "cartoon dirt wearing a tiny perfume bottle",
            },
        ],
    },
    {
        "id": "volcano_lightning",
        "category": "nature",
        "title": "volcanoes can make lightning",
        "beats": [
            {
                "spoken": "Do you know volcanoes can make their own lightning?",
                "caption": "volcano lightning",
                "image_prompt": "cartoon volcano with lightning in the ash cloud",
            },
            {
                "spoken": "Ash particles smash, charge up, and boom — dirty thunderstorm.",
                "caption": "dirty thunderstorm",
                "image_prompt": "cartoon ash particles colliding and sparking",
            },
            {
                "spoken": "No rain required. Just chaos and static.",
                "caption": "no rain needed",
                "image_prompt": "cartoon dry storm cloud made of ash",
            },
            {
                "spoken": "Earth sometimes roleplays as a movie trailer.",
                "caption": "movie trailer earth",
                "image_prompt": "cartoon earth wearing director clapperboard",
            },
        ],
    },
    {
        "id": "moon_earthquakes",
        "category": "nature",
        "title": "the moon has moonquakes",
        "beats": [
            {
                "spoken": "Do you know the moon has moonquakes?",
                "caption": "moonquakes",
                "image_prompt": "cartoon moon with little shake lines",
            },
            {
                "spoken": "Some last longer than Earth quakes because the dry rock rings like a bell.",
                "caption": "rings like a bell",
                "image_prompt": "cartoon moon ringing like a bell",
            },
            {
                "spoken": "Earth's gravity tugs. The crust complains.",
                "caption": "earth tugs it",
                "image_prompt": "cartoon earth pulling the moon with a rubber band",
            },
            {
                "spoken": "Even space rocks have drama.",
                "caption": "space rock drama",
                "image_prompt": "cartoon moon with a tiny soap opera mask",
            },
        ],
    },
    {
        "id": "ants_no_lungs",
        "category": "nature",
        "title": "ants do not have lungs",
        "beats": [
            {
                "spoken": "Do you know ants do not have lungs?",
                "caption": "no lungs",
                "image_prompt": "cartoon ant with tiny air holes along its body",
            },
            {
                "spoken": "They breathe through holes called spiracles. Oxygen diffuses in.",
                "caption": "they just diffuse",
                "image_prompt": "cartoon air going into an ant through side holes",
            },
            {
                "spoken": "That is one reason giant ants stay fiction. Physics said no.",
                "caption": "giant ants are no",
                "image_prompt": "tiny cartoon ant next to a crossed-out giant ant",
            },
            {
                "spoken": "Small body, big empire. Still no cardio.",
                "caption": "empire no cardio",
                "image_prompt": "cartoon ant colony skyline",
            },
        ],
    },
    {
        "id": "northern_lights",
        "category": "nature",
        "title": "auroras are solar leftovers",
        "beats": [
            {
                "spoken": "Do you know the northern lights are the sun throwing leftover particles at Earth?",
                "caption": "sun leftovers",
                "image_prompt": "cartoon sun tossing sparkles at planet earth",
            },
            {
                "spoken": "They slam into air near the poles and the sky glows green and pink.",
                "caption": "sky glows",
                "image_prompt": "cartoon green and pink aurora over simple mountains",
            },
            {
                "spoken": "Same physics as a neon sign. Bigger budget.",
                "caption": "neon sign physics",
                "image_prompt": "cartoon neon sign next to an aurora",
            },
            {
                "spoken": "Space weather, but make it pretty.",
                "caption": "pretty space weather",
                "image_prompt": "cartoon weather forecast showing auroras",
            },
        ],
    },
    {
        "id": "empty_atom",
        "category": "weird_science",
        "title": "atoms are mostly empty",
        "beats": [
            {
                "spoken": "Do you know atoms are almost entirely empty space?",
                "caption": "mostly empty",
                "image_prompt": "cartoon atom with a tiny nucleus and huge empty rings",
            },
            {
                "spoken": "If a nucleus were a marble, the electrons would be a sports stadium away.",
                "caption": "stadium away",
                "image_prompt": "cartoon marble in the middle of a huge stadium",
            },
            {
                "spoken": "You feel solid because of electromagnetic push, not because you are packed.",
                "caption": "you are a force field",
                "image_prompt": "cartoon hand bouncing off an invisible force field",
            },
            {
                "spoken": "You are a polite illusion that can still stub a toe.",
                "caption": "polite illusion",
                "image_prompt": "cartoon toe stubbing a cartoon table leg",
            },
        ],
    },
    {
        "id": "time_slower_speed",
        "category": "weird_science",
        "title": "fast clocks run slow",
        "beats": [
            {
                "spoken": "Do you know clocks run slower when they move faster? Relativity is petty like that.",
                "caption": "fast clocks lag",
                "image_prompt": "cartoon rocket with a slow clock vs a sitting clock",
            },
            {
                "spoken": "GPS satellites have to correct for this or maps would drift.",
                "caption": "GPS needs this",
                "image_prompt": "cartoon GPS satellite with a clock adjustment wrench",
            },
            {
                "spoken": "Time is not a universal hallway. It is local vibes plus gravity.",
                "caption": "time is local",
                "image_prompt": "cartoon hallway of clocks showing different times",
            },
            {
                "spoken": "Your phone is secretly doing Einstein homework.",
                "caption": "phone does Einstein",
                "image_prompt": "cartoon phone wearing tiny Einstein hair",
            },
        ],
    },
    {
        "id": "hot_water_freezes",
        "category": "weird_science",
        "title": "hot water can freeze first",
        "beats": [
            {
                "spoken": "Do you know hot water can freeze faster than cold water? The Mpemba effect.",
                "caption": "hot can freeze first",
                "image_prompt": "cartoon steaming mug racing a cold glass to ice",
            },
            {
                "spoken": "Scientists still argue about the exact why. Evaporation, currents, impurities.",
                "caption": "still arguing",
                "image_prompt": "cartoon scientists arguing around two ice cubes",
            },
            {
                "spoken": "It does not always happen. Nature loves a messy plot twist.",
                "caption": "not always",
                "image_prompt": "cartoon plot twist stamp on an ice cube",
            },
            {
                "spoken": "Even ice has beef.",
                "caption": "ice has beef",
                "image_prompt": "two cartoon ice cubes glaring at each other",
            },
        ],
    },
    {
        "id": "glass_not_liquid",
        "category": "weird_science",
        "title": "glass is not a slow liquid",
        "beats": [
            {
                "spoken": "Do you know old windows being thicker at the bottom is not glass flowing like syrup?",
                "caption": "glass is not syrup",
                "image_prompt": "cartoon window pane thicker at the bottom",
            },
            {
                "spoken": "Medieval glass was just made uneven, then installed that way.",
                "caption": "made uneven",
                "image_prompt": "cartoon old glassmaker rolling lumpy glass",
            },
            {
                "spoken": "Glass is an amorphous solid. Stuck, not dripping through centuries.",
                "caption": "amorphous solid",
                "image_prompt": "cartoon frozen liquid that is actually a solid block",
            },
            {
                "spoken": "A beautiful myth. Physics said sit down.",
                "caption": "myth sits down",
                "image_prompt": "cartoon myth character sitting in a timeout chair",
            },
        ],
    },
    {
        "id": "light_year_distance",
        "category": "weird_science",
        "title": "a light year is distance",
        "beats": [
            {
                "spoken": "Do you know a light year is a distance, not a time?",
                "caption": "it is distance",
                "image_prompt": "cartoon ruler stretching across stars",
            },
            {
                "spoken": "It is how far light travels in one year. About nine trillion kilometers.",
                "caption": "nine trillion km",
                "image_prompt": "cartoon beam of light racing past planets",
            },
            {
                "spoken": "Looking at a star is looking at the past. The light left earlier.",
                "caption": "looking at the past",
                "image_prompt": "cartoon telescope seeing a delayed star postcard",
            },
            {
                "spoken": "The night sky is a delayed group chat.",
                "caption": "delayed group chat",
                "image_prompt": "cartoon stars as chat bubbles with timestamps",
            },
        ],
    },
    {
        "id": "quantum_empty",
        "category": "weird_science",
        "title": "empty space is not empty",
        "beats": [
            {
                "spoken": "Do you know empty space is not empty? It fizzes with virtual particles.",
                "caption": "space fizzes",
                "image_prompt": "cartoon empty box full of tiny spark particles",
            },
            {
                "spoken": "They pop in and out so fast you cannot catch them like regular stuff.",
                "caption": "pop in and out",
                "image_prompt": "cartoon particles appearing and vanishing like popcorn",
            },
            {
                "spoken": "Even vacuum has energy. The universe refuses to chill.",
                "caption": "vacuum has energy",
                "image_prompt": "cartoon vacuum cleaner that is actually sparkling energy",
            },
            {
                "spoken": "Nothing is doing a lot of overtime.",
                "caption": "nothing works overtime",
                "image_prompt": "cartoon clock showing overtime next to empty space",
            },
        ],
    },
]


CATEGORY_HASHTAGS = {
    "animals": ["animals", "wildlife", "naturefacts"],
    "food": ["foodfacts", "didyouknowfood", "scienceoffood"],
    "psychology": ["psychology", "darktriad", "mindfacts"],
    "body": ["humanbody", "bodyfacts", "sciencefacts"],
    "nature": ["nature", "earthfacts", "science"],
    "weird_science": ["science", "physics", "mindblown"],
}


def format_fact_caption(fact: dict[str, Any], hashtags: list[str] | None = None) -> str:
    title = fact["title"]
    spoken = " ".join(b["spoken"] for b in fact.get("beats") or [])
    recap = spoken[:220].rsplit(" ", 1)[0] + "…" if len(spoken) > 220 else spoken
    tags = hashtags or (
        ["didyouknow", "facts", "reels", "nibthefridgegoblin"]
        + CATEGORY_HASHTAGS.get(fact.get("category", ""), ["curious"])
    )
    tag_line = " ".join(f"#{t.lstrip('#')}" for t in tags[:12])
    lines = [
        fact["title"][0].upper() + fact["title"][1:] if fact["title"] else title,
        "",
        recap,
        "",
        "Follow @nibthefridgegoblin",
        tag_line,
    ]
    return "\n".join(lines)
