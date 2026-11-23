import os
from render_lib import *
OUT = os.path.dirname(os.path.abspath(__file__))

COL = {1: "#F57C00", 2: "#F57C00", 3: "#151515", 4: "#D32F2F", 5: "#151515", 6: "#D32F2F", 7: "#151515", 8: "#9E9E9E",
       9: "#7B1FA2", 10: "#FBC02D", 11: "#FBC02D", 12: "#F57C00", 13: "#F57C00", 14: "#1565C0", 15: "#151515", 16: "#2E7D32",
       17: "#151515", 18: "#151515", 19: "#151515", 20: None, 21: "#D32F2F", 22: "#D32F2F", 23: "#D32F2F", 24: "#151515"}
KEY = {9: ("#CE93D8", "9  PURPLE  +5VSB"), 16: ("#69F0AE", "16  GREEN  PS_ON"), 15: ("#FFFFFF", "15  BLACK  GND"), 17: ("#FFFFFF", "17  BLACK  GND")}

def housing(x, y, p, top_nums, bot_nums, title, contact):
    w = 12 * p + 40
    h = 2 * p + 40
    s = f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="url(#nylonblack)"/>'
    # latch on the top row, between pins 18 and 19
    li = top_nums.index(18); lj = top_nums.index(19)
    lx = x + 20 + p * (li + lj + 1) / 2
    s += f'<path d="M {lx-48} {y} L {lx-40} {y-58} L {lx+40} {y-58} L {lx+48} {y} Z" fill="#262626" stroke="#000"/>'
    s += f'<rect x="{lx-34}" y="{y-50}" width="68" height="16" rx="4" fill="#3c3c3c"/></g>'
    s += text(lx + 60, y - 30, "LATCH", 16, "bold", "start", "#3b2b18")
    for row, nums in ((0, top_nums), (1, bot_nums)):
        for i, n in enumerate(nums):
            cx = x + 20 + p * i + p / 2
            cy = y + 20 + p * row + p / 2
            hw = p * 0.36
            rounded = (n % 3 == 0)
            if contact:
                s += f'<rect x="{cx-hw}" y="{cy-hw}" width="{2*hw}" height="{2*hw}" rx="{hw*0.6 if rounded else 3}" fill="#050505" stroke="#3a3a3a" stroke-width="2"/>'
                if COL[n] is not None:
                    s += f'<rect x="{cx-hw*0.45}" y="{cy-hw*0.45}" width="{hw*0.9}" height="{hw*0.9}" rx="3" fill="url(#nickel)" opacity="0.9"/>'
                    s += f'<circle cx="{cx}" cy="{cy}" r="{hw*0.22}" fill="#1a1a1a"/>'
            else:
                s += f'<rect x="{cx-hw}" y="{cy-hw}" width="{2*hw}" height="{2*hw}" rx="4" fill="#0a0a0a" stroke="#333"/>'
                if COL[n] is not None:
                    s += f'<circle cx="{cx}" cy="{cy}" r="{hw*0.82}" fill="{COL[n]}" stroke="#000" stroke-width="2"/>'
                    s += f'<circle cx="{cx-hw*0.25}" cy="{cy-hw*0.3}" r="{hw*0.25}" fill="#fff" opacity="0.28"/>'
                    s += f'<circle cx="{cx}" cy="{cy}" r="{hw*0.22}" fill="#c0c4c6"/>'
            ty = (y + 27) if row == 0 else (y + h - 9)
            s += text(cx, ty, str(n), 15, "bold", "middle", "#ffffff" if n in KEY else "#9e9e9e")
            if n in KEY:
                c = KEY[n][0] if n != 15 and n != 17 else "#FFE000"
                s += f'<rect x="{cx-hw-7}" y="{cy-hw-7}" width="{2*hw+14}" height="{2*hw+14}" rx="8" fill="none" stroke="#000" stroke-opacity="0.6" stroke-width="8"/>'
                s += f'<rect x="{cx-hw-7}" y="{cy-hw-7}" width="{2*hw+14}" height="{2*hw+14}" rx="8" fill="none" stroke="{c}" stroke-width="4" filter="url(#glow)"/>'
    s += text(x + w / 2, y + h + 64, title, 22, "bold", "middle", "#2b2014")
    return s

def atx():
    W, H = 1620, 1400
    b = title_bar(W, "ATX 24-pin plug (from your flex ATX power supply) - which wires to use",
                  "Purple = +5VSB (powers the Pico)   Black = ground   Green = PS_ON (Option B, or jumpered to black for Option A)")
    p = 92
    # Panel A: contact side (looking into the holes), latch up: top row 13..24, bottom row 1..12, left to right
    ax, ay = 40, 200
    b += housing(ax, ay, p, list(range(13, 25)), list(range(1, 13)), "A.  CONTACT side  (looking into the holes, latch on top)", True)
    # Option A jumper inset drawn on panel A: U-wire 16 -> 15
    def hole_xy(x, y, nums_top, nums_bot, n):
        if n in nums_top: return x + 20 + p * nums_top.index(n) + p / 2, y + 20 + p / 2
        return x + 20 + p * nums_bot.index(n) + p / 2, y + 20 + p * 1.5
    # Panel B: wire side (looking at the back where the wires come out) = mirror image
    bx, by = 40, 700
    topB = list(range(24, 12, -1)); botB = list(range(12, 0, -1))
    # wires drawn first, going down from each hole
    for row, nums in ((0, topB), (1, botB)):
        for i, n in enumerate(nums):
            if COL[n] is None: continue
            cx = bx + 20 + p * i + p / 2
            cy = by + 20 + p * row + p / 2
            off = (i - 5.5) * 6
            d = f"M {cx} {cy} C {cx} {cy+200}, {cx*0.85+120+off} {by+420}, {cx*0.7+260+off} {by+600}"
            b += wire_path(d, COL[n], 22 if row == 1 else 20)
    b += housing(bx, by, p, topB, botB, "", False)
    b += text(bx + 6 * p + 20, by - 92, "B.  WIRE side  (back of the plug, latch on top) - the mirror image of A", 22, "bold", "middle", "#2b2014")
    leg = ["Ringed holes / wires:",
           "PURPLE  pin 9   = +5VSB",
           "   -> D1 -> Pico VSYS (pin 39)",
           "BLACK  pin 15 or 17 = ground",
           "   -> Pico GND (pin 38)",
           "GREEN  pin 16  = PS_ON",
           "   Option B: -> Q2 Drain",
           "   Option A: short wire from",
           "   16 to 15 (or 17) = always on"]
    b += label(1290, 690, ["WHICH WIRES"] + leg, "#FFE000", w=300, size=15, title_size=19)
    b += label(1290, 200, ["DON'T CUT THE CABLE", "use a 24-pin ATX", "breakout board or a", "female 24-pin socket"], "#FF8A80", w=300, size=15, title_size=18)
    b += footer(W, H, "Pin layout per the ATX12V spec (contact side, latch up: top row 13-24, bottom 1-12).  All-black cable? Count positions from the latch.")
    return svg(W, H, b)

save(OUT, "R5_ATX24_Plug_Wires", atx())
print("ok")
