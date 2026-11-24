#!/usr/bin/env python3
"""news-23 b130 front-page-dense: render entry.png (1024x1024) with PIL."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (248, 244, 233)
INK = (20, 20, 20)
RED = (164, 18, 31)
GOLD = (176, 132, 16)
NAVY = (31, 58, 110)
DARKNAVY = (13, 27, 62)
GREEN = (30, 122, 60)
PURPLE = (107, 63, 160)
ORANGE = (196, 106, 27)
GRAY = (85, 85, 85)
LIGHT = (232, 226, 208)
BLOB = (183, 211, 168)
BLOB_EDGE = (120, 160, 110)


def font(name, size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVu%s.ttf" % name,
        "/usr/share/fonts/dejavu/DejaVu%s.ttf" % name,
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F = {
    "mast": font("Serif-Bold", 46),
    "date": font("Sans-Bold", 20),
    "kick": font("Sans-Bold", 15),
    "num": font("Sans-Bold", 26),
    "numlab": font("Sans", 11),
    "region": font("Sans-Bold", 13),
    "region_s": font("Sans-Bold", 12),
    "utc": font("Sans", 11),
    "hero_h": font("Sans-Bold", 17),
    "hero_b": font("Sans", 12),
    "hero_s": font("Sans", 9),
    "chip": font("Sans-Bold", 9),
    "bar": font("Sans-Bold", 13),
    "cat": font("Sans-Bold", 10),
    "card_n": font("Sans-Bold", 13),
    "card_h": font("Sans-Bold", 13),
    "card_b": font("Sans", 11),
    "card_s": font("Sans", 9),
    "also_t": font("Sans-Bold", 14),
    "also": font("Sans", 11),
    "legend": font("Sans", 10),
    "dc_t": font("Sans-Bold", 13),
    "dc": font("Sans", 12),
    "foot": font("Sans", 11),
    "foot_b": font("Sans-Bold", 14),
    "big": font("Sans-Bold", 30),
    "huge": font("Sans-Bold", 44),
    "pi_lab": font("Sans-Bold", 13),
    "pi_val": font("Sans-Bold", 14),
}

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)


def text(x, y, s, f, fill=INK, anchor="la"):
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)


def wrap(s, f, maxw):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(s, base_size, maxw, bold=True):
    """Shrink font until text fits maxw; returns (font, size)."""
    size = base_size
    while size >= 8:
        f = font("Sans-Bold" if bold else "Sans", size)
        if d.textlength(s, font=f) <= maxw:
            return f
        size -= 1
    return font("Sans-Bold" if bold else "Sans", 8)


def chip(x, y, label, bg):
    w = int(d.textlength(label, font=F["chip"])) + 12
    d.rounded_rectangle([x, y, x + w, y + 14], radius=3, fill=bg)
    d.text((x + 6, y + 2), label, font=F["chip"], fill=(255, 255, 255))
    return w


# ---- masthead ----
text(16, 8, "THE WORLD TODAY", F["mast"], INK)
text(1008, 22, "MONDAY 23 NOVEMBER 2026", F["date"], GOLD, anchor="ra")

# ---- kicker ----
d.rectangle([0, 64, W, 88], fill=RED)
text(16, 69, "AI rout hits Asia  \u00b7  UN chief urges AI rules  \u00b7  US lead over China at record low  \u00b7  Anthropic IPO $107.3B",
     F["kick"], (255, 255, 255))

# ---- number strip (2 rows x 5 cols) ----
NUMBERS = [
    ("-3.3%", "KOSPI"), ("5.3", "US-CHINA POWER GAP"), ("11,762", "EBOLA CASES, DRC"),
    ("10T won", "SEOUL STABILISATION FUND"), ("2%", "BILLIONAIRE TAX IN PARIS"),
    ("$450M", "SKUBAL DEAL"), ("165", "RUSSIAN MISSILES/WEEK"), ("12,000", "CLEARED IN MANCHESTER"),
    ("264 kg", "EXPLOSIVES SEIZED"), ("$107.3B", "ANTHROPIC IPO"),
]
for i, (v, lab) in enumerate(NUMBERS):
    col, row = i % 5, i // 5
    x = col * 205 + 8
    y0 = 92 + row * 46
    text(x, y0, v, F["num"], INK)
    text(x, y0 + 28, lab, F["numlab"], (70, 70, 70))

# ---- region bar ----
REGIONS = [("ASIA-PACIFIC 7", NAVY, 231), ("AMERICAS 8", RED, 264), ("MIDDLE EAST 6", PURPLE, 198),
           ("EUROPE 5", GREEN, 165), ("AFRICA 3", ORANGE, 99), ("WORLD 2", GRAY, 66)]
x = 0
for label, color, w in REGIONS:
    d.rectangle([x, 184, x + w, 206], fill=color)
    f = F["region"] if w > 70 else F["region_s"]
    d.text((x + w / 2, 189), label, font=f, fill=(255, 255, 255), anchor="ma")
    x += w

# ---- UTC strip ----
d.rectangle([0, 206, W, 224], fill=LIGHT)
text(16, 210, "THE DAY IN UTC   ~00:00 Kospi dives   ~05:30 Guterres opens   ~09:00 Power Index   ~12:00 Paris 2% tax   ~15:00 Kyiv missiles",
     F["utc"], (60, 60, 60))
text(1008, 210, "~ APPROX", F["utc"], (60, 60, 60), anchor="ra")

# ---- heroes ----
HX = [8, 348, 688]
HW = 328


def hero_scene_kospi(x0, y0):
    d.rectangle([x0, y0, x0 + HW, y0 + 98], fill=DARKNAVY)
    # skyline buildings with lit windows
    import random
    rnd = random.Random(7)
    bx = x0 + 6
    while bx < x0 + HW - 30:
        bw = rnd.randint(22, 40)
        bh = rnd.randint(28, 62)
        by = y0 + 98 - 18 - bh
        d.rectangle([bx, by, bx + bw, y0 + 80], fill=(24, 40, 80), outline=(50, 70, 120))
        for wy in range(by + 5, y0 + 76, 9):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 210, 90))
        bx += bw + 4
    # descending chart line (kept below the -3.3% label so it never crosses it)
    pts = [(x0 + 20, y0 + 42), (x0 + 70, y0 + 50), (x0 + 120, y0 + 47), (x0 + 170, y0 + 58),
           (x0 + 220, y0 + 64), (x0 + 270, y0 + 72), (x0 + 310, y0 + 78)]
    d.line(pts, fill=(255, 140, 40), width=3)
    for p in pts:
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(255, 255, 255))
    text(x0 + 10, y0 + 2, "-3.3%", F["big"], (255, 255, 255))
    d.rectangle([x0, y0 + 80, x0 + HW, y0 + 98], fill=(8, 16, 40))
    text(x0 + 10, y0 + 83, "KOSPI 4,708.54  \u00b7  -161 PTS  \u00b7  SAMSUNG -3.1%  \u00b7  SK HYNIX -2.5%", F["hero_s"], (255, 255, 255))


def hero_scene_guterres(x0, y0):
    d.rectangle([x0, y0, x0 + HW, y0 + 98], fill=GREEN)
    text(x0 + 12, y0 + 4, "150", font("Sans-Bold", 36), (255, 215, 0))
    gut = font("Sans-Bold", 16)
    lines = wrap("DELEGATES BACK A RISK FRAMEWORK", gut, 165)
    yy = y0 + 44
    for ln in lines:
        text(x0 + 12, yy, ln, gut, (255, 215, 0))
        yy += 18
    # globe
    cx, cy, r = x0 + 255, y0 + 49, 40
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 240, 220), outline=(255, 255, 255), width=2)
    d.ellipse([cx - 18, cy - r, cx + 18, cy + r], outline=(140, 180, 140), width=1)
    d.line([cx - r, cy, cx + r, cy], fill=(140, 180, 140), width=1)
    d.arc([cx - r, cy - 22, cx + r, cy + 22], 0, 360, fill=(140, 180, 140), width=1)


def hero_scene_power(x0, y0):
    d.rectangle([x0, y0, x0 + HW, y0 + 98], fill=(243, 234, 210))
    text(x0 + 10, y0 + 6, "NARROWEST SINCE 2018", F["pi_lab"], INK)
    text(x0 + HW - 10, y0 + 6, "GAP 5.3", F["pi_lab"], RED, anchor="ra")
    bars = [("78.9", "US", NAVY, 250), ("73.6", "CHINA", RED, 235), ("40.5", "INDIA", (176, 132, 16), 130)]
    yy = y0 + 30
    for val, name, color, bw in bars:
        text(x0 + 10, yy, val, F["pi_val"], INK)
        d.rectangle([x0 + 62, yy + 2, x0 + 62 + bw, yy + 16], fill=color)
        d.text((x0 + 68, yy + 3), name, font=F["chip"], fill=(255, 255, 255))
        yy += 23


HEROES = [
    ("AI ROUT HITS ASIA",
     "Kospi closes -3.3% to 4,708.54, sheds 161 pts; intraday -5.8%.",
     "KOREA EXCHANGE", hero_scene_kospi),
    ("GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
     "UN chief urges global AI safety rules at the Bridgetown summit.",
     "UNITED NATIONS", hero_scene_guterres),
    ("US LEAD OVER CHINA AT RECORD LOW",
     "Asia Power Index 2026: US 78.9, China 73.6 \u2014 gap 5.3, narrowest since 2018.",
     "LOWY INSTITUTE", hero_scene_power),
]
for i, (head, body, src, scene) in enumerate(HEROES):
    x0 = HX[i]
    y0 = 224
    scene(x0, y0)
    hl = wrap(head, F["hero_h"], HW)
    yy = y0 + 102
    for ln in hl[:2]:
        text(x0, yy, ln, F["hero_h"], INK)
        yy += 20
    bl = wrap(body, F["hero_b"], HW - 90)  # keep body clear of the REPORTED chip
    for ln in bl[:2]:
        text(x0, yy, ln, F["hero_b"], (50, 50, 50))
        yy += 15
    text(x0, 392, src, F["hero_s"], (100, 100, 100))
    chip(x0 + HW - 78, 390, "REPORTED", NAVY)

# ---- more of the day bar ----
d.rectangle([0, 408, W, 430], fill=INK)
text(16, 413, "MORE OF THE DAY  \u2014  10 STORIES", F["bar"], (255, 255, 255))

# ---- cards ----
CARDS = [
    ("1", "AMERICAS", "BESSENT: NVIDIA ANSWERS", "Treasury wants answers.", "WSJ", False),
    ("2", "AMERICAS", "FBI PROBES NCIC HACK", "NCIC database hacked.", "AP", False),
    ("3", "WHITE HOUSE", "TRUMP: IRAN STRIKES MAY RESUME", "May resume in New Year.", "Reuters", False),
    ("4", "MARKETS", "US FUTURES JUMP 3%", "Holiday rally lifts 3%.", "Bloomberg", False),
    ("5", "SPORT", "SKUBAL'S $450M METS DEAL", "Nine-year, largest ever.", "AP", False),
    ("6", "SPORT", "TOM JACKSON DIES AT 75", "Broncos LB, ESPN voice.", "ESPN", False),
    ("7", "LEGAL", "STATES SUE SPACEX", "Ten states sue over AI.", "AP", False),
    ("8", "TECH", "ANTHROPIC IPO: $107.3B", "Raised $83; closes $97.17.", "WSJ", False),
    ("9", "EUROPE", "POLAND: 3 MISSILES CROSSED AIRSPACE", "Kyiv: 3 Kh-101s crossed.", "AP", True),
    ("10", "SPACE", "RUSSIAN NUCLEAR SATELLITE", "May carry a nuke.", "Reuters", True),
]
CW = 194
for i, (num, cat, head, body, src, claim) in enumerate(CARDS):
    col, row = i % 5, i // 5
    x0 = 8 + col * 202
    y0 = 434 + row * 75
    text(x0, y0, num, F["card_n"], RED)
    text(x0 + 26, y0 + 1, cat, F["cat"], RED)
    hl = wrap(head, F["card_h"], CW)
    yy = y0 + 17
    for ln in hl[:2]:
        text(x0, yy, ln, F["card_h"], INK)
        yy += 15
    bl = wrap(body, F["card_b"], CW)
    for ln in bl[:1]:
        text(x0, yy, ln, F["card_b"], (50, 50, 50))
        yy += 13
    text(x0, y0 + 60, src, F["card_s"], (100, 100, 100))
    chip(x0 + CW - 78, y0 + 58, "CLAIM" if claim else "REPORTED", RED if claim else NAVY)

# ---- where it happened bar ----
d.rectangle([0, 580, W, 602], fill=INK)
text(16, 585, "WHERE IT HAPPENED", F["bar"], (255, 255, 255))

# ---- map ----
MAP_X0, MAP_Y0 = 8, 602
BLOBS = {
    "americas": [(25, 640), (60, 610), (150, 605), (180, 640), (175, 720), (150, 800), (90, 810), (40, 770), (20, 700)],
    "europe": [(205, 615), (330, 610), (345, 650), (320, 715), (260, 720), (210, 690), (195, 650)],
    "africa": [(215, 730), (320, 725), (335, 765), (305, 810), (250, 815), (215, 785)],
    "asia": [(350, 610), (480, 605), (495, 660), (470, 740), (420, 800), (360, 780), (345, 690)],
}
for pts in BLOBS.values():
    d.polygon(pts, fill=BLOB, outline=BLOB_EDGE)
PINS = {
    1: (440, 650), 2: (95, 790), 3: (455, 625), 4: (120, 690), 5: (150, 660),
    6: (300, 645), 7: (255, 665), 8: (240, 640), 9: (305, 665), 10: (232, 622),
    11: (318, 700), 12: (315, 738), 13: (280, 790),
}
for n, (px, py) in PINS.items():
    d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
    d.text((px, py - 6), str(n), font=F["chip"], fill=(255, 255, 255), anchor="ma")
text(8, 820, "Pins 1\u201313: 1 Seoul \u00b7 2 Bridgetown \u00b7 3 Beijing \u00b7 4 Washington \u00b7 5 New York \u00b7 6 Kyiv \u00b7 7 Paris",
     F["legend"], (60, 60, 60))
text(8, 832, "8 London \u00b7 9 Warsaw \u00b7 10 Manchester \u00b7 11 Beirut \u00b7 12 Gaza \u00b7 13 Khartoum",
     F["legend"], (60, 60, 60))

# ---- ALSO ----
text(516, 606, "ALSO ON MONDAY", F["also_t"], INK)
ALSO = [
    ("14", "Paris: 100+ back 2% billionaire tax", False),
    ("15", "Manchester: 12,000 cleared", False),
    ("16", "Zelenskyy: 165 missiles in a week", False),
    ("17", "COP31: day after Antalya pact rejected", False),
    ("18", "Israel unity talks resume", False),
    ("19", "Gaza: two killed in Israeli strike", False),
    ("20", "West Bank settler attacks", False),
    ("21", "Iran war: no deal in sight", False),
    ("22", "Lebanon seizes 264 kg explosives", False),
    ("23", "Bahrain: strike hits plant, 2 hurt", False),
    ("24", "Benghazi: UN demands probe", True),
    ("25", "Sudan: defences down drones", True),
    ("26", "DRC: fighting traps Ebola teams", False),
    ("27", "Bangladesh: Hasina jailed if she returns", False),
    ("28", "Seoul minister quits over AI exam row", False),
    ("29", "SK Telecom -7.3% as hype cools", False),
    ("30", "China eases margin rules", False),
    ("31", "Seoul readies 10T-won fund", False),
]
for i, (num, item, claim) in enumerate(ALSO):
    col, row = i // 9, i % 9
    x0 = 516 + col * 256
    y0 = 628 + row * 23
    s = "%s. %s" % (num, item)
    f = fit_font(s, 11, 244, bold=False)
    text(x0, y0, s, f, (40, 40, 40))
    if claim:
        cw = int(d.textlength(s, font=f))
        chip(x0 + cw + 5, y0 + 1, "CLAIM", RED)

# ---- DATE CHECK ----
d.rectangle([8, 844, 1016, 920], outline=RED, width=3)
text(20, 849, "DATE CHECK  \u2014  READ 23 NOV 2026, 23:59 UTC  \u00b7  STORIES DATED 23 NOV ONLY", F["dc_t"], RED)
text(20, 868, "LEFT OUT \u2014 NOT 23 NOV:  Dems reach 258 (22 Nov)  \u00b7  Sparta II fire (22 Nov)  \u00b7  El Chapo Isidro captured (22 Nov)",
     F["dc"], INK)
text(20, 885, "EU\u2013Indonesia pact (21 Nov)  \u00b7  Nigeria boat (21 Nov)  \u00b7  ICJ Myanmar ruling (19 Nov)",
     F["dc"], INK)
text(20, 902, "NOT YET \u2014 Dymer search continues (14 missing)  \u00b7  4 House races uncalled  \u00b7  COP32 venue not set  \u00b7  WHO evacuating trapped Ebola staff",
     F["dc"], INK)

# ---- footer ----
text(16, 928, "Sources: Reuters \u00b7 AP \u00b7 Bloomberg \u00b7 AFP \u00b7 Yonhap \u00b7 BBC \u00b7 WSJ \u00b7 ESPN \u00b7 Lowy Institute (Asia Power Index 2026).",
     F["foot"], (80, 80, 80))
text(16, 946, "CHIPS: REPORTED = confirmed by wires \u00b7 CLAIM = one side's claim, independently unconfirmed \u00b7 ONGOING = still developing.",
     F["foot"], (80, 80, 80))
text(16, 964, "All times UTC. Figures as reported 23 Nov 2026. Scenes are drawn illustrations, not photographs.",
     F["foot"], (80, 80, 80))
d.text((512, 986), "THE WORLD TODAY  \u00b7  Monday 23 November 2026  \u00b7  31 stories  \u00b7  6 regions",
       font=F["foot_b"], fill=GOLD, anchor="ma")

img.save("entry.png")
print("saved entry.png", os.path.getsize("entry.png"), "bytes")
