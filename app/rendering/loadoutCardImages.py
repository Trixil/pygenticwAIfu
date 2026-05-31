from pathlib import Path
from PIL import Image, ImageDraw
import random
import hashlib

BASE_WIDTH = 250
BASE_HEIGHT = 400
SCALE = 4

WIDTH = BASE_WIDTH * SCALE
HEIGHT = BASE_HEIGHT * SCALE

COLS = 5
ROWS = 8

PALETTES = [
    ["#1D3557", "#457B9D", "#A8DADC", "#F1FAEE", "#E63946"],
    ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"],
    ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"],
    ["#3A0CA3", "#4361EE", "#4CC9F0", "#F72585", "#B5179E"],
    ["#233D4D", "#FE7F2D", "#FCCA46", "#A1C181", "#619B8A"],
    ["#22223B", "#4A4E69", "#9A8C98", "#C9ADA7", "#F2E9E4"],
]


def _seed_from_text(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _pick_colors(rng: random.Random):
    palette = rng.choice(PALETTES)
    bg = _hex_to_rgb(rng.choice(palette))

    fg_candidates = [c for c in palette if c != "#{:02x}{:02x}{:02x}".format(*bg)]
    if not fg_candidates:
        fg_candidates = palette

    fg = _hex_to_rgb(rng.choice(fg_candidates))

    return bg, fg


def _draw_plus_pattern(draw, x0, y0, x1, y1, fg, rng):
    spacing = rng.randint(28, 40)
    arm = rng.randint(6, 10)
    width = rng.randint(4, 6)

    for y in range(y0 + spacing // 2, y1, spacing):
        for x in range(x0 + spacing // 2, x1, spacing):
            draw.line((x - arm, y, x + arm, y), fill=fg, width=width)
            draw.line((x, y - arm, x, y + arm), fill=fg, width=width)


def _draw_diag_stripes(draw, x0, y0, x1, y1, fg, rng):
    spacing = rng.randint(24, 34)
    width = rng.randint(6, 10)
    h = y1 - y0

    for offset in range(-h, (x1 - x0) + h, spacing):
        draw.line((x0 + offset, y1, x0 + offset + h, y0), fill=fg, width=width)


def _draw_vertical_stripes(draw, x0, y0, x1, y1, fg, rng):
    spacing = rng.randint(22, 30)
    width = rng.randint(6, 10)

    for x in range(x0 + spacing // 2, x1, spacing):
        draw.line((x, y0, x, y1), fill=fg, width=width)


def _draw_horizontal_stripes(draw, x0, y0, x1, y1, fg, rng):
    spacing = rng.randint(22, 30)
    width = rng.randint(6, 10)

    for y in range(y0 + spacing // 2, y1, spacing):
        draw.line((x0, y, x1, y), fill=fg, width=width)


def _draw_dots(draw, x0, y0, x1, y1, fg, rng):
    spacing = rng.randint(26, 36)
    r = rng.randint(6, 10)

    for y in range(y0 + spacing // 2, y1, spacing):
        for x in range(x0 + spacing // 2, x1, spacing):
            if rng.random() > 0.2:
                draw.ellipse((x - r, y - r, x + r, y + r), fill=fg)


def _draw_center_square(draw, x0, y0, x1, y1, fg, rng):
    size = rng.randint(22, 34)
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    draw.rectangle((cx - size, cy - size, cx + size, cy + size), fill=fg)


def _draw_corner_bracket(draw, x0, y0, x1, y1, fg, rng):
    width = rng.randint(5, 7)
    inset = rng.randint(10, 16)
    length = rng.randint(28, 38)

    # top-left only
    draw.line((x0 + inset, y0 + inset, x0 + inset + length, y0 + inset), fill=fg, width=width)
    draw.line((x0 + inset, y0 + inset, x0 + inset, y0 + inset + length), fill=fg, width=width)

    # optional bottom-right
    if rng.random() > 0.5:
        draw.line((x1 - inset - length, y1 - inset, x1 - inset, y1 - inset), fill=fg, width=width)
        draw.line((x1 - inset, y1 - inset - length, x1 - inset, y1 - inset), fill=fg, width=width)


def _draw_mini_blocks(draw, x0, y0, x1, y1, fg, rng):
    cell = rng.randint(12, 16)
    size = rng.randint(8, 12)

    for y in range(y0 + 10, y1 - size, cell):
        for x in range(x0 + 10, x1 - size, cell):
            if rng.random() > 0.35:
                draw.rectangle((x, y, x + size, y + size), fill=fg)


def _draw_x_marks(draw, x0, y0, x1, y1, fg, rng):
    spacing = rng.randint(26, 36)
    arm = rng.randint(8, 12)
    width = rng.randint(4, 6)

    for y in range(y0 + spacing // 2, y1, spacing):
        for x in range(x0 + spacing // 2, x1, spacing):
            draw.line((x - arm, y - arm, x + arm, y + arm), fill=fg, width=width)
            draw.line((x - arm, y + arm, x + arm, y - arm), fill=fg, width=width)


def _draw_half_split(draw, x0, y0, x1, y1, fg, rng):
    mode = rng.choice(["vertical", "horizontal", "diag"])
    if mode == "vertical":
        mid = (x0 + x1) // 2
        draw.rectangle((mid, y0, x1, y1), fill=fg)
    elif mode == "horizontal":
        mid = (y0 + y1) // 2
        draw.rectangle((x0, mid, x1, y1), fill=fg)
    else:
        draw.polygon([(x0, y0), (x1, y0), (x1, y1)], fill=fg)


PATTERNS = [
    _draw_plus_pattern,
    _draw_diag_stripes,
    _draw_vertical_stripes,
    _draw_horizontal_stripes,
    _draw_dots,
    _draw_center_square,
    _draw_corner_bracket,
    _draw_mini_blocks,
    _draw_x_marks,
    _draw_half_split,
]


def create_loadout_quilt_image(loadout_id: str, output_dir: str | Path) -> str:
    rng = random.Random(_seed_from_text(loadout_id))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), (18, 20, 30))
    draw = ImageDraw.Draw(img)

    tile_w = WIDTH // COLS
    tile_h = HEIGHT // ROWS
    pad = 4 * SCALE

    for row in range(ROWS):
        for col in range(COLS):
            x0 = col * tile_w + pad
            y0 = row * tile_h + pad
            x1 = (col + 1) * tile_w - pad
            y1 = (row + 1) * tile_h - pad

            bg, fg = _pick_colors(rng)

            # tile background
            draw.rounded_rectangle((x0, y0, x1, y1), radius=8 * SCALE, fill=bg)

            # inner safe area so patterns do not touch edges
            inner_pad = 8 * SCALE
            ix0 = x0 + inner_pad
            iy0 = y0 + inner_pad
            ix1 = x1 - inner_pad
            iy1 = y1 - inner_pad

            pattern = rng.choice(PATTERNS)
            pattern(draw, ix0, iy0, ix1, iy1, fg, rng)

    # downsample for smoother result
    img = img.resize((BASE_WIDTH, BASE_HEIGHT), Image.Resampling.LANCZOS)

    image_path = output_dir / f"{loadout_id}.png"
    img.save(image_path, format="PNG")

    return str(image_path)