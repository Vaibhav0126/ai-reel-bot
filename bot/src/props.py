from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from .fonts import get_font


def held_prop(item_key: str, size: int = 260) -> Image.Image:
    """
    Eye-catching cartoon prop meant to sit in / near Nib's hand.
    Thick outline + soft shadow for 'in frame' pop.
    """
    canvas = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = size // 2
    key = (item_key or "").lower()

    def outline_ellipse(box, fill, width=6):
        d.ellipse(box, fill=fill)
        d.ellipse(box, outline=(25, 30, 40, 255), width=width)

    def outline_round(box, fill, radius=22, width=6):
        d.rounded_rectangle(box, radius=radius, fill=fill)
        d.rounded_rectangle(box, radius=radius, outline=(25, 30, 40, 255), width=width)

    if key in {"yogurt", "cottage"}:
        outline_round((70, 40, size - 70, size - 25), (255, 255, 255, 255), 28)
        outline_ellipse((80, 25, size - 80, 95), (255, 210, 70, 255))
        outline_ellipse((100, 110, size - 100, size - 80), (255, 248, 210, 255), 4)
        d.rounded_rectangle((95, 145, size - 95, 175), radius=8, fill=(255, 110, 90, 255))
    elif key == "eggs":
        for dx, dy in ((-40, 15), (42, -5), (5, 50)):
            outline_ellipse((cx + dx - 48, cy + dy - 62, cx + dx + 48, cy + dy + 55), (255, 250, 230, 255))
            d.ellipse((cx + dx - 18, cy + dy - 40, cx + dx + 6, cy + dy - 12), fill=(255, 255, 255, 180))
    elif key in {"berries"}:
        colors = [(230, 40, 80), (120, 40, 180), (255, 70, 110), (150, 50, 200), (255, 90, 130)]
        spots = [(-40, -5), (38, -28), (8, 42), (-28, 48), (48, 38), (0, -48)]
        for i, ((dx, dy), col) in enumerate(zip(spots, colors * 2)):
            outline_ellipse((cx + dx - 34, cy + dy - 34, cx + dx + 34, cy + dy + 34), col + (255,))
            d.ellipse((cx + dx - 12, cy + dy - 16, cx + dx + 2, cy + dy - 2), fill=(255, 255, 255, 130))
    elif key == "creatine":
        outline_round((65, 35, size - 65, size - 30), (40, 45, 60, 255), 20)
        outline_round((85, 85, size - 85, 150), (255, 210, 70, 255), 12, 4)
        d.text((98, 98), "CREATINE", font=get_font(26), fill=(30, 30, 40))
        d.ellipse((100, 170, 140, 210), fill=(255, 255, 255, 50))
    elif key == "water":
        outline_round((100, 25, size - 100, size - 25), (120, 205, 245, 220), 26)
        d.rectangle((112, 18, size - 112, 55), fill=(255, 255, 255, 230))
        d.polygon(
            [(125, 85), (size - 125, 105), (size - 135, size - 70), (135, size - 55)],
            fill=(190, 235, 255, 150),
        )
    elif key == "spinach":
        # Fresh leafy spinach bunch
        leaves = [
            ((-25, -10), 55, (70, 160, 70)),
            ((20, -25), 50, (90, 190, 80)),
            ((35, 15), 48, (60, 140, 60)),
            ((-5, 25), 52, (100, 200, 90)),
            ((-40, 20), 46, (80, 170, 75)),
        ]
        for (dx, dy), rad, col in leaves:
            outline_ellipse(
                (cx + dx - rad // 2, cy + dy - rad // 2, cx + dx + rad // 2, cy + dy + rad // 2),
                col + (255,),
                4,
            )
            d.ellipse(
                (cx + dx - 8, cy + dy - 12, cx + dx + 4, cy + dy),
                fill=(180, 255, 160, 100),
            )
        d.rectangle((cx - 8, cy + 40, cx + 8, cy + 85), fill=(90, 140, 60, 255))
    elif key == "frozen":
        outline_round((50, 35, size - 50, size - 30), (70, 185, 230, 255), 24)
        d.rectangle((60, 50, size - 60, 105), fill=(255, 255, 255, 235))
        d.text((78, 58), "FROZEN", font=get_font(32), fill=(30, 90, 140))
        bits = [((-35, 35), (90, 200, 70)), ((25, 20), (255, 130, 50)), ((45, 60), (255, 220, 70)),
                ((-15, 75), (110, 210, 80)), ((30, 95), (255, 150, 60))]
        for (dx, dy), col in bits:
            outline_ellipse((cx + dx - 20, cy + dy - 16, cx + dx + 20, cy + dy + 16), col + (255,), 3)
    elif key == "banana":
        d.pieslice((25, 45, size - 15, size - 15), 200, 345, fill=(255, 220, 60, 255))
        d.pieslice((25, 45, size - 15, size - 15), 200, 345, outline=(25, 30, 40, 255), width=6)
        outline_ellipse((size - 100, 40, size - 55, 85), (70, 150, 60, 255), 4)
    elif key == "milk":
        d.polygon(
            [(95, 50), (size - 95, 50), (size - 65, size - 25), (65, size - 25)],
            fill=(255, 255, 255, 255),
        )
        d.line([(95, 50), (size - 95, 50), (size - 65, size - 25), (65, size - 25), (95, 50)],
               fill=(25, 30, 40, 255), width=6)
        d.polygon([(95, 50), (size // 2, 22), (size - 95, 50)], fill=(255, 210, 70, 255))
        outline_round((115, 100, size - 115, 150), (80, 170, 255, 255), 10, 4)
    elif key == "hummus":
        outline_ellipse((40, 50, size - 40, size - 30), (255, 195, 85, 255))
        outline_ellipse((85, 100, size - 85, size - 80), (230, 155, 45, 255), 4)
        outline_ellipse((110, 120, 150, 155), (90, 180, 70, 255), 3)
    elif key == "chicken":
        # Clear leftover container with chicken — readable in-frame
        outline_round((45, 70, size - 45, size - 25), (255, 255, 255, 255), 18)
        outline_round((55, 40, size - 55, 85), (230, 240, 245, 255), 14, 4)
        # chicken pieces
        outline_ellipse((70, 110, 160, 175), (255, 180, 110, 255), 4)
        outline_ellipse((130, 125, 220, 195), (255, 165, 95, 255), 4)
        outline_ellipse((95, 155, 175, 210), (240, 150, 90, 255), 4)
        d.ellipse((85, 120, 110, 140), fill=(255, 230, 180, 200))
        d.rounded_rectangle((85, 95, size - 85, 118), radius=6, fill=(255, 120, 80, 255))
        d.text((100, 96), "LEFTOVERS", font=get_font(18), fill=(255, 255, 255))
    elif key == "tofu":
        outline_round((55, 70, size - 55, size - 40), (255, 255, 245, 255), 18)
        for yy in (125, 165, 205):
            d.line([(85, yy), (size - 85, yy)], fill=(220, 215, 200, 255), width=5)
        outline_round((90, 90, size - 90, 120), (255, 180, 70, 255), 8, 3)
    elif key == "soda":
        outline_round((100, 30, size - 100, size - 25), (230, 45, 65, 255), 22)
        d.rectangle((110, 70, size - 110, 125), fill=(255, 255, 255, 240))
        for dx, dy in ((-15, 20), (20, 45), (0, 70)):
            d.ellipse((cx + dx, cy + dy, cx + dx + 14, cy + dy + 14), fill=(255, 255, 255, 140))
    elif key == "oats":
        outline_ellipse((40, 55, size - 40, size - 30), (230, 175, 90, 255))
        outline_ellipse((75, 95, size - 75, size - 75), (200, 140, 55, 255), 4)
    elif key == "kimchi":
        outline_round((65, 40, size - 65, size - 25), (255, 75, 70, 255), 24)
        outline_ellipse((90, 90, size - 90, size - 75), (255, 140, 95, 255), 4)
    elif key == "rice":
        outline_ellipse((40, 80, size - 40, size - 30), (255, 250, 230, 255))
        for i in range(14):
            ang = i * 0.9
            outline_ellipse(
                (
                    cx + int(math.cos(ang) * 48) - 7,
                    cy + 15 + int(math.sin(ang) * 20) - 5,
                    cx + int(math.cos(ang) * 48) + 7,
                    cy + 15 + int(math.sin(ang) * 20) + 5,
                ),
                (255, 255, 255, 230),
                2,
            )
    elif key == "pickles":
        outline_round((105, 25, size - 105, size - 20), (70, 165, 80, 255), 28)
        for yy in (85, 135, 185):
            outline_ellipse((120, yy, size - 120, yy + 30), (150, 210, 100, 220), 3)
    elif key == "box":
        outline_round((45, 65, size - 45, size - 35), (255, 140, 70, 255), 16)
        outline_round((55, 80, size - 55, 125), (255, 245, 225, 255), 10, 3)
        d.text((78, 88), "PROTEIN", font=get_font(28), fill=(170, 55, 20))
    elif key == "moon":
        outline_ellipse((50, 50, size - 50, size - 50), (255, 235, 160, 255))
        d.ellipse((100, 40, size - 20, size - 80), fill=(40, 120, 140, 255))
    elif key == "garlic":
        outline_ellipse((70, 70, size - 70, size - 50), (245, 240, 220, 255))
        for dx in (-25, 0, 25):
            outline_ellipse((cx + dx - 28, cy - 10, cx + dx + 28, cy + 55), (250, 245, 225, 255), 4)
        d.rectangle((cx - 6, 40, cx + 6, 75), fill=(120, 170, 80, 255))
    elif key == "honey":
        outline_round((95, 55, size - 95, size - 30), (255, 180, 40, 255), 18)
        outline_round((110, 35, size - 110, 70), (200, 140, 40, 255), 10, 4)
        d.polygon([(cx - 20, 90), (cx + 20, 90), (cx, 140)], fill=(255, 220, 100, 220))
    elif key == "tomato":
        outline_ellipse((55, 60, size - 55, size - 40), (230, 55, 55, 255))
        outline_ellipse((cx - 18, 45, cx + 18, 80), (70, 160, 70, 255), 4)
        d.ellipse((90, 90, 130, 120), fill=(255, 180, 160, 120))
    elif key == "cheese":
        outline_round((50, 80, size - 50, size - 40), (255, 210, 90, 255), 16)
        d.polygon([(50, 80), (size // 2, 40), (size - 50, 80)], fill=(255, 225, 120, 255))
        d.line([(50, 80), (size // 2, 40), (size - 50, 80)], fill=(25, 30, 40, 255), width=5)
        for dx, dy in ((-30, 20), (20, 35), (5, 55)):
            outline_ellipse((cx + dx - 12, cy + dy - 10, cx + dx + 12, cy + dy + 10), (240, 180, 60, 255), 3)
    elif key == "tuna":
        outline_round((55, 70, size - 55, size - 40), (180, 200, 210, 255), 16)
        outline_round((70, 45, size - 70, 90), (90, 130, 160, 255), 12, 4)
        d.text((95, 120), "TUNA", font=get_font(32), fill=(40, 60, 80))
    elif key == "avocado":
        outline_ellipse((60, 45, size - 60, size - 35), (90, 160, 70, 255))
        outline_ellipse((95, 85, size - 95, size - 75), (200, 210, 90, 255), 4)
        outline_ellipse((cx - 22, cy - 10, cx + 22, cy + 35), (90, 55, 30, 255), 4)
    elif key == "soy":
        left, right = int(size * 0.32), int(size * 0.68)
        outline_round((left, int(size * 0.12), right, int(size * 0.9)), (40, 35, 40, 255), 18)
        outline_round((left + 12, int(size * 0.28), right - 12, int(size * 0.48)), (255, 245, 230, 255), 8, 3)
        d.text((cx - 22, int(size * 0.55)), "SOY", font=get_font(26), fill=(240, 220, 180))
    elif key == "tortilla":
        outline_ellipse((35, 45, size - 35, size - 35), (240, 200, 130, 255))
        outline_ellipse((70, 80, size - 70, size - 70), (230, 180, 100, 200), 3)
    elif key == "shrimp":
        d.arc((40, 50, size - 40, size - 40), 20, 200, fill=(255, 130, 100, 255), width=28)
        outline_ellipse((size - 110, 55, size - 55, 110), (255, 150, 120, 255), 4)
        for i in range(4):
            yy = 90 + i * 28
            outline_ellipse((70, yy, 130, yy + 22), (255, 160, 130, 255), 3)
    elif key == "noodles":
        for i, col in enumerate([(255, 210, 90), (240, 180, 70), (255, 225, 120)]):
            y0 = 60 + i * 18
            d.arc((40, y0, size - 40, y0 + 120), 0, 180, fill=col + (255,), width=10)
        outline_ellipse((50, size - 90, size - 50, size - 35), (230, 200, 140, 255), 4)
    elif key == "butter":
        outline_round((55, 90, size - 55, size - 50), (255, 230, 120, 255), 14)
        outline_round((70, 70, size - 70, 105), (255, 245, 180, 255), 10, 4)
    elif key == "bread":
        outline_round((45, 70, size - 45, size - 40), (220, 170, 100, 255), 20)
        outline_ellipse((55, 45, size - 55, 110), (235, 195, 130, 255), 5)
        d.ellipse((90, 100, 120, 125), fill=(200, 140, 70, 180))
        d.ellipse((150, 130, 185, 160), fill=(200, 140, 70, 160))
    elif key == "cucumber":
        outline_round((90, 30, size - 90, size - 25), (90, 180, 90, 255), 30)
        for yy in (70, 120, 170):
            d.ellipse((110, yy, size - 110, yy + 18), fill=(140, 210, 120, 200))
    elif key == "salmon":
        outline_ellipse((40, 80, size - 40, size - 50), (255, 140, 110, 255))
        d.arc((60, 70, size - 60, size - 40), 200, 340, fill=(255, 180, 150, 255), width=8)
        outline_ellipse((size - 100, 95, size - 55, 140), (255, 160, 130, 255), 3)
    elif key == "lemon":
        outline_ellipse((55, 55, size - 55, size - 45), (255, 230, 70, 255))
        outline_ellipse((90, 90, size - 90, size - 80), (255, 245, 140, 255), 3)
        d.rectangle((cx - 5, 40, cx + 5, 65), fill=(100, 160, 60, 255))
    elif key == "oil":
        left, right = int(size * 0.34), int(size * 0.66)
        outline_round((left, int(size * 0.16), right, int(size * 0.88)), (200, 220, 120, 230), 22)
        outline_round((left + 12, int(size * 0.1), right - 12, int(size * 0.22)), (180, 160, 100, 255), 8, 3)
        d.polygon(
            [
                (left + 20, int(size * 0.35)),
                (right - 20, int(size * 0.38)),
                (right - 24, int(size * 0.75)),
                (left + 24, int(size * 0.78)),
            ],
            fill=(230, 240, 150, 160),
        )
    elif key == "beef":
        outline_round((50, 75, size - 50, size - 40), (160, 70, 55, 255), 18)
        outline_ellipse((80, 100, size - 80, size - 80), (190, 90, 70, 255), 4)
        d.ellipse((100, 120, 140, 150), fill=(220, 140, 120, 160))
    elif key == "basil":
        leaves = [((-20, -5), 50, (60, 150, 70)), ((25, -15), 45, (80, 180, 90)), ((5, 25), 48, (50, 130, 60))]
        for (dx, dy), rad, col in leaves:
            outline_ellipse(
                (cx + dx - rad // 2, cy + dy - rad // 2, cx + dx + rad // 2, cy + dy + rad // 2),
                col + (255,),
                4,
            )
        d.rectangle((cx - 5, cy + 30, cx + 5, cy + 75), fill=(70, 120, 50, 255))
    elif key in {"spices", "spice", "paprika", "cumin", "oregano", "ginger", "cinnamon", "chili", "sesame", "vanilla", "sugar"}:
        # Spice jar / shaker (proportional so size=200 still works)
        left, right = int(size * 0.30), int(size * 0.70)
        outline_round((left, int(size * 0.22), right, int(size * 0.88)), (240, 235, 220, 255), 16)
        outline_round((left + 12, int(size * 0.12), right - 12, int(size * 0.28)), (180, 100, 60, 255), 10, 4)
        fill = {
            "paprika": (220, 70, 50),
            "chili": (200, 40, 40),
            "cumin": (180, 130, 70),
            "cinnamon": (140, 80, 40),
            "oregano": (90, 140, 70),
            "ginger": (210, 160, 90),
            "sesame": (230, 210, 160),
            "vanilla": (245, 230, 190),
            "sugar": (255, 250, 245),
        }.get(key, (200, 120, 60))
        outline_ellipse((left + 18, int(size * 0.42), right - 18, int(size * 0.72)), fill + (255,), 4)
        d.text((cx - 28, int(size * 0.78)), key[:6].upper(), font=get_font(22), fill=(40, 40, 40))
    elif key in {"salt", "pepper"}:
        left, right = int(size * 0.32), int(size * 0.68)
        outline_round(
            (left, int(size * 0.15), right, int(size * 0.88)),
            (245, 245, 245, 255) if key == "salt" else (50, 45, 45, 255),
            20,
        )
        outline_ellipse((left + 16, int(size * 0.2), right - 16, int(size * 0.36)), (200, 200, 200, 255), 3)
        dots = (30, 30, 30, 255) if key == "salt" else (230, 230, 230, 255)
        for dx, dy in ((-15, 20), (10, 40), (-5, 55), (20, 60)):
            d.ellipse((cx + dx, cy + dy, cx + dx + 8, cy + dy + 8), fill=dots)
        d.text(
            (cx - 30, int(size * 0.78)),
            key.upper(),
            font=get_font(24),
            fill=(40, 40, 40) if key == "salt" else (240, 240, 240),
        )
    elif key == "plate":
        outline_ellipse((30, 50, size - 30, size - 30), (245, 245, 240, 255))
        outline_ellipse((70, 90, size - 70, size - 70), (230, 230, 220, 255), 4)
        outline_ellipse((95, 110, size - 95, size - 95), (255, 180, 100, 255), 4)
        outline_ellipse((110, 130, size - 110, size - 110), (90, 170, 80, 255), 3)
    else:
        outline_round((55, 55, size - 55, size - 40), (255, 210, 70, 255), 26)
        d.text((cx - 18, cy - 24), "?", font=get_font(64), fill=(40, 40, 40))

    # Soft drop shadow under prop
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((30, size - 10, size + 10, size + 35), fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(im, (20, 10))
    return canvas
