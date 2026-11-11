from __future__ import annotations

import re
from typing import Any

# Fallback curiosity facts if Gemini cannot invent a new topic.
# Daily runs generate fresh facts; this bank is only used when the API is down.
# [pause] marks become real TTS breaths.
FACTS: list[dict[str, Any]] = [
    {
        "id": "octopus_three_hearts",
        "category": "animals",
        "title": "octopuses have three hearts",
        "beats": [
            {
                "spoken": "Don't look away. [pause] This sea goblin is walking around with three hearts.",
                "caption": "three hearts",
                "image_prompt": "cute cartoon octopus with three small red hearts floating beside it",
            },
            {
                "spoken": "Two hearts are on gill duty. [pause] The third one bosses the rest of the body.",
                "caption": "two for gills",
                "image_prompt": "simple cartoon octopus gills with two tiny hearts pumping",
            },
            {
                "spoken": "And when it swims? [pause:short] That body heart just… stops. That's why it would rather crawl.",
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
                "spoken": "A crow can hold a grudge longer than your ex. [pause] Years. Faces included.",
                "caption": "they remember you",
                "image_prompt": "cartoon crow staring at a simple human face mask",
            },
            {
                "spoken": "You were mean? [pause] They tell the whole flock. Group chat with wings.",
                "caption": "they tell friends",
                "image_prompt": "three cartoon crows whispering together on a wire",
            },
            {
                "spoken": "Be nice and they might pay you in shiny junk. [pause] Goblin-approved gifts.",
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
                "spoken": "Trees are the new kids. [pause] Sharks were already hunting.",
                "caption": "older than trees",
                "image_prompt": "cartoon shark swimming past a tiny cartoon tree",
            },
            {
                "spoken": "Four hundred million years on this planet. [pause] Trees hadn't even shown up yet.",
                "caption": "400 million years",
                "image_prompt": "simple prehistoric cartoon ocean with a primitive shark",
            },
            {
                "spoken": "Ice ages. Extinction waves. [pause] Still looking like a warning sticker.",
                "caption": "still here",
                "image_prompt": "cartoon shark silhouette like a warning sign",
            },
            {
                "spoken": "The ocean had killers before the forest even existed. [pause] Trees are the new kids.",
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
                "spoken": "Lose an arm. Grow a new one. [pause] This salamander actually does it.",
                "caption": "grow limbs back",
                "image_prompt": "cute cartoon pink axolotl smiling",
            },
            {
                "spoken": "Legs. Tails. Chunks of heart. [pause] Even bits of brain. No scar drama.",
                "caption": "heart and brain",
                "image_prompt": "cartoon axolotl with a tiny regenerated glowing limb",
            },
            {
                "spoken": "Scientists are taking notes. [pause] Humans want that trick.",
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
                "spoken": "Look a goat in the eye. [pause] Those pupils are rectangles.",
                "caption": "rectangle eyes",
                "image_prompt": "cartoon goat face with horizontal rectangle pupils",
            },
            {
                "spoken": "That rectangle eye is a security camera. [pause] Almost panoramic. Predators hate it.",
                "caption": "panoramic vision",
                "image_prompt": "cartoon wide landscape seen through goat eyes",
            },
            {
                "spoken": "Head down to eat? [pause] The pupils rotate so the world stays level. Fancy.",
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
                "spoken": "I need five seconds. [pause] Wombats poop cubes. I am not joking.",
                "caption": "cube poop",
                "image_prompt": "cartoon wombat next to a few neat brown cubes",
            },
            {
                "spoken": "The cubes stack. [pause] Territory markers that don't roll downhill. Architecture.",
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
                "spoken": "This jar can outlive you. [pause] Honey basically never dies.",
                "caption": "never spoils",
                "image_prompt": "cartoon jar of golden honey with a bee",
            },
            {
                "spoken": "Low water. High sugar. A splash of hydrogen peroxide. [pause] Bacteria hate that combo.",
                "caption": "bacteria hate it",
                "image_prompt": "cartoon bacteria running away from a honey jar",
            },
            {
                "spoken": "Archaeologists found thousand-year-old honey. [pause] Still edible. Still smug.",
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
                "spoken": "Spicy is not a flavor. [pause] It is your nerves screaming.",
                "caption": "not a flavor",
                "image_prompt": "cartoon red chili pepper with a warning sign",
            },
            {
                "spoken": "Capsaicin tricks pain receptors that also detect heat. [pause] Your mouth files a false alarm.",
                "caption": "pain receptors",
                "image_prompt": "cartoon tongue with little alarm bells",
            },
            {
                "spoken": "Your brain thinks you are on fire. [pause] You are not. You ate a plant's defense system.",
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
                "spoken": "The grocery aisle has been lying. [pause] Bananas are berries. Strawberries are not.",
                "caption": "banana is a berry",
                "image_prompt": "cartoon banana wearing a berry name tag",
            },
            {
                "spoken": "Botany's definition is petty. [pause] One flower. Seeds inside the flesh. That's a berry.",
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
                "spoken": "That green paste next to your sushi? [pause] Probably not wasabi.",
                "caption": "fake wasabi",
                "image_prompt": "cartoon green sushi paste dollop",
            },
            {
                "spoken": "It's usually horseradish, mustard, and green dye. [pause] A costume in a little pile.",
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
                "spoken": "Pineapple is eating you back. [pause] Stay with me.",
                "caption": "it eats you",
                "image_prompt": "cartoon pineapple with tiny teeth smiling",
            },
            {
                "spoken": "Bromelain. [pause] An enzyme that breaks down protein. Including your tongue.",
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
                "spoken": "Vanilla is not a cute bean cartoon. [pause] It is a high-maintenance orchid.",
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
                "spoken": "Three traits travel in a pack. [pause] Charm. Calculation. Ice.",
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
                "spoken": "This is not self-love. [pause] It is an applause addiction.",
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
                "spoken": "Some people don't argue. [pause] They play chess with your life.",
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
                "spoken": "Gossip is not just mean. [pause] Your brain treats it like survival intel.",
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
                "spoken": "One insult outweighs a stack of compliments. [pause] Your brain is built that way.",
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
                "spoken": "When you go idle, your brain doesn't. [pause] It starts writing lore.",
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
                "spoken": "You cannot tickle yourself. [pause] Your brain ruins the surprise on purpose.",
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
                "spoken": "Yawning is a mind virus. [pause] Even reading this can set one off.",
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
                "spoken": "You have a second brain. [pause] It lives in your gut.",
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
                "spoken": "You had an ID before you had a name. [pause] Fingerprints, drawn in the womb.",
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
                "spoken": "The skeleton you have today is a renovation. [pause] It keeps tearing itself down.",
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
                "spoken": "Most of flavor is not the tongue. [pause] The nose is running the show.",
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
                "spoken": "Trees talk underground. [pause] Through a fungal internet.",
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
                "spoken": "That smell after rain has a name. [pause] Petrichor.",
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
                "spoken": "Volcanoes can make lightning. [pause] No storm required.",
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
                "spoken": "The moon is not a dead rock. [pause] It has moonquakes.",
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
                "spoken": "Ants do not have lungs. [pause] They breathe through their armor.",
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
                "spoken": "The northern lights are leftover sun. [pause] Slapping Earth's sky.",
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
                "spoken": "You are mostly empty space. [pause] Atoms are a magic trick.",
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
                "spoken": "Clocks get petty when they move faster. [pause] Time actually slows.",
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
                "spoken": "Hot water can freeze first. [pause] Science still argues about it.",
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
                "spoken": "Old windows thicker at the bottom? [pause] Not because glass is dripping.",
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
                "spoken": "A light year is not a time. [pause] It is a distance wearing a costume.",
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
                "spoken": "Empty space is not empty. [pause] It fizzes.",
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


# Rotating genres for generated fact reels. Add a key here to unlock a new bucket.
FACT_CATEGORIES = [
    "animals",
    "sports",
    "psychology",
    "body",
    "nature",
    "food",
    "space",
    "history",
    "ocean",
    "inventions",
    "music",
    "geography",
    "weather",
    "chemistry",
    "physics",
    "plants",
    "insects",
    "dinosaurs",
    "architecture",
    "language",
    "money",
    "sleep",
    "tech",
    "cars",
    "aviation",
    "olympics",
    "games",
    "art",
    "archaeology",
    "cities",
    "records",
    "weird_science",
]

CATEGORY_HASHTAGS = {
    "animals": ["animals", "wildlife", "naturefacts"],
    "sports": ["sports", "sportsfacts", "athletics"],
    "psychology": ["psychology", "mindfacts", "brainfacts"],
    "body": ["humanbody", "bodyfacts", "sciencefacts"],
    "nature": ["nature", "earthfacts", "science"],
    "food": ["foodfacts", "didyouknowfood", "scienceoffood"],
    "space": ["space", "astronomy", "nasa"],
    "history": ["history", "historyfacts", "didyouknow"],
    "ocean": ["ocean", "marinebiology", "seafacts"],
    "inventions": ["inventions", "innovation", "techhistory"],
    "music": ["music", "musicfacts", "musichistory"],
    "geography": ["geography", "earthfacts", "maps"],
    "weather": ["weather", "climate", "science"],
    "chemistry": ["chemistry", "science", "stem"],
    "physics": ["physics", "science", "mindblown"],
    "plants": ["plants", "botany", "naturefacts"],
    "insects": ["insects", "bugs", "naturefacts"],
    "dinosaurs": ["dinosaurs", "paleontology", "prehistoric"],
    "architecture": ["architecture", "design", "historyfacts"],
    "language": ["language", "linguistics", "words"],
    "money": ["money", "economics", "financefacts"],
    "sleep": ["sleep", "brainfacts", "sciencefacts"],
    "tech": ["tech", "computers", "innovation"],
    "cars": ["cars", "automotive", "engineering"],
    "aviation": ["aviation", "planes", "engineering"],
    "olympics": ["olympics", "sports", "sportsfacts"],
    "games": ["gaming", "videogames", "gamer"],
    "art": ["art", "arthistory", "museum"],
    "archaeology": ["archaeology", "history", "ancient"],
    "cities": ["cities", "geography", "travel"],
    "records": ["worldrecords", "facts", "mindblown"],
    "weird_science": ["science", "physics", "mindblown"],
}


def format_fact_caption(fact: dict[str, Any], hashtags: list[str] | None = None) -> str:
    title = fact["title"]
    spoken = " ".join(b["spoken"] for b in fact.get("beats") or [])
    spoken = re.sub(r"\[pause(?::\w+)?\]", " ", spoken)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    recap = spoken[:220].rsplit(" ", 1)[0] + "…" if len(spoken) > 220 else spoken
    tags = hashtags or (
        ["didyouknow", "facts", "shorts", "curiosity"]
        + CATEGORY_HASHTAGS.get(fact.get("category", ""), ["curious"])
    )
    tag_line = " ".join(f"#{t.lstrip('#')}" for t in tags[:12])
    lines = [
        fact["title"][0].upper() + fact["title"][1:] if fact["title"] else title,
        "",
        recap,
        "",
        "Subscribe for one weird true fact every day.",
        tag_line,
    ]
    return "\n".join(lines)
