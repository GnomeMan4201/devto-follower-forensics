#!/usr/bin/env python3
"""Cover image for the INV-001 correction post, in the same terminal style as the original.

Needs: pip install pillow pyfiglet   (plus a monospace TTF; DejaVu Sans Mono by default)
Usage: python3 make_banner.py [out.png] [--font /path/to/Mono.ttf]
Makes a 2000x840 PNG (DEV's 1000x420 cover ratio, at 2x).
"""
import sys
from PIL import Image, ImageDraw, ImageFont
import pyfiglet

W, H = 2000, 840
BG = (13, 17, 23)
PANEL = (22, 27, 34)
DIM = (125, 133, 144)
TEXT = (201, 209, 217)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
YELLOW = (227, 179, 65)
CYAN = (57, 197, 207)
MAGENTA = (188, 140, 255)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args else "correction_cover.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
if "--font" in sys.argv:
    FONT = sys.argv[sys.argv.index("--font") + 1]

def font(size): return ImageFont.truetype(FONT, size)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def gradient(stops, t):
    t = max(0.0, min(1.0, t)); n = len(stops) - 1
    i = min(int(t * n), n - 1)
    return lerp(stops[i], stops[i + 1], t * n - i)

def figlet_block(d, text, x, y, size, stops, fig="ansi_shadow"):
    """Draw figlet text with a left-to-right colour gradient, one glyph cell at a time."""
    lines = pyfiglet.figlet_format(text, font=fig, width=400).rstrip("\n").split("\n")
    f = font(size)
    cw = f.getlength("M"); lh = int(size * 1.0)
    width = max(len(l) for l in lines)
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == " ": continue
            col = gradient(stops, c / max(1, width - 1))
            if ch not in "█▓▒░":
                col = lerp(col, BG, 0.45)          # outline chars dimmer, like a drop shadow
            d.text((x + c * cw, y + r * lh), ch, font=f, fill=col)
    return x + width * cw, y + len(lines) * lh

def term(d, x, y, rows, size=23, lh=34):
    f = font(size)
    for row in rows:
        cx = x
        for seg, col in row:
            d.text((cx, y), seg, font=f, fill=col); cx += f.getlength(seg)
        y += lh
    return y

def rule(d, x, y, w, col, label=None, size=20):
    d.line([(x, y), (x + w, y)], fill=col, width=2)
    if label:
        f = font(size)
        tw = f.getlength(label) + 16
        d.rectangle([x + 8, y - 13, x + 8 + tw, y + 13], fill=PANEL)
        d.text((x + 16, y - 12), label, font=f, fill=col)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
for yy in range(0, H, 4):                           # faint scanlines
    d.line([(0, yy), (W, yy)], fill=(16, 21, 28))

M = 40; GAP = 40; PW = (W - 2 * M - GAP) // 2
L, R = M, M + PW + GAP
for px in (L, R):
    d.rectangle([px, M, px + PW, H - M], fill=PANEL, outline=(48, 54, 61), width=2)

# ---- left panel: RE-AUDIT ---------------------------------------------------
figlet_block(d, "RE-AUDIT", L + 34, M + 30, 19, [RED, YELLOW])
y = M + 170
y = term(d, L + 34, y, [
    [("INV-001 re-audit", CYAN), (" | badBANANA Research Collective", DIM)],
    [("snapshot 2026-11-14 · followers via /api/followers/users", DIM)],
])
rule(d, L + 34, y + 22, PW - 68, YELLOW, "PHASE 1 · ORIGINAL AUDIT CSV")
y = term(d, L + 34, y + 52, [
    [("$ ", GREEN), ("python3 uniform_cols.py devto_bot_audit_full.csv", TEXT)],
    [("   1409 Following=1   ", RED), ("<- profile.get(\"followed_users_count\", 1)", DIM)],
    [("   1409 Followers=0   ", RED), ("<- field never returned", DIM)],
    [("   1409 PostCount=0   ", RED), ("<- \"No posts\" scored for everyone", DIM)],
    [("$ ", GREEN), ("wc -l flagged_usernames.txt", TEXT)],
    [("    899 ", YELLOW), ("(published: 897 · cannot reproduce)", DIM)],
])
rule(d, L + 34, y + 22, PW - 68, YELLOW, "PHASE 2 · NOV-2025 COHORT")
y = term(d, L + 34, y + 52, [
    [("exact ID match ", TEXT), ("338/338", GREEN), ("   follows dated ", TEXT), ("2025-11-14..20", GREEN)],
    [("claimed: dormant 187 days   ", DIM), ("observed: 0 days", GREEN)],
])
d.text((L + 34, H - M - 72), "VERDICT: 897 -> WITHDRAWN", font=font(34), fill=RED)

# ---- right panel: BASELINE --------------------------------------------------
figlet_block(d, "BASELINE", R + 34, M + 30, 19, [MAGENTA, CYAN])
y = M + 170
y = term(d, R + 34, y, [
    [("follow timing vs your own posting", CYAN), (" | 9,638 followers", DIM)],
    [("null: post dates shuffled within month, 3000 reps", DIM)],
])
rule(d, R + 34, y + 22, PW - 68, CYAN, "PHASE 3 · DAYS SINCE LAST POST")
bars = [("same day", 28.4), ("1-3 d", 58.5), ("4-7 d", 13.0), ("8-14 d", 0.0), ("15+ d", 0.2)]
f = font(23); by = y + 52; bx = R + 34 + f.getlength("same day  ")
maxw = PW - 68 - (bx - (R + 34)) - 110
for i, (lab, v) in enumerate(bars):
    d.text((R + 34, by), lab, font=f, fill=TEXT)
    n = int(round(v / 60 * maxw / 14))
    for k in range(n):
        d.text((bx + k * 14, by), "█", font=f, fill=gradient([MAGENTA, CYAN], k / max(1, maxw / 14)))
    d.text((bx + max(n, 1) * 14 + 10, by), f"{v:4.1f}%", font=f, fill=YELLOW if v > 10 else DIM)
    by += 34
y = by
rule(d, R + 34, y + 22, PW - 68, CYAN, "PHASE 4 · PERMUTATION TEST")
y = term(d, R + 34, y + 52, [
    [("observed ", TEXT), ("86.8%", GREEN), (" within 0-3 d · null median ", TEXT), ("49-59%", DIM)],
    [("shuffles >= observed: ", TEXT), ("0/3000", GREEN), ("   p=0.00033", YELLOW)],
    [("excl. May+Nov: ", TEXT), ("75.6%", GREEN), (" vs ~30% expected", DIM)],
])
d.text((R + 34, H - M - 72), "association != mechanism", font=font(34), fill=CYAN)

img.save(OUT)
print("wrote", OUT, img.size)
