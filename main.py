#!/usr/bin/env python3
"""
Make the coolest art — make.fun bounty "coolest-art-01"
https://make.fun/bounty/coolest-art-01

A deterministic program that paints one piece of art and writes it to
/output/entry.png (override with the ENTRY_PATH environment variable).

Scene: "Aurora over a glass lake" — a ringed planet glowing above a
star-filled indigo sky, three aurora ribbons, twin mountain ridges and a
mirror-still lake that reflects the whole sky.

Deterministic: fixed seed, no network, no wall clock, no timestamps in the
PNG. Running the program twice produces byte-identical output.

Stdlib only (a hand-written zlib PNG encoder), so it runs on any Python 3.13
with no third-party packages.

License: MIT
"""

import math
import os
import random
import struct
import zlib

W, H = 1024, 1024
SEED = 20261113


# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def _i(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, r, g, b):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._i(x, y)
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def blend(self, x, y, r, g, b, a):
        """Alpha-blend colour (r,g,b) with alpha a (0..255) over the pixel."""
        if 0 <= x < self.w and 0 <= y < self.h and a > 0:
            i = self._i(x, y)
            if a >= 255:
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b
            else:
                ia = 255 - a
                self.px[i] = (r * a + self.px[i] * ia) // 255
                self.px[i + 1] = (g * a + self.px[i + 1] * ia) // 255
                self.px[i + 2] = (b * a + self.px[i + 2] * ia) // 255

    def add(self, x, y, r, g, b, a):
        """Additive glow: pixel += colour * a/255, clamped at 255."""
        if 0 <= x < self.w and 0 <= y < self.h and a > 0:
            i = self._i(x, y)
            v = self.px[i] + (r * a) // 255
            self.px[i] = 255 if v > 255 else v
            v = self.px[i + 1] + (g * a) // 255
            self.px[i + 1] = 255 if v > 255 else v
            v = self.px[i + 2] + (b * a) // 255
            self.px[i + 2] = 255 if v > 255 else v

    def fill_row(self, y, color):
        if 0 <= y < self.h:
            i = y * self.w * 3
            self.px[i:i + self.w * 3] = bytes(color) * self.w

    def vgrad(self, y0, y1, c0, c1):
        """Vertical linear gradient between two RGB colours."""
        for y in range(max(0, y0), min(self.h, y1)):
            t = (y - y0) / max(1, y1 - y0 - 1)
            self.fill_row(y, tuple(
                int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3)))

    def disc(self, cx, cy, r, color, alpha=255):
        """Filled disc with 1px antialiased edge."""
        x0 = max(0, int(cx - r - 1))
        x1 = min(self.w - 1, int(cx + r + 1))
        y0 = max(0, int(cy - r - 1))
        y1 = min(self.h - 1, int(cy + r + 1))
        for y in range(y0, y1 + 1):
            dy = y - cy
            for x in range(x0, x1 + 1):
                dx = x - cx
                d = math.sqrt(dx * dx + dy * dy)
                cov = r + 0.5 - d
                if cov <= 0:
                    continue
                a = alpha if cov >= 1 else int(alpha * cov)
                self.blend(x, y, color[0], color[1], color[2], a)

    def ellipse(self, cx, cy, rx, ry, color, alpha=255):
        """Filled ellipse with 1px antialiased edge."""
        x0 = max(0, int(cx - rx - 1))
        x1 = min(self.w - 1, int(cx + rx + 1))
        y0 = max(0, int(cy - ry - 1))
        y1 = min(self.h - 1, int(cy + ry + 1))
        for y in range(y0, y1 + 1):
            ny = (y - cy) / ry
            for x in range(x0, x1 + 1):
                nx = (x - cx) / rx
                d = math.sqrt(nx * nx + ny * ny)
                cov = 1.0 + 0.5 / max(rx, ry) - d
                if cov <= 0:
                    continue
                a = alpha if cov >= 1 else int(alpha * cov)
                self.blend(x, y, color[0], color[1], color[2], a)

    def line(self, x0, y0, x1, y1, color, alpha=255, width=1):
        """Line drawn as a chain of small discs (round caps)."""
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(steps + 1):
            t = i / steps
            self.disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t,
                      width / 2.0, color, alpha)


def poly_fill(c, pts, color, alpha=255):
    """Scanline fill of a simple polygon given as [(x, y), ...]."""
    ys = [p[1] for p in pts]
    y0, y1 = int(min(ys)), int(max(ys))
    n = len(pts)
    for y in range(max(0, y0), min(c.h, y1 + 1)):
        xs = []
        for i in range(n):
            x1, yy1 = pts[i]
            x2, yy2 = pts[(i + 1) % n]
            if (yy1 <= y < yy2) or (yy2 <= y < yy1):
                t = (y - yy1) / (yy2 - yy1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                c.blend(x, y, color[0], color[1], color[2], alpha)


def ellipse_arc_points(cx, cy, rx, ry, angle_deg, t0, t1, steps):
    """Points along a rotated ellipse arc (angles in radians)."""
    th = math.radians(angle_deg)
    ct, st = math.cos(th), math.sin(th)
    pts = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        x = rx * math.cos(t)
        y = ry * math.sin(t)
        pts.append((cx + x * ct - y * st, cy + x * st + y * ct))
    return pts


# ------------------------------------------------------------------- png ----
def write_png(path, w, h, px):
    """Minimal deterministic PNG encoder (RGB, 8-bit, Up filter, zlib-9)."""
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    raw = bytearray()
    stride = w * 3
    prev = bytes(stride)
    for y in range(h):
        row = bytes(px[y * stride:(y + 1) * stride])
        raw.append(2)  # Up filter
        raw += bytes((a - b) & 0xff for a, b in zip(row, prev))
        prev = row
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


# ----------------------------------------------------------------- scene ----
def draw_aurora(c, base_y, amp1, f1, p1, amp2, f2, p2, half_h, color,
                strength, y_scale=1.0, y_off=0.0, alpha_mul=1.0):
    """One glowing aurora ribbon; additive, with a Gaussian vertical falloff.

    y_scale / y_off let the same band be re-drawn squashed in the lake as a
    reflection (y_off is the horizon line for the mirror).
    """
    # Precompute the vertical falloff LUT once (softer edges than a hard cut).
    lut = []
    for dy in range(-half_h, half_h + 1):
        u = dy / half_h
        fall = math.exp(-u * u * 3.0)
        lut.append((dy, fall))
    for x in range(c.w):
        cy = (base_y + amp1 * math.sin(x * f1 + p1)
              + amp2 * math.sin(x * f2 + p2))
        # Fade the ribbon out near the left/right edges.
        fx = min(1.0, x / 90.0, (c.w - 1 - x) / 90.0)
        if fx <= 0:
            continue
        for dy, fall in lut:
            y = int(y_off + (cy - y_off + dy) * y_scale)
            # tiny deterministic dither breaks up visible contour banding
            dith = ((x * 374761393 + y * 668265263) % 17) - 8
            a = int(255 * strength * fall * fx * alpha_mul) + dith
            if a > 0:
                c.add(x, y, color[0], color[1], color[2], a)


def ridge(c, horizon, fn, c_top, c_bot, snow=False):
    """A mountain ridge: fn(x) gives the ridge height above the horizon."""
    for x in range(c.w):
        hgt = fn(x)
        top = int(horizon - hgt)
        for y in range(top, horizon):
            t = (y - top) / max(1, hgt)
            col = tuple(int(c_top[k] + (c_bot[k] - c_top[k]) * t)
                        for k in range(3))
            if snow and y - top < 12:
                s = 1.0 - (y - top) / 12.0
                col = tuple(int(col[k] + (210 - col[k]) * s * 0.55)
                            for k in range(3))
            c.set(x, y, col[0], col[1], col[2])


def main():
    rng = random.Random(SEED)
    c = Canvas(W, H)
    horizon = 640

    # --- sky ---
    c.vgrad(0, 300, (7, 9, 34), (26, 22, 78))
    c.vgrad(300, 560, (26, 22, 78), (62, 30, 94))
    c.vgrad(560, horizon, (62, 30, 94), (148, 54, 118))

    # --- stars ---
    for _ in range(650):
        x = rng.randrange(W)
        y = rng.randrange(0, 600)
        b = rng.randint(150, 255)
        tone = rng.choice([(255, 255, 255), (220, 230, 255),
                           (255, 240, 220), (200, 220, 255)])
        r = 1 if rng.random() < 0.8 else 2
        if r == 1:
            c.blend(x, y, tone[0], tone[1], tone[2], b)
        else:
            c.disc(x, y, 1.6, tone, int(b * 0.9))
    # a few bright stars with a sparkle cross
    for _ in range(14):
        x = rng.randrange(40, W - 40)
        y = rng.randrange(30, 480)
        c.disc(x, y, 2.2, (255, 255, 255), 255)
        c.line(x - 7, y, x + 7, y, (255, 255, 255), 150, 1)
        c.line(x, y - 7, x, y + 7, (255, 255, 255), 150, 1)

    # --- aurora ribbons ---
    draw_aurora(c, 150, 55, 0.006, 1.1, 22, 0.014, 3.0, 70,
                (86, 255, 178), 0.85)
    draw_aurora(c, 295, 70, 0.005, 4.4, 30, 0.012, 0.7, 95,
                (64, 224, 220), 0.70)
    draw_aurora(c, 435, 60, 0.007, 2.2, 26, 0.016, 5.1, 80,
                (168, 110, 255), 0.60)

    # --- ringed planet (upper right) ---
    pcx, pcy, pr = 740, 205, 86
    # warm halo
    for rr, aa in ((135, 14), (115, 22), (98, 30)):
        c.disc(pcx, pcy, rr, (255, 200, 120), aa)
    # back half of the ring (annulus, upper arc)
    outer = ellipse_arc_points(pcx, pcy, 158, 38, -16, math.pi, 2 * math.pi, 90)
    inner = ellipse_arc_points(pcx, pcy, 132, 28, -16, 2 * math.pi, math.pi, 90)
    poly_fill(c, outer + inner, (222, 198, 158), 210)
    # planet disc with directional light (lit from the upper right)
    for y in range(int(pcy - pr - 1), int(pcy + pr + 2)):
        for x in range(int(pcx - pr - 1), int(pcx + pr + 2)):
            dx = (x - pcx) / pr
            dy = (y - pcy) / pr
            d = math.sqrt(dx * dx + dy * dy)
            if d > 1:
                continue
            dot = dx * 0.65 - dy * 0.65
            bright = (0.62 + 0.38 * dot) * (0.82 + 0.18 * (1 - d))
            base = (255 - 28 * d, 232 - 58 * d, 182 - 62 * d)
            cov = pr + 0.5 - d * pr
            a = 255 if cov >= 1 else int(255 * cov)
            c.blend(x, y, int(base[0] * bright), int(base[1] * bright),
                    int(base[2] * bright), a)
    # soft horizontal cloud band across the planet
    for t in range(0, 628):
        a = t / 100.0
        x = pcx + 62 * math.cos(a)
        y = pcy + 18 * math.sin(a) - 12
        c.disc(x, y, 3.0, (240, 190, 140), 60)
    # front half of the ring (lower arc, in front of the planet)
    outer = ellipse_arc_points(pcx, pcy, 158, 38, -16, 0, math.pi, 90)
    inner = ellipse_arc_points(pcx, pcy, 132, 28, -16, math.pi, 0, 90)
    poly_fill(c, outer + inner, (232, 208, 168), 235)

    # --- shooting star (upper left) ---
    for i in range(80):
        t = i / 79.0
        x = 140 + 260 * t
        y = 100 + 130 * t
        c.add(int(x), int(y), 255, 255, 255, int(255 * (1 - t)))
    c.disc(140, 100, 4.0, (255, 255, 255), 255)

    # --- mountain ridges ---
    ridge(c, horizon,
          lambda x: 55 + 45 * math.sin(x * 0.008 + 1.2)
          + 25 * math.sin(x * 0.021 + 3.9) + 12 * math.sin(x * 0.043 + 0.5),
          (52, 42, 102), (34, 26, 76), snow=True)
    ridge(c, horizon,
          lambda x: 25 + 35 * math.sin(x * 0.011 + 4.2)
          + 18 * math.sin(x * 0.027 + 1.1),
          (20, 15, 50), (12, 10, 34))

    # --- lake ---
    c.vgrad(horizon, H, (128, 58, 108), (8, 10, 34))
    # aurora reflections (squashed, dimmer, rippled)
    draw_aurora(c, 150, 55, 0.006, 1.1, 22, 0.014, 3.0, 70,
                (86, 255, 178), 0.85, y_scale=0.42, y_off=horizon,
                alpha_mul=0.38)
    draw_aurora(c, 295, 70, 0.005, 4.4, 30, 0.012, 0.7, 95,
                (64, 224, 220), 0.70, y_scale=0.42, y_off=horizon,
                alpha_mul=0.32)
    draw_aurora(c, 435, 60, 0.007, 2.2, 26, 0.016, 5.1, 80,
                (168, 110, 255), 0.60, y_scale=0.42, y_off=horizon,
                alpha_mul=0.30)
    # planet reflection: a narrower, golden vertical smear under the planet
    for y in range(horizon + 6, 930):
        t = (y - horizon) / (930 - horizon)
        wob = 4 * math.sin(y * 0.06)
        half = int(40 * (1 - t) + 8)
        cx = int(pcx + wob)
        a = int(95 * (1 - t))
        for x in range(cx - half, cx + half + 1):
            c.add(x, y, 255, 208, 135, a)
    # reflected stars
    for _ in range(60):
        x = rng.randrange(W)
        y = rng.randrange(horizon + 20, 990)
        c.blend(x, y, 220, 225, 255, rng.randint(50, 130))
    # ripple lines
    for _ in range(42):
        y = rng.randrange(horizon + 15, H - 5)
        x = rng.randrange(0, W - 200)
        ln = rng.randrange(60, 300)
        a = rng.randint(8, 22)
        for xx in range(x, x + ln):
            c.blend(xx, y, 200, 210, 255, a)

    # --- pine silhouettes on the near shore ---
    def pine(x, base, hgt, wdt):
        poly_fill(c, [(x, base - hgt), (x - wdt // 2, base),
                      (x + wdt // 2, base)], (6, 8, 26), 255)
        poly_fill(c, [(x, base - hgt * 0.62), (x - wdt // 2 - 4, base - hgt * 0.3),
                      (x + wdt // 2 + 4, base - hgt * 0.3)], (6, 8, 26), 255)

    for (x, b, hgt, wdt) in ((70, 1024, 130, 70), (150, 1024, 95, 56),
                             (880, 1024, 115, 62), (955, 1024, 88, 52),
                             (905, 1024, 60, 40)):
        pine(x, b, hgt, wdt)

    out = os.environ.get("ENTRY_PATH", "/output/entry.png")
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    write_png(out, W, H, c.px)
    print("wrote", out)


if __name__ == "__main__":
    main()
