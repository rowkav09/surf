"""
Procedurally generates 25 CS2-style knife skin textures using Pillow.
Each skin is a 512x512 PNG cached to assets/skins/<skin_id>.png.
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

SKIN_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'skins')
SIZE = 512


def _save(img, skin_id):
    os.makedirs(SKIN_DIR, exist_ok=True)
    path = os.path.join(SKIN_DIR, f'{skin_id}.png')
    img.save(path)
    return path


def _lerp_color(c0, c1, t):
    return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))


def _gradient_h(colors, size=SIZE):
    img = Image.new('RGB', (size, size))
    n = len(colors) - 1
    for x in range(size):
        t = x / (size - 1)
        seg = min(int(t * n), n - 1)
        lt = (t * n) - seg
        col = _lerp_color(colors[seg], colors[seg + 1], lt)
        for y in range(size):
            img.putpixel((x, y), col)
    return img


def _gradient_v(colors, size=SIZE):
    img = Image.new('RGB', (size, size))
    n = len(colors) - 1
    for y in range(size):
        t = y / (size - 1)
        seg = min(int(t * n), n - 1)
        lt = (t * n) - seg
        col = _lerp_color(colors[seg], colors[seg + 1], lt)
        for x in range(size):
            img.putpixel((x, y), col)
    return img


def _noise_layer(seed, scale=8, size=SIZE):
    rng = random.Random(seed)
    base = Image.new('L', (size // scale, size // scale))
    px = base.load()
    for y in range(size // scale):
        for x in range(size // scale):
            px[x, y] = rng.randint(0, 255)
    return base.resize((size, size), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))


def _blend(img_a, img_b, alpha):
    return Image.blend(img_a.convert('RGB'), img_b.convert('RGB'), alpha)


def _tint(img, color):
    overlay = Image.new('RGB', img.size, color)
    return Image.blend(img.convert('RGB'), overlay, 0.5)


# ─── Individual skin generators ───────────────────────────────────────────────

def _gen_vanilla():
    img = Image.new('RGB', (SIZE, SIZE), (160, 155, 150))
    draw = ImageDraw.Draw(img)
    for i in range(0, SIZE, 32):
        draw.line([(i, 0), (i, SIZE)], fill=(140, 135, 130), width=1)
    return img


def _gen_fade():
    return _gradient_h([(110, 0, 200), (210, 0, 160), (255, 80, 0), (255, 210, 0)])


def _doppler_base(seed, highlight_color, dark=(10, 10, 15)):
    noise = _noise_layer(seed, scale=6)
    base  = Image.new('RGB', (SIZE, SIZE), dark)
    hl    = Image.new('RGB', (SIZE, SIZE), highlight_color)
    mask  = noise
    return Image.composite(hl, base, mask)


def _gen_doppler_p1():
    return _doppler_base(1, (180, 60, 180))

def _gen_doppler_p2():
    return _doppler_base(2, (210, 80, 140))

def _gen_doppler_p3():
    return _doppler_base(3, (60, 80, 220))

def _gen_doppler_p4():
    return _doppler_base(4, (40, 40, 60))

def _gen_doppler_ruby():
    return _doppler_base(5, (220, 20, 20))

def _gen_doppler_sapphire():
    return _doppler_base(6, (10, 40, 230))

def _gen_doppler_blackpearl():
    img = _doppler_base(7, (60, 50, 90))
    teal = _doppler_base(8, (0, 120, 110))
    return Image.blend(img, teal, 0.3)

def _gen_gamma_doppler():
    return _doppler_base(9, (50, 200, 30))


def _gen_marble_fade():
    noise = _noise_layer(42, scale=4)
    fade  = _gradient_h([(150, 0, 200), (200, 50, 150), (255, 150, 0)])
    marble = Image.new('RGB', (SIZE, SIZE), (240, 240, 240))
    result = Image.composite(fade, marble, noise)
    return result.filter(ImageFilter.SMOOTH)


def _gen_tiger_tooth():
    img = Image.new('RGB', (SIZE, SIZE), (200, 160, 0))
    draw = ImageDraw.Draw(img)
    stripe_w = 28
    for i in range(-SIZE, SIZE * 2, stripe_w * 2):
        draw.polygon([
            (i, 0), (i + stripe_w, 0),
            (i + stripe_w + SIZE // 4, SIZE),
            (i + SIZE // 4, SIZE)
        ], fill=(15, 15, 15))
    return img.filter(ImageFilter.SMOOTH_MORE)


def _gen_crimson_web():
    img = Image.new('RGB', (SIZE, SIZE), (160, 10, 10))
    draw = ImageDraw.Draw(img)
    rng = random.Random(101)
    web_color = (30, 5, 5)
    for _ in range(12):
        cx = rng.randint(50, SIZE - 50)
        cy = rng.randint(50, SIZE - 50)
        for spoke in range(8):
            angle = spoke * math.pi / 4 + rng.uniform(-0.2, 0.2)
            max_r = rng.randint(80, 160)
            for r_step in range(20, max_r, 20):
                x1 = cx + int(r_step * math.cos(angle))
                y1 = cy + int(r_step * math.sin(angle))
                x2 = cx + int((r_step + 15) * math.cos(angle))
                y2 = cy + int((r_step + 15) * math.sin(angle))
                draw.line([(x1, y1), (x2, y2)], fill=web_color, width=2)
            for ring_r in range(30, max_r, 35):
                bbox = [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r]
                draw.arc(bbox, 0, 360, fill=web_color, width=1)
    return img.filter(ImageFilter.SMOOTH)


def _gen_case_hardened():
    base  = _gradient_h([(120, 90, 20), (40, 80, 180), (120, 50, 150)])
    noise = _noise_layer(55, scale=5)
    gold  = Image.new('RGB', (SIZE, SIZE), (180, 140, 30))
    return Image.composite(base, gold, noise).filter(ImageFilter.SMOOTH)


def _gen_slaughter():
    img  = Image.new('RGB', (SIZE, SIZE), (180, 15, 15))
    draw = ImageDraw.Draw(img)
    rng  = random.Random(22)
    for _ in range(30):
        x0 = rng.randint(0, SIZE)
        y0 = rng.randint(0, SIZE)
        x1 = x0 + rng.randint(-120, 120)
        y1 = y0 + rng.randint(-60, 60)
        draw.line([(x0, y0), (x1, y1)], fill=(240, 230, 220), width=rng.randint(1, 4))
    return img.filter(ImageFilter.SMOOTH)


def _gen_lore():
    base = _gradient_v([(180, 130, 20), (220, 175, 50), (160, 110, 15)])
    draw = ImageDraw.Draw(base)
    rng  = random.Random(33)
    for _ in range(60):
        x = rng.randint(10, SIZE - 10)
        y = rng.randint(10, SIZE - 10)
        r = rng.randint(4, 14)
        draw.ellipse([x - r, y - r, x + r, y + r], outline=(100, 70, 5), width=1)
    return base.filter(ImageFilter.SMOOTH)


def _gen_autotronic():
    base = Image.new('RGB', (SIZE, SIZE), (100, 8, 8))
    draw = ImageDraw.Draw(base)
    grid = 16
    for x in range(0, SIZE, grid):
        draw.line([(x, 0), (x, SIZE)], fill=(60, 5, 5), width=1)
    for y in range(0, SIZE, grid):
        draw.line([(0, y), (SIZE, y)], fill=(60, 5, 5), width=1)
    for x in range(0, SIZE, grid * 4):
        draw.line([(x, 0), (x, SIZE)], fill=(140, 20, 20), width=2)
    return base


def _gen_night_stripe():
    img  = Image.new('RGB', (SIZE, SIZE), (40, 42, 48))
    draw = ImageDraw.Draw(img)
    stripe_h = 18
    for y in range(0, SIZE, stripe_h * 2):
        draw.rectangle([0, y, SIZE, y + stripe_h], fill=(60, 63, 72))
    return img


def _gen_freehand():
    img  = Image.new('RGB', (SIZE, SIZE), (235, 225, 200))
    draw = ImageDraw.Draw(img)
    rng  = random.Random(77)
    for _ in range(80):
        x0 = rng.randint(0, SIZE)
        y0 = rng.randint(0, SIZE)
        x1 = x0 + rng.randint(-40, 40)
        y1 = y0 + rng.randint(-40, 40)
        col = (rng.randint(30, 80),) * 3
        draw.line([(x0, y0), (x1, y1)], fill=col, width=rng.randint(1, 3))
    return img.filter(ImageFilter.SMOOTH)


def _gen_stained():
    return _gradient_v([(130, 100, 60), (100, 80, 50), (80, 60, 35)])


def _gen_blue_steel():
    return _gradient_h([(60, 80, 130), (80, 100, 160), (50, 70, 120)]).filter(ImageFilter.SMOOTH)


def _gen_damascus_steel():
    base = Image.new('RGB', (SIZE, SIZE), (60, 60, 60))
    draw = ImageDraw.Draw(base)
    for i in range(0, SIZE, 8):
        wave = int(20 * math.sin(i * 0.15))
        draw.line([(0, i + wave), (SIZE, i + wave + int(SIZE * 0.05))],
                  fill=(100, 100, 100) if i % 16 == 0 else (40, 40, 40), width=3)
    return base.filter(ImageFilter.SMOOTH)


def _gen_rust_coat():
    noise = _noise_layer(88, scale=5)
    orange = Image.new('RGB', (SIZE, SIZE), (180, 80, 20))
    dark   = Image.new('RGB', (SIZE, SIZE), (100, 40, 10))
    return Image.composite(orange, dark, noise).filter(ImageFilter.SMOOTH)


def _gen_ultraviolet():
    return _gradient_h([(30, 0, 60), (60, 0, 90), (20, 0, 40)])


def _gen_bright_water():
    noise = _noise_layer(99, scale=7)
    teal  = Image.new('RGB', (SIZE, SIZE), (0, 160, 180))
    blue  = Image.new('RGB', (SIZE, SIZE), (0, 80, 160))
    return Image.composite(teal, blue, noise).filter(ImageFilter.SMOOTH)


# ─── Registry ─────────────────────────────────────────────────────────────────

_GENERATORS = {
    'vanilla':            _gen_vanilla,
    'fade':               _gen_fade,
    'doppler_p1':         _gen_doppler_p1,
    'doppler_p2':         _gen_doppler_p2,
    'doppler_p3':         _gen_doppler_p3,
    'doppler_p4':         _gen_doppler_p4,
    'doppler_ruby':       _gen_doppler_ruby,
    'doppler_sapphire':   _gen_doppler_sapphire,
    'doppler_blackpearl': _gen_doppler_blackpearl,
    'gamma_doppler':      _gen_gamma_doppler,
    'marble_fade':        _gen_marble_fade,
    'tiger_tooth':        _gen_tiger_tooth,
    'crimson_web':        _gen_crimson_web,
    'case_hardened':      _gen_case_hardened,
    'slaughter':          _gen_slaughter,
    'lore':               _gen_lore,
    'autotronic':         _gen_autotronic,
    'night_stripe':       _gen_night_stripe,
    'freehand':           _gen_freehand,
    'stained':            _gen_stained,
    'blue_steel':         _gen_blue_steel,
    'damascus_steel':     _gen_damascus_steel,
    'rust_coat':          _gen_rust_coat,
    'ultraviolet':        _gen_ultraviolet,
    'bright_water':       _gen_bright_water,
}


def get_skin_path(skin_id):
    path = os.path.join(SKIN_DIR, f'{skin_id}.png')
    if not os.path.exists(path):
        gen = _GENERATORS.get(skin_id)
        if gen:
            img = gen()
            _save(img, skin_id)
    return path


def generate_all():
    for skin_id, gen in _GENERATORS.items():
        path = os.path.join(SKIN_DIR, f'{skin_id}.png')
        if not os.path.exists(path):
            img = gen()
            _save(img, skin_id)


def apply_skin_to_node(nodepath, skin_id, loader):
    path = get_skin_path(skin_id)
    if os.path.exists(path):
        from panda3d.core import Texture
        tex = loader.loadTexture(path)
        if tex:
            nodepath.setTexture(tex, 1)
