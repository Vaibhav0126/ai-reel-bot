from __future__ import annotations

from typing import Any

# Quick, easy, delicious meals for Nib kitchen reels.
# ingredients/spices [].key maps to cartoon props in props.py
MEALS: list[dict[str, Any]] = [
    {
        "id": "garlic_honey_chicken_rice",
        "name": "Garlic honey chicken rice",
        "time_mins": 25,
        "hook": "Takeout is slow. [pause] I'm faster — garlic honey chicken rice.",
        "ingredients_line": "Grab chicken, cooked rice, fresh garlic, honey, and a splash of soy sauce.",
        "spices_line": "Season with salt, black pepper, paprika, and a tiny pinch of chili flakes for heat.",
        "cook_line": "Sear the chicken golden, add garlic, then glaze with honey and soy. Coat every piece. Serve over hot rice and spoon the pan sauce on top.",
        "benefit": "High protein, sticky-glossy flavor, and one pan — fridge goblin approved.",
        "payoff": "Save this recipe. Full spices and steps are in the caption — cook it tonight.",
        "ingredients": [
            {"key": "chicken", "label": "Chicken thigh or breast", "amount": "150–180g, bite-size pieces"},
            {"key": "rice", "label": "Cooked rice", "amount": "1 cup (warm)"},
            {"key": "garlic", "label": "Garlic", "amount": "3 cloves, minced"},
            {"key": "honey", "label": "Honey", "amount": "1 tbsp"},
            {"key": "soy", "label": "Soy sauce", "amount": "1 tbsp"},
            {"key": "oil", "label": "Cooking oil", "amount": "1 tbsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "1/2 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "paprika", "label": "Paprika", "amount": "1/2 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "pinch (optional)"},
        ],
        "steps": [
            "Pat chicken dry. Toss with salt, black pepper, and paprika so every piece is coated.",
            "Heat oil in a pan on medium-high. Add chicken in one layer. Sear 3–4 minutes per side until golden.",
            "Lower heat to medium. Add minced garlic. Stir 30 seconds until fragrant (do not burn).",
            "Pour in honey, soy sauce, and a splash of water (1–2 tbsp). Add chili flakes if you want heat.",
            "Toss chicken until the glaze turns sticky and shiny, about 1–2 minutes.",
            "Scoop warm rice into a bowl. Top with chicken and all the pan sauce. Eat hot.",
        ],
        "nutrition": {
            "serving": "1 bowl",
            "kcal": 520,
            "protein_g": 40,
            "carbs_g": 55,
            "fat_g": 14,
            "fiber_g": 1,
        },
        "plate_prompt": (
            "Photoreal top-down bowl of garlic honey glazed chicken over white rice, "
            "glossy sticky sauce, sesame optional, ceramic bowl, soft kitchen light"
        ),
    },
    {
        "id": "egg_veggie_scramble",
        "name": "Egg veggie scramble",
        "time_mins": 12,
        "hook": "Twelve minutes. One pan. [pause] Breakfast that actually hits.",
        "ingredients_line": "Three eggs, a handful of spinach, one tomato, and a little cheese if you have it.",
        "spices_line": "Whisk in salt, black pepper, garlic powder, and a pinch of chili flakes.",
        "cook_line": "Scramble the eggs soft and slow, then fold in spinach and tomato at the end so they stay bright. Cheese melts on top.",
        "benefit": "Cheap protein that actually keeps you full until lunch.",
        "payoff": "Caption has every spice and step. Make it messy — goblins do.",
        "ingredients": [
            {"key": "eggs", "label": "Eggs", "amount": "3 large"},
            {"key": "spinach", "label": "Spinach", "amount": "1 big handful"},
            {"key": "tomato", "label": "Tomato", "amount": "1 small, chopped"},
            {"key": "cheese", "label": "Cheese", "amount": "20g shredded (optional)"},
            {"key": "butter", "label": "Butter or oil", "amount": "1 tsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "1/4 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "garlic", "label": "Garlic powder", "amount": "1/4 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "pinch (optional)"},
        ],
        "steps": [
            "Crack eggs into a bowl. Add salt, black pepper, garlic powder, and chili flakes. Whisk until smooth.",
            "Warm butter or oil in a nonstick pan on medium-low heat.",
            "Pour in eggs. Stir gently with a spatula, scraping the bottom, until mostly set but still soft.",
            "Add chopped tomato and spinach. Fold for 30–45 seconds until spinach wilts.",
            "Turn off heat. Sprinkle cheese on top and let it melt from the residual heat.",
            "Plate immediately. Soft eggs overcook fast — pull them early.",
        ],
        "nutrition": {
            "serving": "1 plate",
            "kcal": 340,
            "protein_g": 25,
            "carbs_g": 7,
            "fat_g": 23,
            "fiber_g": 2,
        },
        "plate_prompt": (
            "Photoreal fluffy scrambled eggs with wilted spinach and tomato on a rustic "
            "breakfast plate, melted cheese, natural morning light"
        ),
    },
    {
        "id": "tuna_avocado_rice",
        "name": "Tuna avocado rice bowl",
        "time_mins": 10,
        "hook": "No chef cosplay. [pause] Ten minutes. Tuna avocado rice bowl.",
        "ingredients_line": "Canned tuna, half an avocado, warm rice, soy sauce, and a squeeze of lemon.",
        "spices_line": "Mix in black pepper, garlic powder, and a pinch of chili flakes or sesame seeds.",
        "cook_line": "Flake the tuna with soy, lemon, and spices. Pile on rice. Fan the avocado on top. Done.",
        "benefit": "Protein plus healthy fats with almost zero dishes.",
        "payoff": "Full spice list and steps are in the caption — save it for lazy nights.",
        "ingredients": [
            {"key": "tuna", "label": "Canned tuna", "amount": "1 can (drained)"},
            {"key": "avocado", "label": "Avocado", "amount": "1/2, sliced"},
            {"key": "rice", "label": "Cooked rice", "amount": "1 cup (warm)"},
            {"key": "soy", "label": "Soy sauce", "amount": "1–2 tsp"},
            {"key": "lemon", "label": "Lemon or lime", "amount": "1 tsp juice"},
        ],
        "spices": [
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "garlic", "label": "Garlic powder", "amount": "1/4 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "pinch (optional)"},
            {"key": "sesame", "label": "Sesame seeds", "amount": "1/2 tsp (optional)"},
        ],
        "steps": [
            "Warm the rice in the microwave or steamer until hot and fluffy.",
            "Drain tuna well. Flake into a bowl with soy sauce, lemon juice, black pepper, and garlic powder.",
            "Taste and add a pinch more soy or chili flakes if you want it bolder.",
            "Scoop rice into a serving bowl. Spoon the seasoned tuna over half the rice.",
            "Slice avocado and lay it on the other half. Sprinkle sesame seeds if using.",
            "Eat right away so the avocado stays bright green.",
        ],
        "nutrition": {
            "serving": "1 bowl",
            "kcal": 460,
            "protein_g": 33,
            "carbs_g": 42,
            "fat_g": 17,
            "fiber_g": 5,
        },
        "plate_prompt": (
            "Photoreal rice bowl with flaked tuna and sliced avocado, soy drizzle, "
            "sesame seeds, ceramic bowl, bright kitchen light"
        ),
    },
    {
        "id": "greek_yogurt_parfait",
        "name": "Greek yogurt berry parfait",
        "time_mins": 5,
        "hook": "Dessert energy. Breakfast macros. [pause] Five-minute yogurt heist.",
        "ingredients_line": "Thick Greek yogurt, mixed berries, oats for crunch, and a drizzle of honey.",
        "spices_line": "Add cinnamon and a tiny pinch of salt — salt makes the berries pop.",
        "cook_line": "Layer yogurt, berries, oats, cinnamon, then honey. Repeat once. That is the whole recipe.",
        "benefit": "High protein treat that feels fancy with zero cooking.",
        "payoff": "Spices and amounts are in the caption. Build it, eat it, go.",
        "ingredients": [
            {"key": "yogurt", "label": "Greek yogurt", "amount": "200g plain"},
            {"key": "berries", "label": "Berries", "amount": "1/2 cup fresh or thawed"},
            {"key": "oats", "label": "Rolled oats", "amount": "2 tbsp"},
            {"key": "honey", "label": "Honey", "amount": "1 tsp (optional)"},
        ],
        "spices": [
            {"key": "cinnamon", "label": "Cinnamon", "amount": "1/4 tsp"},
            {"key": "salt", "label": "Salt", "amount": "tiny pinch"},
            {"key": "vanilla", "label": "Vanilla extract", "amount": "2 drops (optional)"},
        ],
        "steps": [
            "Stir cinnamon, a tiny pinch of salt, and optional vanilla into the yogurt.",
            "Spoon half the yogurt into a glass or bowl.",
            "Add half the berries and 1 tbsp oats.",
            "Repeat with remaining yogurt, berries, and oats.",
            "Drizzle honey on top. Serve cold.",
        ],
        "nutrition": {
            "serving": "1 cup",
            "kcal": 290,
            "protein_g": 22,
            "carbs_g": 30,
            "fat_g": 6,
            "fiber_g": 4,
        },
        "plate_prompt": (
            "Photoreal Greek yogurt parfait layered with mixed berries and oats in a "
            "clear glass, honey drizzle, soft morning light"
        ),
    },
    {
        "id": "chicken_wrap",
        "name": "Crispy chicken wrap",
        "time_mins": 18,
        "hook": "One wrap. One hand. Full meal. [pause] Crispy chicken. Let's go.",
        "ingredients_line": "Cooked chicken, a large tortilla, greens, and a quick yogurt sauce.",
        "spices_line": "Season chicken with salt, pepper, paprika, and oregano. Sauce gets garlic powder and chili.",
        "cook_line": "Warm the tortilla, load seasoned chicken and greens, smear yogurt sauce, roll tight, and slice.",
        "benefit": "Portable high-protein lunch you can eat walking out the door.",
        "payoff": "Every spice is listed in the caption — roll two and hide one.",
        "ingredients": [
            {"key": "chicken", "label": "Cooked chicken", "amount": "120–150g shredded or sliced"},
            {"key": "tortilla", "label": "Large tortilla / wrap", "amount": "1"},
            {"key": "spinach", "label": "Lettuce or spinach", "amount": "1 handful"},
            {"key": "yogurt", "label": "Greek yogurt (sauce)", "amount": "2 tbsp"},
            {"key": "lemon", "label": "Lemon juice", "amount": "1/2 tsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "1/4 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "paprika", "label": "Paprika", "amount": "1/2 tsp"},
            {"key": "oregano", "label": "Oregano", "amount": "1/4 tsp"},
            {"key": "garlic", "label": "Garlic powder", "amount": "1/4 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "pinch (optional)"},
        ],
        "steps": [
            "Toss chicken with salt, pepper, paprika, and oregano. Warm briefly in a dry pan so the spices bloom.",
            "Mix yogurt with lemon juice, garlic powder, and chili flakes for the sauce.",
            "Warm tortilla in a dry pan 20–30 seconds per side until soft and flexible.",
            "Spread yogurt sauce down the center. Add greens, then the seasoned chicken.",
            "Fold in the sides, then roll tightly from the bottom.",
            "Slice in half on a diagonal if you want it Instagram-ready. Eat warm.",
        ],
        "nutrition": {
            "serving": "1 wrap",
            "kcal": 430,
            "protein_g": 36,
            "carbs_g": 36,
            "fat_g": 14,
            "fiber_g": 3,
        },
        "plate_prompt": (
            "Photoreal chicken wrap cut in half on a plate, greens and sauce peeking out, "
            "home kitchen style"
        ),
    },
    {
        "id": "tofu_stir_fry",
        "name": "Tofu veggie stir-fry",
        "time_mins": 20,
        "hook": "Tofu does not have to be sad. [pause] Watch me make it dangerous.",
        "ingredients_line": "Firm tofu, frozen mixed veggies, garlic, soy sauce, and a little oil.",
        "spices_line": "Use salt, black pepper, ginger powder, and chili flakes — that is the flavor engine.",
        "cook_line": "Crisp the tofu first, blast the veggies hot, then sauce everything with soy, garlic, and spices.",
        "benefit": "Plant protein that tastes cooked, not steamed sadness.",
        "payoff": "Detailed spice amounts are in the caption. Serve over rice or alone.",
        "ingredients": [
            {"key": "tofu", "label": "Firm tofu", "amount": "200g, cubed"},
            {"key": "frozen", "label": "Frozen mixed veggies", "amount": "2 cups"},
            {"key": "garlic", "label": "Garlic", "amount": "3 cloves, minced"},
            {"key": "soy", "label": "Soy sauce", "amount": "1.5 tbsp"},
            {"key": "oil", "label": "Oil", "amount": "1.5 tbsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "pinch"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "ginger", "label": "Ginger powder", "amount": "1/2 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "1/4 tsp"},
        ],
        "steps": [
            "Press tofu 5 minutes in a towel. Cube. Season lightly with salt, pepper, and ginger powder.",
            "Heat 1 tbsp oil in a wide pan on medium-high. Add tofu. Do not crowd. Crisp 3–4 minutes per side.",
            "Push tofu aside or remove. Add remaining oil, then frozen veggies. Stir-fry 4–5 minutes until hot and slightly charred.",
            "Add garlic and chili flakes. Stir 30 seconds.",
            "Return tofu. Pour soy sauce around the pan. Toss until everything is glossy.",
            "Taste — add a splash more soy or pepper. Serve immediately over rice if you want.",
        ],
        "nutrition": {
            "serving": "1 plate",
            "kcal": 360,
            "protein_g": 27,
            "carbs_g": 22,
            "fat_g": 18,
            "fiber_g": 6,
        },
        "plate_prompt": (
            "Photoreal tofu vegetable stir-fry on a white plate, golden tofu cubes, "
            "colorful veggies, soy glaze, kitchen lighting"
        ),
    },
    {
        "id": "overnight_oats_bowl",
        "name": "Protein overnight oats",
        "time_mins": 5,
        "hook": "Two minutes tonight. [pause] Tomorrow-you gets protein oats without thinking.",
        "ingredients_line": "Oats, milk, Greek yogurt, and banana for sweetness.",
        "spices_line": "Stir in cinnamon, a pinch of salt, and optional vanilla — do not skip the salt.",
        "cook_line": "Mix everything in a jar, fridge overnight, top with banana in the morning. No stove.",
        "benefit": "Wake up to food that already exists. That is the goblin magic.",
        "payoff": "Caption has exact spice amounts. Make three jars at once.",
        "ingredients": [
            {"key": "oats", "label": "Rolled oats", "amount": "1/2 cup"},
            {"key": "milk", "label": "Milk (any)", "amount": "1/2 cup"},
            {"key": "yogurt", "label": "Greek yogurt", "amount": "100g"},
            {"key": "banana", "label": "Banana", "amount": "1/2, sliced (for topping)"},
            {"key": "honey", "label": "Honey", "amount": "1 tsp (optional)"},
        ],
        "spices": [
            {"key": "cinnamon", "label": "Cinnamon", "amount": "1/2 tsp"},
            {"key": "salt", "label": "Salt", "amount": "tiny pinch"},
            {"key": "vanilla", "label": "Vanilla extract", "amount": "1/4 tsp (optional)"},
        ],
        "steps": [
            "In a jar, combine oats, milk, yogurt, cinnamon, salt, vanilla, and honey if using.",
            "Stir until no dry oats remain. Scrape the sides.",
            "Lid on. Fridge at least 4 hours, ideally overnight.",
            "In the morning, stir once. Add a splash of milk if too thick.",
            "Top with banana slices. Eat cold or warm 30 seconds in the microwave.",
        ],
        "nutrition": {
            "serving": "1 jar",
            "kcal": 400,
            "protein_g": 24,
            "carbs_g": 54,
            "fat_g": 8,
            "fiber_g": 6,
        },
        "plate_prompt": (
            "Photoreal overnight oats in a glass jar topped with banana slices, creamy "
            "texture, soft morning light"
        ),
    },
    {
        "id": "shrimp_garlic_noodles",
        "name": "Garlic shrimp noodles",
        "time_mins": 18,
        "hook": "Restaurant energy. One pan. [pause] Garlic shrimp noodles in under twenty.",
        "ingredients_line": "Shrimp, noodles, lots of garlic, butter, and a splash of pasta water.",
        "spices_line": "Salt the shrimp, then finish with black pepper, paprika, and chili flakes in the butter.",
        "cook_line": "Boil noodles, sear shrimp pink, melt garlic butter with spices, then toss noodles until glossy.",
        "benefit": "Lean protein plus carbs that actually satisfy — tastes way fancier than the effort.",
        "payoff": "Spices and steps are written out in the caption. Screenshot before Nib eats it.",
        "ingredients": [
            {"key": "shrimp", "label": "Shrimp", "amount": "150g, peeled"},
            {"key": "noodles", "label": "Noodles or spaghetti", "amount": "80g dry"},
            {"key": "garlic", "label": "Garlic", "amount": "4 cloves, minced"},
            {"key": "butter", "label": "Butter", "amount": "1.5 tbsp"},
            {"key": "lemon", "label": "Lemon juice", "amount": "1 tsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "1/2 tsp (divided)"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "paprika", "label": "Paprika", "amount": "1/2 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "1/4 tsp"},
        ],
        "steps": [
            "Boil noodles in salted water until just al dente. Save 1/3 cup pasta water, then drain.",
            "Pat shrimp dry. Season with half the salt, black pepper, and paprika.",
            "Melt butter in a wide pan on medium. Add shrimp. Cook 1–2 minutes per side until pink. Remove.",
            "In the same pan, add garlic and chili flakes. Stir 30 seconds. Splash in lemon juice.",
            "Add noodles + a splash of pasta water. Toss until glossy and coated.",
            "Return shrimp. Toss 20 seconds. Taste for salt. Serve immediately with extra pepper.",
        ],
        "nutrition": {
            "serving": "1 bowl",
            "kcal": 530,
            "protein_g": 35,
            "carbs_g": 55,
            "fat_g": 17,
            "fiber_g": 2,
        },
        "plate_prompt": (
            "Photoreal garlic butter shrimp noodles in a bowl, glossy noodles, pink shrimp, "
            "chili flakes, warm kitchen light"
        ),
    },
    {
        "id": "cottage_cheese_toast",
        "name": "Cottage cheese toast",
        "time_mins": 8,
        "hook": "Toast, but make it protein. [pause] Cottage cheese. Stay with me.",
        "ingredients_line": "Bread, thick cottage cheese, ripe tomato, and optional fried egg.",
        "spices_line": "Finish with salt, cracked black pepper, chili flakes, and oregano.",
        "cook_line": "Toast the bread deep golden, pile cottage cheese high, add tomato, then crush spices on top.",
        "benefit": "Snack macros that punch way above a sad sandwich.",
        "payoff": "Exact spices are in the caption. Two slices. Zero excuses.",
        "ingredients": [
            {"key": "bread", "label": "Bread", "amount": "2 slices"},
            {"key": "cottage", "label": "Cottage cheese", "amount": "150g"},
            {"key": "tomato", "label": "Tomato", "amount": "1, sliced"},
            {"key": "eggs", "label": "Egg (optional)", "amount": "1 fried"},
            {"key": "oil", "label": "Olive oil", "amount": "1/2 tsp drizzle"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "pinch"},
            {"key": "pepper", "label": "Black pepper", "amount": "to taste (generous)"},
            {"key": "chili", "label": "Chili flakes", "amount": "pinch"},
            {"key": "oregano", "label": "Oregano or Italian herbs", "amount": "pinch"},
        ],
        "steps": [
            "Toast bread until deep golden and crisp at the edges.",
            "Spread cottage cheese thick on both slices while toast is hot.",
            "Layer tomato slices evenly. Optional: top one slice with a fried egg.",
            "Drizzle a tiny bit of olive oil.",
            "Season with salt, lots of cracked black pepper, chili flakes, and oregano.",
            "Eat immediately so the toast stays crunchy.",
        ],
        "nutrition": {
            "serving": "2 toasts",
            "kcal": 380,
            "protein_g": 30,
            "carbs_g": 32,
            "fat_g": 13,
            "fiber_g": 3,
        },
        "plate_prompt": (
            "Photoreal open-faced toast with thick cottage cheese and tomato slices, "
            "cracked black pepper and chili flakes, rustic plate"
        ),
    },
    {
        "id": "kimchi_fried_rice",
        "name": "Kimchi fried rice",
        "time_mins": 15,
        "hook": "Leftover rice plus kimchi. [pause] Chaos dinner. You're welcome.",
        "ingredients_line": "Day-old rice, kimchi, one egg, oil, and a splash of soy.",
        "spices_line": "Add garlic, gochugaru or chili flakes, black pepper, and a pinch of sugar to balance the sour.",
        "cook_line": "Fry kimchi hot, smash in rice, season, push aside, scramble the egg, then mix everything wild.",
        "benefit": "Spicy, filling, weirdly perfect for late nights.",
        "payoff": "Full spice list in the caption. Top with a fried egg if you are dramatic.",
        "ingredients": [
            {"key": "rice", "label": "Day-old cooked rice", "amount": "1.5 cups"},
            {"key": "kimchi", "label": "Kimchi", "amount": "1/2 cup, chopped (+ 1 tbsp juice)"},
            {"key": "eggs", "label": "Egg", "amount": "1 (plus optional fried egg on top)"},
            {"key": "soy", "label": "Soy sauce", "amount": "1 tsp"},
            {"key": "oil", "label": "Oil", "amount": "1 tbsp"},
            {"key": "garlic", "label": "Garlic", "amount": "2 cloves, minced"},
        ],
        "spices": [
            {"key": "chili", "label": "Gochugaru or chili flakes", "amount": "1/2 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "sugar", "label": "Sugar", "amount": "1/4 tsp"},
            {"key": "sesame", "label": "Sesame seeds / oil", "amount": "1/2 tsp (finish)"},
        ],
        "steps": [
            "Chop kimchi into small pieces. Keep a spoon of the juice.",
            "Heat oil in a hot pan. Add kimchi + garlic. Stir-fry 2 minutes until fragrant and slightly caramelized.",
            "Add rice. Smash clumps with a spatula. Stir-fry 2–3 minutes until hot.",
            "Add kimchi juice, soy, chili flakes, black pepper, and sugar. Toss until evenly pink-red.",
            "Push rice aside. Crack in the egg. Scramble quickly, then mix through the rice.",
            "Finish with sesame oil or seeds. Optional fried egg on top. Serve hot.",
        ],
        "nutrition": {
            "serving": "1 bowl",
            "kcal": 460,
            "protein_g": 16,
            "carbs_g": 64,
            "fat_g": 15,
            "fiber_g": 3,
        },
        "plate_prompt": (
            "Photoreal kimchi fried rice in a bowl topped with sunny-side-up egg, red "
            "kimchi bits, sesame seeds, chopsticks beside"
        ),
    },
    {
        "id": "hummus_bowl",
        "name": "Loaded hummus bowl",
        "time_mins": 10,
        "hook": "No stove. [pause] Assemble this hummus bowl like a snack architect.",
        "ingredients_line": "Hummus, cucumber, tomato, boiled eggs, and a drizzle of olive oil.",
        "spices_line": "Dust with paprika, cumin, salt, black pepper, and chili flakes.",
        "cook_line": "Swipe hummus thick, pile toppings in sections, drizzle oil, then rain spices over everything.",
        "benefit": "Fiber and protein without turning on the oven.",
        "payoff": "Spices make it taste restaurant-level — amounts are in the caption.",
        "ingredients": [
            {"key": "hummus", "label": "Hummus", "amount": "1/2 cup"},
            {"key": "cucumber", "label": "Cucumber", "amount": "1/2, chopped"},
            {"key": "tomato", "label": "Tomato", "amount": "1, chopped"},
            {"key": "eggs", "label": "Boiled eggs", "amount": "2, halved"},
            {"key": "oil", "label": "Olive oil", "amount": "1 tbsp"},
        ],
        "spices": [
            {"key": "paprika", "label": "Paprika", "amount": "1/2 tsp"},
            {"key": "cumin", "label": "Cumin", "amount": "1/4 tsp"},
            {"key": "salt", "label": "Salt", "amount": "pinch"},
            {"key": "pepper", "label": "Black pepper", "amount": "to taste"},
            {"key": "chili", "label": "Chili flakes", "amount": "pinch"},
        ],
        "steps": [
            "Spread hummus in a shallow bowl, swiping a well in the center with the back of a spoon.",
            "Arrange cucumber, tomato, and egg halves in sections on top.",
            "Drizzle olive oil over the hummus and veggies.",
            "Sprinkle paprika, cumin, salt, black pepper, and chili flakes evenly.",
            "Scoop with pita, crackers, or a spoon. Mix as you eat.",
        ],
        "nutrition": {
            "serving": "1 bowl",
            "kcal": 430,
            "protein_g": 23,
            "carbs_g": 24,
            "fat_g": 28,
            "fiber_g": 8,
        },
        "plate_prompt": (
            "Photoreal loaded hummus bowl with cucumber, tomato, halved boiled eggs, "
            "paprika dusting, olive oil drizzle, Mediterranean home style"
        ),
    },
    {
        "id": "banana_oat_pancakes",
        "name": "2-ingredient banana oat pancakes",
        "time_mins": 15,
        "hook": "Pancakes. No flour explosion. [pause] Banana oat stack. Let's cook.",
        "ingredients_line": "One ripe banana, oats, optional egg for fluff, berries to top.",
        "spices_line": "Blend in cinnamon, a pinch of salt, and optional vanilla for bakery vibes.",
        "cook_line": "Blend batter smooth, cook small pancakes on medium heat, flip once, stack with berries.",
        "benefit": "Sweet breakfast with real fuel — not just syrup and regret.",
        "payoff": "Spices and exact steps are in the caption. Yogurt on top if you are thriving.",
        "ingredients": [
            {"key": "banana", "label": "Ripe banana", "amount": "1 large"},
            {"key": "oats", "label": "Rolled oats", "amount": "1/2 cup"},
            {"key": "eggs", "label": "Egg", "amount": "1 (optional, for fluff)"},
            {"key": "berries", "label": "Berries", "amount": "handful to top"},
            {"key": "oil", "label": "Oil or butter for pan", "amount": "1 tsp"},
        ],
        "spices": [
            {"key": "cinnamon", "label": "Cinnamon", "amount": "1/2 tsp"},
            {"key": "salt", "label": "Salt", "amount": "tiny pinch"},
            {"key": "vanilla", "label": "Vanilla", "amount": "1/4 tsp (optional)"},
        ],
        "steps": [
            "Blend banana, oats, optional egg, cinnamon, salt, and vanilla until mostly smooth (small oat bits OK).",
            "Rest batter 2 minutes so oats hydrate. Add a splash of water/milk if too thick.",
            "Heat a lightly oiled nonstick pan on medium. Scoop small pancakes (about 2 tbsp each).",
            "Cook 2–3 minutes until bubbles form and edges look set. Flip once. Cook 1–2 minutes more.",
            "Stack on a plate. Top with berries. Optional Greek yogurt or honey.",
        ],
        "nutrition": {
            "serving": "1 stack",
            "kcal": 360,
            "protein_g": 13,
            "carbs_g": 58,
            "fat_g": 9,
            "fiber_g": 7,
        },
        "plate_prompt": (
            "Photoreal small stack of banana oat pancakes topped with fresh berries, "
            "rustic breakfast plate, soft light"
        ),
    },
    {
        "id": "salmon_sheet_pan",
        "name": "Sheet-pan salmon & veg",
        "time_mins": 25,
        "hook": "One tray. Oven does the work. [pause] You look competent. Sheet-pan salmon.",
        "ingredients_line": "Salmon fillet, mixed veggies, olive oil, and lemon.",
        "spices_line": "Coat everything with salt, pepper, garlic powder, paprika, and dried herbs.",
        "cook_line": "Season tray, roast hot until salmon flakes, finish with lemon. Almost zero dishes.",
        "benefit": "Omega-3s and protein with restaurant-level seasoning from your spice rack.",
        "payoff": "Caption lists every spice amount. Squeeze lemon. Pretend you meal-prepped.",
        "ingredients": [
            {"key": "salmon", "label": "Salmon fillet", "amount": "150–170g"},
            {"key": "frozen", "label": "Mixed veg or broccoli", "amount": "2 cups"},
            {"key": "lemon", "label": "Lemon", "amount": "1/2"},
            {"key": "oil", "label": "Olive oil", "amount": "1 tbsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "1/2 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "garlic", "label": "Garlic powder", "amount": "1/2 tsp"},
            {"key": "paprika", "label": "Paprika", "amount": "1/2 tsp"},
            {"key": "oregano", "label": "Oregano or thyme", "amount": "1/2 tsp"},
        ],
        "steps": [
            "Preheat oven to 220°C / 425°F. Line a tray with foil or parchment.",
            "Toss veggies with half the oil, salt, pepper, garlic powder, paprika, and herbs. Spread out.",
            "Pat salmon dry. Rub with remaining oil and the same spice mix on top.",
            "Place salmon on the tray beside the veggies (or on a clear spot in the center).",
            "Roast 12–15 minutes until salmon flakes easily and veggies are tender-crisp.",
            "Squeeze lemon over everything. Rest 1 minute. Plate and eat.",
        ],
        "nutrition": {
            "serving": "1 plate",
            "kcal": 450,
            "protein_g": 37,
            "carbs_g": 14,
            "fat_g": 27,
            "fiber_g": 5,
        },
        "plate_prompt": (
            "Photoreal roasted salmon fillet with mixed roasted vegetables, lemon wedge, "
            "paprika seasoning, sheet-pan dinner plate"
        ),
    },
    {
        "id": "beef_rice_bowl",
        "name": "Quick beef rice bowl",
        "time_mins": 20,
        "hook": "Ground beef. Rice. Sticky glaze. [pause] Dinner math that actually works.",
        "ingredients_line": "Ground beef, cooked rice, garlic, soy sauce, and honey.",
        "spices_line": "Bloom ginger, black pepper, chili flakes, and a pinch of salt in the beef fat.",
        "cook_line": "Brown the beef hard, add garlic and spices, glaze with soy-honey, then scoop over rice.",
        "benefit": "Iron and protein when you need a real meal, not a snack pretending to be dinner.",
        "payoff": "Spices and steps are fully written in the caption. Fried egg on top optional.",
        "ingredients": [
            {"key": "beef", "label": "Ground beef", "amount": "150g"},
            {"key": "rice", "label": "Cooked rice", "amount": "1 cup"},
            {"key": "garlic", "label": "Garlic", "amount": "3 cloves, minced"},
            {"key": "soy", "label": "Soy sauce", "amount": "1.5 tbsp"},
            {"key": "honey", "label": "Honey", "amount": "1 tbsp"},
            {"key": "oil", "label": "Oil", "amount": "1 tsp (if beef is very lean)"},
        ],
        "spices": [
            {"key": "ginger", "label": "Ginger powder", "amount": "1/2 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "chili", "label": "Chili flakes", "amount": "1/4 tsp"},
            {"key": "salt", "label": "Salt", "amount": "pinch (soy is salty — taste first)"},
        ],
        "steps": [
            "Heat a pan on medium-high. Add beef (and oil if needed). Break it up and brown hard, 4–5 minutes.",
            "Add garlic, ginger powder, black pepper, and chili flakes. Stir 30–45 seconds.",
            "Pour soy sauce and honey. Simmer 1–2 minutes until glossy and sticky. Taste for salt.",
            "Warm rice in a bowl. Spoon beef and all the glaze over the top.",
            "Optional: fry an egg and slide it on. Eat hot.",
        ],
        "nutrition": {
            "serving": "1 bowl",
            "kcal": 580,
            "protein_g": 35,
            "carbs_g": 50,
            "fat_g": 25,
            "fiber_g": 1,
        },
        "plate_prompt": (
            "Photoreal ground beef rice bowl with glossy soy-honey glaze, steam rising, "
            "ceramic bowl, warm kitchen light"
        ),
    },
    {
        "id": "caprese_chicken",
        "name": "Caprese chicken skillet",
        "time_mins": 22,
        "hook": "Chicken, tomato, melty cheese. [pause] Fancy words for easy pan food.",
        "ingredients_line": "Chicken breast, tomato, mozzarella, basil if you have it, splash of balsamic optional.",
        "spices_line": "Season chicken with salt, pepper, garlic powder, and Italian herbs before it hits the pan.",
        "cook_line": "Sear chicken, top with tomato and mozzarella, cover to melt, finish with basil and balsamic.",
        "benefit": "High-protein dinner that looks intentional with almost no prep.",
        "payoff": "Every spice amount is in the caption. Confidence not optional.",
        "ingredients": [
            {"key": "chicken", "label": "Chicken breast", "amount": "160–180g, pounded even"},
            {"key": "tomato", "label": "Tomato", "amount": "1, sliced"},
            {"key": "cheese", "label": "Mozzarella", "amount": "40–50g, sliced"},
            {"key": "basil", "label": "Fresh basil", "amount": "few leaves"},
            {"key": "oil", "label": "Olive oil", "amount": "1 tbsp"},
        ],
        "spices": [
            {"key": "salt", "label": "Salt", "amount": "1/2 tsp"},
            {"key": "pepper", "label": "Black pepper", "amount": "1/4 tsp"},
            {"key": "garlic", "label": "Garlic powder", "amount": "1/2 tsp"},
            {"key": "oregano", "label": "Italian herbs / oregano", "amount": "1/2 tsp"},
        ],
        "steps": [
            "Pat chicken dry. Season both sides with salt, pepper, garlic powder, and Italian herbs.",
            "Heat oil in a skillet on medium. Sear chicken 4–5 minutes until golden. Flip.",
            "On the second side, lay tomato slices then mozzarella on top of the chicken.",
            "Cover the pan 3–4 minutes until cheese melts and chicken is cooked through (75°C / 165°F).",
            "Kill the heat. Tear basil over the top. Optional balsamic drizzle.",
            "Rest 1 minute, then plate. Spoon any pan juices over the chicken.",
        ],
        "nutrition": {
            "serving": "1 plate",
            "kcal": 410,
            "protein_g": 44,
            "carbs_g": 6,
            "fat_g": 22,
            "fiber_g": 1,
        },
        "plate_prompt": (
            "Photoreal Caprese-style chicken breast topped with melted mozzarella and "
            "tomato slices, basil leaves, skillet dinner plate"
        ),
    },
]


def _spice_names(meal: dict[str, Any]) -> str:
    spices = meal.get("spices") or []
    if not spices:
        return "salt and black pepper"
    names = [s.get("label") or s.get("key", "") for s in spices]
    names = [n for n in names if n]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def format_meal_caption(meal: dict[str, Any]) -> str:
    """Instagram caption = ingredients + spices + detailed process + macros."""
    n = meal.get("nutrition") or {}
    name = meal["name"]
    mins = meal.get("time_mins", 15)
    lines = [
        f"{name} — quick & easy",
        f"~{mins} min · detailed recipe below",
        "",
        "Ingredients",
    ]
    for ing in meal.get("ingredients") or []:
        label = ing.get("label") or ing.get("key", "item")
        amount = ing.get("amount", "")
        lines.append(f"- {label}: {amount}" if amount else f"- {label}")

    spices = meal.get("spices") or []
    if spices:
        lines.append("")
        lines.append("Spices (do not skip)")
        for sp in spices:
            label = sp.get("label") or sp.get("key", "spice")
            amount = sp.get("amount", "")
            lines.append(f"- {label}: {amount}" if amount else f"- {label}")

    lines.append("")
    lines.append("How to (follow in order)")
    for i, step in enumerate(meal.get("steps") or [], 1):
        lines.append(f"{i}. {step}")

    lines.append("")
    lines.append("Macros (1 serving)")
    lines.append(
        f"{n.get('kcal', 0)} kcal · "
        f"{n.get('protein_g', 0)}g protein · "
        f"{n.get('carbs_g', 0)}g carbs · "
        f"{n.get('fat_g', 0)}g fat"
    )
    fiber = n.get("fiber_g")
    if fiber:
        lines.append(f"{fiber}g fiber")
    serving = n.get("serving")
    if serving:
        lines.append(f"Serving: {serving}")

    lines.append("")
    lines.append("Tip: measure the spices listed above — that is where the flavor comes from.")
    lines.append("")
    lines.append("Follow @nibthefridgegoblin")
    lines.append(
        "#easymeals #quickrecipes #mealprep #healthyrecipes "
        "#highprotein #homecooking #nibthefridgegoblin #fridgegoblin #reels"
    )
    return "\n".join(lines)
