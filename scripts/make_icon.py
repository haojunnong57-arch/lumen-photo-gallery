#!/usr/bin/env python3
"""Generate the Lumen app icon: two stacked liquid-glass photo plates floating
over a dark cinema gradient. Deterministic, no network, no external assets."""
from __future__ import annotations

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 4
W = 1024
N = W * S
OUT = os.path.join(os.path.dirname(__file__), "..", "Lumen", "Resources",
                   "Assets.xcassets", "AppIcon.appiconset", "AppIcon.png")

CORAL = (255, 107, 74)
AMBER = (255, 176, 32)
BLUE = (74, 158, 255)


def background() -> Image.Image:
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    cx, cy = N * 0.5, N * 0.48
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (N * 0.74)
    t = np.clip(r, 0, 1)[..., None]
    bg = np.array([22, 24, 31], np.float32) * (1 - t) + np.array([5, 6, 8], np.float32) * t

    def pool(px, py, spread, color, power, strength):
        rr = np.sqrt((xx - px) ** 2 + (yy - py) ** 2) / spread
        g = np.clip(1 - rr, 0, 1) ** power
        return np.array(color, np.float32) * (g[..., None] * strength)

    bg += pool(N * 0.21, N * 0.10, N * 0.62, CORAL, 2.4, 0.20)
    bg += pool(N * 0.84, N * 0.92, N * 0.58, BLUE, 2.6, 0.13)
    bg += pool(N * 0.52, N * 0.55, N * 0.40, AMBER, 2.8, 0.045)

    yv = (yy / N)[..., None]
    bg *= 1.0 - 0.16 * yv
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def glow(radius: int, color: tuple[int, int, int], strength: float) -> Image.Image:
    d = radius * 2
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32)
    r = np.sqrt((xx - radius) ** 2 + (yy - radius) ** 2) / radius
    a = np.clip(1 - r, 0, 1) ** 2.3 * strength
    arr = np.zeros((d, d, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = color
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def round_mask(size: tuple[int, int], radius: int) -> Image.Image:
    w, h = size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    return m


def plate(w: int, h: int, radius: int, content: Image.Image, angle: float) -> Image.Image:
    layer = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    x0 = (N - w) // 2
    y0 = (N - h) // 2
    mask = round_mask((w, h), radius)
    clipped = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    clipped.paste(content, (0, 0))
    clipped.putalpha(Image.composite(clipped.getchannel("A"), Image.new("L", (w, h), 0), mask))
    layer.alpha_composite(clipped, (x0, y0))
    return layer.rotate(angle, resample=Image.BICUBIC, center=(N // 2, N // 2))


def horizon_photo(w: int, h: int, rng: np.random.Generator) -> Image.Image:
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    c0 = np.array([26, 32, 49], np.float32)
    c1 = np.array([6, 8, 13], np.float32)
    sky = c0 * (1 - y) + c1 * y
    rgb = np.repeat(sky, w, axis=1)
    arr = np.concatenate([rgb, np.full((h, w, 1), 255, np.float32)], axis=2)
    photo = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    band = glow(int(w * 0.55), (255, 120, 70), 0.55).resize((w, int(h * 0.9)))
    photo.alpha_composite(band, (0, int(h * 0.34)))

    sun = glow(int(w * 0.19), (255, 213, 158), 0.95)
    photo.alpha_composite(sun, (int(w * 0.58 - sun.width / 2), int(h * 0.40 - sun.height / 2)))

    refl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(refl)
    for i in range(30):
        yy = int(h * 0.44) + i * int(h * 0.014)
        wdt = int(w * (0.18 - i * 0.005))
        x0 = int(w * 0.60) - wdt // 2 + int(rng.normal(0, w * 0.012))
        a = max(0, int(130 - i * 4))
        d.rounded_rectangle([x0, yy, x0 + wdt, yy + max(1, int(h * 0.0022))],
                            radius=2, fill=(255, 184, 128, a))
    photo.alpha_composite(refl.filter(ImageFilter.GaussianBlur(N * 0.0025)))

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    tint = np.clip(1 - (yy / h), 0, 1)[..., None]
    arr = np.array(photo, np.float32)
    arr[..., :3] = arr[..., :3] * (1 - 0.10 * tint) + np.array(BLUE, np.float32) * 0.10 * tint
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def main() -> None:
    rng = np.random.default_rng(7)
    canvas = background()

    card_w, card_h = int(N * 0.50), int(N * 0.62)
    radius = int(N * 0.055)

    bw, bh = card_w, card_h
    back_content = Image.new("RGBA", (bw, bh), (255, 255, 255, 22))
    bd = ImageDraw.Draw(back_content)
    bd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=radius,
                         outline=(255, 255, 255, 78), width=max(2, int(N * 0.003)))
    back_content.alpha_composite(glow(int(bw * 0.9), (90, 120, 255), 0.10),
                                 (int(-bw * 0.2), int(-bh * 0.25)))
    back = plate(bw, bh, radius, back_content, angle=12)
    back_offset = (int(-N * 0.055), int(-N * 0.040))

    fw, fh = card_w, card_h
    photo = horizon_photo(fw, fh, rng)

    yy, xx = np.mgrid[0:fh, 0:fw].astype(np.float32)
    r = np.sqrt(((xx / fw) - 0.5) ** 2 + ((yy / fh) - 0.5) ** 2) / 0.72
    v = np.clip(r, 0, 1)[..., None] * 0.55
    arr = np.array(photo, np.float32)
    arr[..., :3] *= 1 - v
    photo = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    metal = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    md = ImageDraw.Draw(metal)
    md.rounded_rectangle([0, 0, fw - 1, fh - 1], radius=radius,
                         outline=(255, 255, 255, 155), width=max(2, int(N * 0.0035)))
    metal = metal.filter(ImageFilter.GaussianBlur(N * 0.0006))
    photo.alpha_composite(metal)

    sweep = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    sd.polygon([(int(fw * -0.15), int(fh * 0.04)), (int(fw * 0.40), int(fh * -0.06)),
                (int(fw * 0.80), int(fh * 0.52)), (int(fw * 0.18), int(fh * 0.66))],
               fill=(255, 255, 255, 30))
    photo.alpha_composite(sweep.filter(ImageFilter.GaussianBlur(N * 0.012)))

    glint = glow(int(N * 0.035), (255, 245, 230), 0.9)
    photo.alpha_composite(glint, (int(fw * 0.14), int(fh * 0.13)))

    front = plate(fw, fh, radius, photo, angle=-7)
    front_offset = (int(N * 0.015), int(N * 0.006))

    shadow = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    for layer, off in ((back, back_offset), (front, front_offset)):
        a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(N * 0.032))
        a = a.point(lambda x: int(x * 0.62))
        dark = Image.new("RGBA", (N, N), (0, 0, 0, 255))
        dark.putalpha(a)
        shadow.alpha_composite(dark, (off[0] + int(N * 0.010), off[1] + int(N * 0.032)))
    canvas.alpha_composite(shadow)

    canvas.alpha_composite(back, back_offset)
    canvas.alpha_composite(front, front_offset)

    arr = np.array(canvas, np.float32)
    arr[..., :3] += rng.normal(0, 9, (N, N, 1))
    canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    r = np.sqrt(((xx / N) - 0.5) ** 2 + ((yy / N) - 0.5) ** 2) / 0.72
    v = np.clip(r, 0, 1) ** 1.8
    arr = np.array(canvas, np.float32)
    arr[..., :3] *= 1 - 0.55 * v[..., None]
    canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    final = canvas.convert("RGB").resize((W, W), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    final.save(OUT, "PNG", optimize=True)
    print("icon:", os.path.abspath(OUT), final.size)


if __name__ == "__main__":
    main()
