#!/usr/bin/env python3
"""news-image-01: a front-page montage of Friday 13 November 2026 world news.

Pure Python 3.13 stdlib. No network, no randomness, no time dependence:
every run writes the same bytes to $MAKEFUN_OUTPUT_DIR/entry.png.

Six verified stories of 13 November 2026 (each first reported that day):
  1. US Senate Banking Committee summons ex-Nvidia chief Jensen Huang and
     Commerce Secretary Howard Lutnick (Al Jazeera / BBC).
  2. Zelensky meets US envoys Kushner and Witkoff in Dublin; Europe is
     brought into the next round of Ukraine peace talks (BBC).
  3. A Ukrainian drone hits the Russian warship Naro-Fominsk in the Gulf
     of Finland (BBC).
  4. Iran claims it struck a US radar site in Bahrain; the US later said
     it intercepted the drones (Al Jazeera).
  5. The FBI says North Korean hackers stole over $400m in crypto through
     fake video calls (BBC / Reuters).
  6. The Microsoft 365 outage, begun 12 November, runs through 13 November
     worldwide, the largest outage of 2026 (BBC / Ookla).
Footer ticker: Kane's record 126th England cap, and the US reporting a
record 483,200 deportations in fiscal 2026.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ----
NAVY = (11, 37, 69)
NAVY2 = (16, 52, 92)
GOLD = (242, 193, 78)
WHITE = (255, 255, 255)
INK = (24, 28, 36)
PAPER = (247, 244, 238)
SLATE = (216, 222, 230)
SKY = (159, 179, 200)
SEA = (46, 74, 99)
SAND = (201, 162, 39)
DARK = (31, 42, 55)
RED = (196, 48, 48)
GREEN = (63, 163, 77)
BLUE = (46, 127, 194)
BROWN = (122, 84, 52)
LEATHER = (58, 46, 42)
GREY = (60, 71, 80)
SMOKE = (150, 158, 166)
LIGHT = (232, 238, 244)


# ---- 5x7 bitmap font: A-Z, 0-9 and the punctuation the labels need ----
def _g(*rows):
    return [int(r, 2) for r in rows]


FONT = {
    "A": _g("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": _g("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": _g("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": _g("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": _g("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": _g("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": _g("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": _g("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": _g("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": _g("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": _g("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": _g("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": _g("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": _g("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": _g("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": _g("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": _g("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": _g("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": _g("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": _g("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": _g("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": _g("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": _g("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": _g("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": _g("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": _g("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": _g("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": _g("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": _g("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": _g("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": _g("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": _g("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": _g("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": _g("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": _g("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": _g("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": _g("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "&": _g("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    ":": _g("00000", "00100", "00100", "00000", "00100", "00100", "00000"),
    "$": _g("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    ".": _g("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": _g("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": _g("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": _g("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": _g("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": _g("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": _g("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "•": _g("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "!": _g("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
}

CHAR_W = 6  # 5 pixels + 1 spacing, in font units


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


class Canvas:
    """An RGB bitmap with flat vector drawing and a bitmap font."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x0, x1, y, c):
        if x0 > x1:
            x0, x1 = x1, x0
        self.rect(x0, y, x1 - x0 + 1, 1, c)

    def vline(self, x, y0, y1, c):
        if y0 > y1:
            y0, y1 = y1, y0
        self.rect(x, y0, 1, y1 - y0 + 1, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if thick <= 1:
                self.set(x0, y0, c)
            else:
                self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            if fill:
                self.hline(cx - dx, cx + dx, cy + dy, c)
            else:
                self.set(cx - dx, cy + dy, c)
                self.set(cx + dx, cy + dy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            dx = int(rx * (1 - (dy / ry) ** 2) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def triangle(self, p0, p1, p2, c):
        pts = sorted([p0, p1, p2], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        for y in range(y0, y2 + 1):
            xs = []
            for (ax, ay), (bx, by) in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[0], pts[2])):
                if ay == by:
                    continue
                if min(ay, by) <= y <= max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                self.hline(int(min(xs)), int(max(xs)), y, c)

    def text(self, x, y, s, color, scale=1):
        """Draw s with its top-left corner at (x, y)."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += CHAR_W * scale

    def text_center(self, cx, y, s, color, scale=1):
        self.text(cx - text_width(s, scale) // 2, y, s, color, scale)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---- layout ----
MARGIN, GAP = 14, 12
CARD_W, CARD_H = 324, 403
GRID_TOP = 128
LABEL_H = 116
FOOTER_TOP = 958


def card_xy(col, row):
    return (MARGIN + col * (CARD_W + GAP), GRID_TOP + row * (CARD_H + GAP))


def label_band(cv, x, y, line1, line2, bg=NAVY):
    cv.rect(x, y + CARD_H - LABEL_H, CARD_W, LABEL_H, bg)
    cv.rect(x, y + CARD_H - LABEL_H, CARD_W, 4, GOLD)
    mid = x + CARD_W // 2
    cv.text_center(mid, y + CARD_H - LABEL_H + 26, line1, WHITE, 3)
    cv.text_center(mid, y + CARD_H - LABEL_H + 64, line2, WHITE, 3)


def draw_flag_us(cv, x, y, w, h):
    stripe = max(2, h // 13)
    for i in range(13):
        cv.rect(x, y + i * stripe, w, stripe,
                RED if i % 2 == 0 else WHITE)
    cw, ch = int(w * 0.4), stripe * 7
    cv.rect(x, y, cw, ch, NAVY2)
    for r in range(3):
        for c in range(4):
            cv.circle(x + 8 + c * 13, y + 5 + r * 8, 2, WHITE)


def draw_flag_ua(cv, x, y, w, h):
    cv.rect(x, y, w, h // 2, (0, 91, 187))
    cv.rect(x, y + h // 2, w, h - h // 2, (255, 213, 0))


def draw_flag_eu(cv, x, y, w, h):
    cv.rect(x, y, w, h, (0, 51, 153))
    import math
    for k in range(12):
        a = 2 * math.pi * k / 12
        cv.circle(x + w // 2 + int(0.32 * w * 0.9 * math.cos(a)),
                  y + h // 2 + int(0.32 * h * 0.9 * math.sin(a)), 2, GOLD)


# ---- vignette 1: Senate summons Huang & Lutnick ----
def v_senate(cv, x, y):
    cv.rect(x, y, CARD_W, CARD_H - LABEL_H, SLATE)
    draw_flag_us(cv, x + 24, y + 22, 96, 56)
    cv.rect(x + CARD_W - 130, y + 22, 106, 56, NAVY2)
    cv.text_center(x + CARD_W - 77, y + 40, "SENATE", WHITE, 2)
    # two empty witness chairs behind the desk
    for cx0 in (x + 62, x + 182):
        cv.rect(cx0, y + 108, 80, 96, LEATHER)
        cv.rect(cx0 + 6, y + 114, 68, 84, (74, 58, 52))
        cv.rect(cx0 - 8, y + 204, 96, 16, LEATHER)
    # leather jacket draped over the left chair
    cv.rect(x + 62, y + 96, 80, 22, INK)
    cv.rect(x + 70, y + 100, 64, 10, (44, 44, 52))
    # hearing desk
    cv.rect(x, y + 224, CARD_W, 63, BROWN)
    cv.rect(x, y + 224, CARD_W, 6, GOLD)
    cv.rect(x + 20, y + 244, 110, 22, PAPER)
    cv.text(x + 28, y + 249, "HEARING", INK, 1)
    # gavel on the desk
    cv.rect(x + 238, y + 248, 56, 6, (90, 60, 30))
    cv.rect(x + 258, y + 238, 18, 16, (90, 60, 30))
    label_band(cv, x, y, "SENATE SUMMONS", "HUANG & LUTNICK")


# ---- vignette 2: Zelensky meets US envoys ----
def v_zelensky(cv, x, y):
    cv.rect(x, y, CARD_W, CARD_H - LABEL_H, LIGHT)
    # three flags on poles behind the table
    poles = [(x + 48, draw_flag_ua), (x + 142, draw_flag_us),
             (x + 236, draw_flag_eu)]
    for px, fn in poles:
        cv.vline(px + 26, y + 26, y + 150, GREY)
        fn(cv, px, y + 30, 52, 34)
    # three figures: heads and shoulders around the table
    skins = [(232, 190, 150), (214, 172, 134), (198, 158, 122)]
    suits = [(30, 58, 92), (52, 52, 60), (74, 84, 58)]
    for i, fx in enumerate((x + 74, x + 162, x + 250)):
        cv.circle(fx, y + 178, 22, skins[i])
        cv.rect(fx - 30, y + 200, 60, 44, suits[i])
        cv.rect(fx - 8, y + 200, 16, 26, WHITE)
    # round table
    cv.ellipse(x + CARD_W // 2, y + 252, 138, 26, BROWN)
    cv.rect(x + CARD_W // 2 - 10, y + 252, 20, 34, (90, 60, 30))
    cv.ellipse(x + CARD_W // 2, y + 246, 138, 24, (150, 104, 64))
    # papers on the table
    cv.rect(x + 120, y + 238, 34, 12, PAPER)
    cv.rect(x + 172, y + 238, 34, 12, PAPER)
    label_band(cv, x, y, "ZELENSKY MEETS", "US ENVOYS")


# ---- vignette 3: drone hits Russian warship ----
def v_warship(cv, x, y):
    cv.rect(x, y, CARD_W, 150, SKY)
    cv.rect(x, y + 150, CARD_W, CARD_H - LABEL_H - 150, SEA)
    cv.circle(x + 56, y + 44, 26, (244, 214, 130))
    # drone top right
    dx, dy = x + 232, y + 66
    cv.rect(dx - 14, dy - 6, 28, 12, INK)
    cv.line(dx - 22, dy - 12, dx + 22, dy - 12, INK, 2)
    cv.line(dx - 22, dy + 12, dx + 22, dy + 12, INK, 2)
    cv.circle(dx - 22, dy - 12, 4, GREY)
    cv.circle(dx + 22, dy - 12, 4, GREY)
    cv.circle(dx - 22, dy + 12, 4, GREY)
    cv.circle(dx + 22, dy + 12, 4, GREY)
    # smoke from the ship
    cv.circle(x + 118, y + 96, 20, SMOKE)
    cv.circle(x + 138, y + 74, 24, (176, 182, 190))
    cv.circle(x + 162, y + 52, 18, (200, 204, 210))
    # warship hull and superstructure
    cv.rect(x + 40, y + 176, 220, 20, GREY)
    cv.triangle((x + 40, y + 176), (x + 40, y + 196), (x + 8, y + 196), GREY)
    cv.triangle((x + 260, y + 176), (x + 260, y + 196), (x + 292, y + 196), GREY)
    cv.rect(x + 96, y + 150, 96, 26, (74, 84, 94))
    cv.rect(x + 118, y + 128, 52, 22, (74, 84, 94))
    cv.vline(x + 144, y + 104, y + 128, INK)
    cv.rect(x + 210, y + 158, 22, 18, (52, 60, 68))
    # fire glow at the hit point
    cv.circle(x + 118, y + 168, 12, (240, 140, 40))
    cv.circle(x + 118, y + 168, 6, (250, 210, 80))
    # waves
    for wx in (x + 20, x + 120, x + 220):
        cv.line(wx, y + 236, wx + 34, y + 236, WHITE, 2)
        cv.line(wx + 60, y + 258, wx + 94, y + 258, WHITE, 2)
    label_band(cv, x, y, "DRONE HITS", "RUSSIAN WARSHIP")


# ---- vignette 4: Iran claims strike in Bahrain ----
def v_bahrain(cv, x, y):
    cv.rect(x, y, CARD_W, 170, (242, 216, 160))
    cv.rect(x, y + 170, CARD_W, CARD_H - LABEL_H - 170, (214, 178, 110))
    cv.circle(x + 52, y + 44, 22, (244, 214, 130))
    # missile streak across the sky
    cv.line(x + 196, y + 30, x + 296, y + 118, (240, 120, 40), 4)
    cv.line(x + 190, y + 36, x + 290, y + 124, (250, 200, 90), 2)
    cv.triangle((x + 292, y + 112), (x + 306, y + 128), (x + 288, y + 132),
                (240, 120, 40))
    # radar tower and dome
    cv.rect(x + 118, y + 168, 88, 80, (120, 126, 134))
    cv.rect(x + 110, y + 160, 104, 12, (96, 102, 110))
    cv.circle(x + 162, y + 160, 44, WHITE)
    cv.rect(x + 118, y + 160, 88, 10, WHITE)
    cv.line(x + 162, y + 116, x + 162, y + 92, GREY, 3)
    cv.circle(x + 162, y + 90, 6, RED)
    # blast marks on the dome
    cv.line(x + 138, y + 128, x + 150, y + 140, (120, 120, 120), 2)
    cv.line(x + 182, y + 122, x + 172, y + 138, (120, 120, 120), 2)
    # sea strip at the bottom
    cv.rect(x, y + 248, CARD_W, 39, (70, 110, 140))
    cv.line(x + 20, y + 264, x + 70, y + 264, WHITE, 2)
    cv.line(x + 230, y + 272, x + 290, y + 272, WHITE, 2)
    label_band(cv, x, y, "IRAN CLAIMS", "STRIKE IN BAHRAIN")


# ---- vignette 5: FBI, North Korea $400m hack ----
def v_hack(cv, x, y):
    cv.rect(x, y, CARD_W, CARD_H - LABEL_H, DARK)
    # laptop screen
    cv.rect(x + 42, y + 34, 240, 150, INK)
    cv.rect(x + 52, y + 44, 220, 130, (14, 26, 40))
    # masked face on the video call
    cv.circle(x + 162, y + 100, 34, (20, 20, 24))
    cv.rect(x + 128, y + 62, 68, 26, (20, 20, 24))
    cv.rect(x + 140, y + 92, 16, 6, WHITE)
    cv.rect(x + 168, y + 92, 16, 6, WHITE)
    cv.rect(x + 152, y + 112, 20, 4, (120, 120, 120))
    # call controls
    cv.circle(x + 142, y + 158, 9, RED)
    cv.circle(x + 182, y + 158, 9, (40, 120, 70))
    # laptop base
    cv.rect(x + 22, y + 184, 280, 16, (52, 60, 68))
    cv.rect(x + 130, y + 188, 64, 6, INK)
    # gold coins spilling out
    for i, (cx0, cy0) in enumerate(((x + 66, y + 216), (x + 100, y + 228),
                                    (x + 140, y + 214), (x + 178, y + 230),
                                    (x + 216, y + 216), (x + 252, y + 226))):
        cv.circle(cx0, cy0, 13, GOLD)
        cv.circle(cx0, cy0, 8, (214, 164, 40))
        cv.text(cx0 - 4, cy0 - 7, "$", (120, 88, 10), 1)
    label_band(cv, x, y, "FBI: N. KOREA", "$400M HACK")


# ---- vignette 6: Microsoft 365 outage ----
def v_outage(cv, x, y):
    cv.rect(x, y, CARD_W, CARD_H - LABEL_H, LIGHT)
    # big monitor with a mail envelope and a red X
    cv.rect(x + 52, y + 30, 220, 150, INK)
    cv.rect(x + 62, y + 40, 200, 130, (220, 230, 240))
    cv.rect(x + 112, y + 82, 100, 56, WHITE)
    cv.rect(x + 112, y + 82, 100, 56, (160, 170, 180))
    cv.line(x + 112, y + 82, x + 162, y + 112, (160, 170, 180), 2)
    cv.line(x + 212, y + 82, x + 162, y + 112, (160, 170, 180), 2)
    cv.line(x + 96, y + 62, x + 228, y + 158, RED, 7)
    cv.line(x + 228, y + 62, x + 96, y + 158, RED, 7)
    # monitor stand
    cv.rect(x + 152, y + 180, 20, 26, INK)
    cv.rect(x + 122, y + 206, 80, 10, INK)
    # small dead devices
    cv.rect(x + 36, y + 226, 44, 46, INK)
    cv.rect(x + 42, y + 232, 32, 34, (220, 230, 240))
    cv.line(x + 44, y + 234, x + 72, y + 264, RED, 3)
    cv.line(x + 72, y + 234, x + 44, y + 264, RED, 3)
    cv.rect(x + 244, y + 226, 44, 46, INK)
    cv.rect(x + 250, y + 232, 32, 34, (220, 230, 240))
    cv.line(x + 252, y + 234, x + 280, y + 264, RED, 3)
    cv.line(x + 280, y + 234, x + 252, y + 264, RED, 3)
    label_band(cv, x, y, "MICROSOFT 365", "OUTAGE HITS WORLD")


def draw_header(cv):
    cv.rect(0, 0, W, 118, NAVY)
    # globe
    gx, gy, gr = 62, 59, 42
    cv.circle(gx, gy, gr, BLUE)
    cv.circle(gx - 12, gy - 10, 12, GREEN)
    cv.circle(gx + 14, gy + 8, 14, GREEN)
    cv.circle(gx + 8, gy - 18, 8, GREEN)
    cv.circle(gx, gy, gr, WHITE, fill=False)
    cv.ellipse(gx, gy, 18, gr, (120, 180, 230))
    cv.line(gx - gr, gy, gx + gr, gy, (120, 180, 230), 1)
    # title and subtitle
    cv.text(124, 24, "FRIDAY 13 NOVEMBER 2026", WHITE, 4)
    cv.text(124, 72, "THE WORLD TODAY", GOLD, 3)
    cv.text(W - 180, 34, "6 STORIES", GOLD, 2)
    cv.text(W - 180, 62, "WORLDWIDE", GOLD, 2)
    cv.rect(0, 118, W, 4, GOLD)


def draw_footer(cv):
    cv.rect(0, FOOTER_TOP, W, H - FOOTER_TOP, NAVY)
    cv.rect(0, FOOTER_TOP, W, 4, GOLD)
    cv.text_center(W // 2, FOOTER_TOP + 22,
                   "ALSO: KANE 126 CAPS RECORD  •  US REPORTS RECORD 483,200 DEPORTATIONS",
                   WHITE, 2)


def build():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    vignettes = [v_senate, v_zelensky, v_warship, v_bahrain, v_hack, v_outage]
    for i, fn in enumerate(vignettes):
        x, y = card_xy(i % 3, i // 3)
        cv.rect(x - 2, y - 2, CARD_W + 4, CARD_H + 4, NAVY2)
        fn(cv, x, y)
    draw_footer(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
