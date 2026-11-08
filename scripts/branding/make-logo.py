"""Draws the Confluence Viewer logo and writes every file the build needs.

Two streams, violet and teal, meet and run on side by side inside a ring: a
confluence. The same polygons go to the SVGs and, supersampled, to the PNG,
ICO and ICNS, so all of them match.

Run from the repository root:  python scripts/branding/make-logo.py
Needs Pillow (pip install pillow). Writes into assets/branding/.
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw

OUT = os.path.join("assets", "branding")
SIZE = 720
C = SIZE / 2

NAVY = "#070B1F"
INDIGO = "#4F46E5"
VIOLET = "#8B5CF6"
VIOLET_LIGHT = "#A78BFA"
TEAL = "#5EEAD4"

DISC_R = 340  # navy background disc (colour logo only)
RING_R = 312  # centre line of the ring
RING_W = 36
CLIP_R = 280  # the streams stop inside this circle


def bezier(p, t):
    u = 1 - t
    x = u**3 * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t**3 * p[3][0]
    y = u**3 * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t**3 * p[3][1]
    return x, y


def tangent(p, t):
    u = 1 - t
    dx = 3 * u * u * (p[1][0] - p[0][0]) + 6 * u * t * (p[2][0] - p[1][0]) + 3 * t * t * (p[3][0] - p[2][0])
    dy = 3 * u * u * (p[1][1] - p[0][1]) + 6 * u * t * (p[2][1] - p[1][1]) + 3 * t * t * (p[3][1] - p[2][1])
    n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


def width(t):
    s = min(1.0, t * 1.6)
    s = s * s * (3 - 2 * s)
    return 50 + (66 - 50) * s


def stream(p, steps=120):
    """Outline of one stream: a band along the curve (the source end lies outside the ring)."""
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        x, y = bezier(p, t)
        tx, ty = tangent(p, t)
        nx, ny = -ty, tx
        h = width(t) / 2
        left.append((x + nx * h, y + ny * h))
        right.append((x - nx * h, y - ny * h))
    x0, y0 = p[0]
    tx, ty = tangent(p, 0)
    a0 = math.atan2(ty, tx)
    h = width(0) / 2
    cap = []
    for i in range(1, 24):
        a = a0 - math.pi / 2 - math.pi * i / 24
        cap.append((x0 + math.cos(a) * h, y0 + math.sin(a) * h))
    return left + right[::-1] + cap


LEFT = [(40, 190), (250, 240), (327, 380), (327, 700)]
RIGHT = [(SIZE - x, y) for x, y in LEFT]
STREAMS = [stream(LEFT), stream(RIGHT)]


def svg(kind):
    """kind: 'colour', 'white' or 'black'."""
    def path(poly):
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly) + " Z"

    if kind == "colour":
        fills = ("url(#ring)", VIOLET, TEAL)
        disc = f'  <circle cx="{C:g}" cy="{C:g}" r="{DISC_R}" fill="{NAVY}"/>\n'
        defs = (
            '    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">\n'
            f'      <stop offset="0" stop-color="{VIOLET_LIGHT}"/>\n'
            f'      <stop offset="1" stop-color="{INDIGO}"/>\n'
            "    </linearGradient>\n"
        )
    else:
        ink = "#ffffff" if kind == "white" else "#000000"
        fills = (ink, ink, ink)
        disc = ""
        defs = ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}">\n'
        "  <title>Confluence Viewer</title>\n"
        "  <defs>\n"
        f"{defs}"
        f'    <clipPath id="inside"><circle cx="{C:g}" cy="{C:g}" r="{CLIP_R}"/></clipPath>\n'
        "  </defs>\n"
        f"{disc}"
        f'  <circle cx="{C:g}" cy="{C:g}" r="{RING_R}" fill="none" stroke="{fills[0]}" stroke-width="{RING_W}"/>\n'
        '  <g clip-path="url(#inside)">\n'
        f'    <path fill="{fills[1]}" d="{path(STREAMS[0])}"/>\n'
        f'    <path fill="{fills[2]}" d="{path(STREAMS[1])}"/>\n'
        "  </g>\n"
        "</svg>\n"
    )


def raster(px):
    """Colour logo as an RGBA image of px x px (drawn 4x larger, then reduced)."""
    ss = 4
    big = px * ss
    k = big / SIZE

    def scaled(poly):
        return [(x * k, y * k) for x, y in poly]

    def circle_mask(r, inner=None):
        m = Image.new("L", (big, big), 0)
        d = ImageDraw.Draw(m)
        d.ellipse([(C - r) * k, (C - r) * k, (C + r) * k, (C + r) * k], fill=255)
        if inner is not None:
            d.ellipse([(C - inner) * k, (C - inner) * k, (C + inner) * k, (C + inner) * k], fill=0)
        return m

    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (big, big), NAVY), mask=circle_mask(DISC_R))

    # Ring: diagonal gradient from light violet (top left) to indigo.
    a = Image.new("RGBA", (big, big), VIOLET_LIGHT)
    b = Image.new("RGBA", (big, big), INDIGO)
    v = Image.linear_gradient("L").resize((big, big))
    grad = ImageChops.add(v.point(lambda x: x // 2), v.transpose(Image.Transpose.ROTATE_270).point(lambda x: x // 2))
    ring = Image.composite(b, a, grad)
    img.paste(ring, mask=circle_mask(RING_R + RING_W / 2, RING_R - RING_W / 2))

    clip = circle_mask(CLIP_R)
    for poly, colour in zip(STREAMS, (VIOLET, TEAL)):
        m = Image.new("L", (big, big), 0)
        ImageDraw.Draw(m).polygon(scaled(poly), fill=255)
        m = Image.composite(m, Image.new("L", (big, big), 0), clip)
        img.paste(Image.new("RGBA", (big, big), colour), mask=m)

    return img.resize((px, px), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for kind, name in (("colour", "confluence-logo.svg"), ("white", "confluence-logo-white.svg"), ("black", "confluence-logo-black.svg")):
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg(kind))
    big = raster(1024)
    big.resize((720, 720), Image.LANCZOS).save(os.path.join(OUT, "confluence-logo.png"), optimize=True)
    big.resize((256, 256), Image.LANCZOS).save(
        os.path.join(OUT, "confluence.ico"),
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    big.save(os.path.join(OUT, "confluence.icns"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
