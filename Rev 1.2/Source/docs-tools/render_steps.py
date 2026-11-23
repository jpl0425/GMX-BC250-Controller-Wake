import os, base64, math
from render_lib import *
from board_lib import *
OUT = os.path.dirname(os.path.abspath(__file__))
ORANGE, GREEN, YELLOW, BLACK, RED, PURPLE = "#EF6C00", "#2E7D32", "#F9A825", "#1b1b1b", "#D32F2F", "#7B1FA2"

def img_embed(path, x, y, w, h, clip=None):
    data = base64.b64encode(open(path, "rb").read()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'

def pico_alone(cx, cy, P=26, label="Pico W / Pico 2 W"):
    b = Board(cx - P * 4, cy - P * 10, 1, 1, P)
    return pico_w(b, 0, 0, label)

def gamepad(cx, cy, scale=1.0, glow=False):
    s = f'<g transform="translate({cx},{cy}) scale({scale})" filter="url(#shadow)">'
    s += ('<path d="M -170 -40 C -150 -90, -60 -95, 0 -80 C 60 -95, 150 -90, 170 -40 C 200 40, 220 120, 170 140 '
          'C 130 155, 100 110, 70 80 C 30 70, -30 70, -70 80 C -100 110, -130 155, -170 140 C -220 120, -200 40, -170 -40 Z" fill="#e9ecef" stroke="#9aa3a9" stroke-width="3"/>')
    s += '<circle cx="-95" cy="-20" r="30" fill="#2b2b2b"/><circle cx="45" cy="35" r="28" fill="#2b2b2b"/>'
    s += '<path d="M -55 30 h 16 v -16 h 16 v 16 h 16 v 16 h -16 v 16 h -16 v -16 h -16 z" fill="#3a3a3a" transform="translate(-10,0)"/>'
    for (bx, by, c) in [(105, -35, "#43a047"), (130, -60, "#fbc02d"), (80, -60, "#1e88e5"), (105, -85, "#e53935")]:
        s += f'<circle cx="{bx}" cy="{by+25}" r="13" fill="{c}"/>'
    if glow:
        s += '<circle cx="0" cy="-55" r="30" fill="#ffffff" opacity="0.9" filter="url(#glow)"/>'
    s += f'<circle cx="0" cy="-55" r="20" fill="{"#f1f8e9" if glow else "#cfd4d6"}" stroke="#777" stroke-width="2"/>'
    s += "</g>"
    return s

def led_strip(x, y, pattern, title):
    """draws a little timeline of LED on/off: pattern list of (on, duration_units)"""
    s = text(x, y, title, 16, "bold", "start", "#fff")
    t = 0
    for on, d in pattern:
        s += f'<rect x="{x + t*14}" y="{y+10}" width="{d*14-2}" height="18" rx="4" fill="{"#76ff03" if on else "#33402f"}"/>'
        t += d
    return s

def panel(x, y, w, h, title=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#0f1a14" fill-opacity="0.88" stroke="#4caf50" stroke-width="2"/>'
    if title: s += text(x + 18, y + 32, title, 20, "bold", "start", "#c8e6c9")
    return s

# ------------------------------------------------------------------ parts kit
def parts_kit(option):
    B = option == "B"
    W, H = 1700, 1100
    s = title_bar(W, f"OPTION {option}  -  parts you need",
                  "Lay everything out before you start.  The blue boards are SMD-to-DIP adapters that make the tiny parts easy to wire.")
    # perfboard
    bb = Board(60, 140, 14, 10, 24); s += bb.draw()
    s += text(60 + 7 * 24, 140 + 10 * 24 + 44, "Perfboard (about 7 x 5 cm)", 17, "bold", "middle", "#2b2014")
    # pico
    s += pico_alone(560, 390, 18)
    s += text(560, 610, "Raspberry Pi Pico W  or  Pico 2 W", 17, "bold", "middle", "#2b2014")
    # adapters
    items = [("Q1", "BSS138LT1G on a", "SOT-23-to-DIP adapter")]
    if B: items.append(("Q2", "BSS138LT1G on a", "SOT-23-to-DIP adapter"))
    items += [("R1", "10k (0603) on a", "2-pin SMD adapter")]
    if B: items.append(("R2", "10k (0603) on a", "2-pin SMD adapter"))
    items += [("R3", "1k (0603) on a", "2-pin SMD adapter"), ("D1", "1N5819WS (SOD-323)", "on a 2-pin adapter")]
    for i, (ref, l1, l2) in enumerate(items):
        x = 800 + (i % 3) * 290; y = 150 + (i // 3) * 220
        ab = Board(x, y, 4, 4, 30)
        if ref.startswith("Q"): s += sot23_adapter(ab, 1, 0, ref)
        elif ref == "D1": s += chip_adapter(ab, 0, 1, 3, 1, ref, "diode")
        else: s += chip_adapter(ab, 1, 0, 1, 3, ref, "res")
        s += text(x + 60, y + 150, l1, 15, "bold", "middle", "#2b2014") + text(x + 60, y + 170, l2, 15, "normal", "middle", "#2b2014")
    # headers
    y0 = 640
    hb = Board(90, y0, 6, 1, 26); s += header(hb, [(0, 0), (1, 0)]) + header(hb, [(3, 0), (4, 0), (5, 0)] + ([(6, 0)] if B else []))
    s += text(170, y0 + 70, f"Pin headers: 1x2 (J1) + 1x{4 if B else 3} (J2)", 16, "bold", "middle", "#2b2014")
    # wires
    for i, c in enumerate([PURPLE, BLACK, ORANGE, BLACK, YELLOW] + ([GREEN] if B else [])):
        s += wire_path(f"M {420} {660+i*26} C 520 {640+i*26}, 600 {690+i*26}, 720 {670+i*26}", c, 9)
    s += text(570, y0 + 200, "Hook-up wire + female Dupont lead (yellow)", 16, "bold", "middle", "#2b2014")
    # extension cable
    s += '<g filter="url(#shadow)"><rect x="840" y="650" width="330" height="70" rx="10" fill="url(#nylonblack)"/></g>'
    cols = ["#F57C00", "#1565C0", BLACK, GREEN, BLACK, BLACK, BLACK, BLACK, "#D32F2F", "#D32F2F", "#D32F2F", BLACK]
    for i, c in enumerate(cols):
        s += wire_path(f"M {860+i*26} 720 C {860+i*26} 800, {900+i*20} 830, {960+i*16} 880", c, 9)
    cols2 = ["#F57C00", "#F57C00", BLACK, "#D32F2F", BLACK, "#D32F2F", BLACK, "#9E9E9E", PURPLE, "#FBC02D", "#FBC02D", "#F57C00"]
    for i, c in enumerate(cols2):
        s += wire_path(f"M {860+i*26} 650 C {860+i*26} 600, {900+i*20} 590, {960+i*16} 560", c, 9)
    s += text(1005, 925, "24-pin ATX EXTENSION cable", 17, "bold", "middle", "#2b2014")
    s += text(1005, 948, "(colour-coded wires, NOT all-black)", 15, "normal", "middle", "#2b2014")
    if B:
        s += f'<g filter="url(#shadow)"><rect x="1300" y="640" width="110" height="110" rx="8" fill="#1b1b1b"/><circle cx="1355" cy="695" r="34" fill="#3a3a3a" stroke="#555" stroke-width="3"/></g>'
        s += text(1355, 790, "SW1 push button", 16, "bold", "middle", "#2b2014") + text(1355, 812, "(manual power on/off)", 15, "normal", "middle", "#2b2014")
    # tools
    s += label(1250 if not B else 1450, 840 if B else 650, ["ALSO", "soldering iron + thin solder", "multimeter (DC volts)", "heat-shrink tubing", "micro-USB data cable"], "#80DEEA", w=300 if not B else 240, size=14, title_size=17)
    s += footer(W, H, "Exact part numbers are in the parts table on the same page.")
    return svg(W, H, s)

# ------------------------------------------------------------------ prep adapters
def prep_adapters(option):
    W, H = 1700, 900
    s = title_bar(W, "Solder the SMD parts onto their adapter boards", "Flux, a fine tip and tweezers.  Check each MOSFET with the meter before it goes on the perfboard.")
    # big SOT-23 adapter
    ab = Board(140, 200, 4, 4, 80)
    s += sot23_adapter(ab, 1, 0, "Q1" if option == "A" else "Q1 / Q2")
    for i, n in enumerate(["1 = GATE", "2 = SOURCE", "3 = DRAIN"]):
        x, y = ab.xy(1, i)
        s += text(x + 230, y + 7, n, 20, "bold", "start", ["#1565C0", "#111", ORANGE][i])
    s += probe(ab.xy(1, 1)[0] + 6, ab.xy(1, 1)[1], "#D32F2F", 200, 230)
    s += probe(ab.xy(1, 2)[0] + 6, ab.xy(1, 2)[1] + 4, "#1b1b1b", 160, 230)
    s += label(40, 560, ["METER CHECK (diode mode)", "RED probe on pin 2 (Source)", "BLACK probe on pin 3 (Drain)", "= roughly 0.4 - 0.9 (built-in diode)", "Reversed probes = open / OL.", "Nothing like this? Chip is rotated", "or the adapter numbers differ."], "#FFE000", w=420, size=15, title_size=18)
    # resistor adapter
    rb = Board(820, 200, 3, 5, 70)
    s += chip_adapter(rb, 1, 0, 1, 3, "R1 / R3" if option == "A" else "R1 / R2 / R3", "res")
    s += label(760, 560, ["RESISTOR ADAPTERS", "10k may be marked 103 or 01C", "1k may be marked 102 or 01B", "(many 0603s are unmarked - measure)", "No direction - either way round."], "#80DEEA", w=420, size=15, title_size=18)
    # diode adapter
    db = Board(1250, 230, 5, 3, 70)
    s += chip_adapter(db, 0, 1, 3, 1, "D1", "diode")
    x, y = db.xy(3, 1)
    s += callout_ring(x, y, 30)
    s += label(1220, 560, ["DIODE ADAPTER (D1)", "Painted BAND = cathode.", "Mark the adapter pin on the", "band side with a pen: that pin", "goes toward the Pico (VSYS)."], "#FFB74D", w=420, size=15, title_size=18)
    s += footer(W, H, "Resistor marking codes vary by maker - if unsure, measure: 10k = about 10.0 k, 1k = about 1.0 k on the ohms range.")
    return svg(W, H, s)

# ------------------------------------------------------------------ flash
def flash():
    W, H = 1700, 950
    s = title_bar(W, "Flash the firmware (.UF2)", "Hold BOOTSEL, plug in USB, let go - then drag the .uf2 file onto the new drive.")
    s += pico_alone(420, 520, 26)
    # usb cable
    s += '<g filter="url(#shadow)"><rect x="385" y="140" width="70" height="80" rx="8" fill="#2b2b2b"/></g>' + wire_path("M 420 140 C 420 100, 520 100, 700 110", "#2b2b2b", 16)
    # finger
    bx, by = 420 - 26, 520 - 10 * 26 - 26 * 1.1 + 26 * 1.8
    s += f'<ellipse cx="{bx-14}" cy="{by+20}" rx="40" ry="56" fill="#e8b48f" stroke="#b07a56" stroke-width="3" opacity="0.9" transform="rotate(-25 {bx-14} {by+20})"/>'
    s += label(60, 300, ["1. HOLD BOOTSEL", "the small white button", "next to the USB socket"], "#FFE000", w=260, anchor_pt=(bx - 40, by))
    s += label(560, 140, ["2. PLUG IN USB", "while still holding,", "then let go"], "#FFE000", w=250)
    # computer window
    s += panel(820, 180, 820, 560, None)
    s += f'<rect x="820" y="180" width="820" height="44" rx="14" fill="#263238"/>' + text(840, 210, "File manager  -  new drive", 18, "bold", "start", "#fff")
    s += '<g filter="url(#softshadow)"><rect x="880" y="270" width="190" height="130" rx="10" fill="#cfd8dc"/><rect x="900" y="300" width="150" height="60" rx="6" fill="#90a4ae"/></g>'
    s += text(975, 430, "RPI-RP2  (Pico W)", 17, "bold", "middle", "#fff") + text(975, 455, "RP2350  (Pico 2 W)", 17, "bold", "middle", "#fff")
    s += '<g filter="url(#softshadow)"><path d="M 1330 520 h 90 l 30 30 v 110 h -120 z" fill="#ffffff"/><path d="M 1420 520 v 30 h 30" fill="#cfd8dc"/></g>'
    s += text(1390, 610, ".UF2", 22, "bold", "middle", "#1565C0")
    s += text(1390, 700, "GMX-BC250-Wake_Rev1_PicoW.uf2", 14, "normal", "middle", "#fff") + text(1390, 720, "or  ..._Pico2W.uf2", 14, "normal", "middle", "#fff")
    s += f'<path d="M 1320 580 C 1200 560, 1130 470, 1080 380" fill="none" stroke="#FFE000" stroke-width="6" stroke-dasharray="14,8"/>'
    s += '<polygon points="1068,360 1098,375 1074,392" fill="#FFE000"/>'
    s += label(860, 770, ["3. DRAG the .uf2 onto the drive", "Pico W -> ..._PicoW.uf2   |   Pico 2 W -> ..._Pico2W.uf2", "The drive closes by itself when done = finished."], "#FFE000", w=760)
    s += footer(W, H, "Use a micro-USB DATA cable (charge-only cables won't show the drive).  Anything already on the Pico is replaced.")
    return svg(W, H, s)

# ------------------------------------------------------------------ teach + bench test
def teach():
    W, H = 1700, 1000
    s = title_bar(W, "Teach the Pico your controller + bench test (USB power only, no wiring yet)",
                  "Keep the BC-250 OFF so the controller can't connect to it during this test.")
    s += pico_alone(330, 560, 24)
    s += '<g filter="url(#shadow)"><rect x="297" y="190" width="66" height="70" rx="8" fill="#2b2b2b"/></g>' + wire_path("M 330 190 C 330 150, 260 130, 120 140", "#2b2b2b", 15)
    # LED glow
    s += f'<circle cx="{330+24*0.98}" cy="{560-10*24+24*1.6}" r="14" fill="#76ff03" opacity="0.85" filter="url(#glow)"/>'
    s += gamepad(780, 520, 1.0, True)
    s += f'<path d="M 600 520 C 520 520, 470 520, 430 520" fill="none" stroke="#4fc3f7" stroke-width="5" stroke-dasharray="8,8"/>'
    s += text(520, 500, "a few cm", 17, "bold", "middle", "#0d47a1")
    s += panel(1040, 120, 630, 820, "Steps")
    steps = ["1. Plug the Pico into USB. LED: double flash",
             "   every 2 s = running, nothing taught yet.",
             "2. HOLD BOOTSEL 5-10 s, then let go.",
             "   LED blinks FAST = learn mode (30 s).",
             "3. Hold the controller next to the Pico and",
             "   switch it ON with its centre button",
             "   (normal power-on, not the pair button).",
             "4. ~3 s later: 3 LONG blinks = saved.",
             "5. Switch the controller OFF (hold the centre",
             "   button ~6 s). Wait 30 s.",
             "6. Switch it ON again: Pico LED goes SOLID",
             "   = it heard the controller.",
             "7. ~21 s later one long flash = 'no PC found'.",
             "   On the bench that is the CORRECT result."]
    for i, l in enumerate(steps):
        s += text(1062, 185 + i * 30, l, 17, "bold" if l[0].isdigit() else "normal", "start", "#fff")
    y = 640
    s += led_strip(1062, y, [(1, 1), (0, 1), (1, 1), (0, 9), (1, 1), (0, 1), (1, 1), (0, 9)], "Double flash = running, nothing taught")
    s += led_strip(1062, y + 60, [(1, 1), (0, 1)] * 12, "Fast blink = learn mode")
    s += led_strip(1062, y + 120, [(1, 4), (0, 3)] * 3, "3 long blinks = controller saved")
    s += led_strip(1062, y + 180, [(1, 1), (0, 14), (1, 1), (0, 14)], "Short flash every 2 s = listening")
    s += footer(W, H, "Optional: watch the log in any serial monitor at 115200 baud (e.g. Arduino IDE Serial Monitor).")
    return svg(W, H, s)

# ------------------------------------------------------------------ ATX extension cable taps
def atx_ext(option):
    B = option == "B"
    W, H = 1700, 1050
    s = title_bar(W, f"OPTION {option}  -  connect to the ATX power using a 24-pin EXTENSION cable",
                  "Plug the PSU's 24-pin plug into the extension cable.  Splice onto the extension cable's wires - never cut the PSU's own cable.  The far end is not used.")
    # PSU plug at left, extension female end
    s += '<g filter="url(#shadow)"><rect x="80" y="380" width="160" height="300" rx="12" fill="url(#nylonblack)"/></g>' + text(160, 710, "PSU plug", 17, "bold", "middle", "#2b2014")
    s += '<g filter="url(#shadow)"><rect x="240" y="370" width="170" height="320" rx="12" fill="#2a2a2a" stroke="#000"/></g>' + text(325, 720, "extension socket", 17, "bold", "middle", "#2b2014")
    s += wire_path("M 80 530 C 40 530, 30 560, 10 560", "#1b1b1b", 40)
    # wires of the extension cable fanned out
    colors = ["#F57C00", "#F57C00", BLACK, "#D32F2F", BLACK, "#D32F2F", BLACK, "#9E9E9E", PURPLE, "#FBC02D", "#FBC02D", "#F57C00",
              "#F57C00", "#1565C0", BLACK, GREEN, BLACK, BLACK, BLACK, None, "#D32F2F", "#D32F2F", "#D32F2F", BLACK]
    ys = {}
    k = 0
    for n, c in enumerate(colors, start=1):
        if c is None: continue
        y = 380 + k * 13.5
        ye = 150 + k * 36
        ys[n] = ye
        s += wire_path(f"M 410 {y} C 520 {y}, 560 {ye}, 700 {ye} L 1120 {ye} C 1180 {ye}, 1190 {420+k*12}, 1230 {420+k*12}", c, 9 if n not in (9, 15, 16) else 12)
        k += 1
    s += '<g filter="url(#shadow)"><rect x="1230" y="400" width="80" height="300" rx="12" fill="url(#nylonblack)"/></g>'
    s += text(1270, 735, "far end:", 15, "bold", "middle", "#2b2014") + text(1270, 755, "not used", 15, "bold", "middle", "#2b2014")
    # taps
    def splice(n, color, d_end, lab, lc, xs=900):
        ye = ys[n]
        r = f'<rect x="{xs-26}" y="{ye-11}" width="52" height="22" rx="6" fill="url(#solder)" stroke="#555"/>'
        r += f'<rect x="{xs-40}" y="{ye-14}" width="80" height="28" rx="8" fill="#000" fill-opacity="0.25"/>'
        r += wire_path(f"M {xs} {ye} " + d_end, color, 10)
        r += callout_ring(xs, ye, 26)
        return r
    s += splice(9, PURPLE, f"C {980} {ys[9]-60}, 1250 {ys[9]-50}, 1340 {ys[9]-60}", "", "")
    s += label(1340, ys[9] - 120, ["PURPLE (+5VSB)", "splice a wire -> J1 pin 1"], "#CE93D8", w=320, size=15, title_size=18)
    s += splice(15, BLACK, f"C {980} {ys[15]+20}, 1250 {ys[15]+20}, 1340 {ys[15]+10}", "", "", xs=850)
    s += label(1340, ys[15] - 40, ["BLACK (any black = ground)", "splice a wire -> J1 pin 2"], "#FFE000", w=320, size=15, title_size=18)
    if B:
        s += splice(16, GREEN, f"C {1000} {ys[16]+80}, 1250 {ys[16]+110}, 1340 {ys[16]+120}", "", "")
        s += label(1340, ys[16] + 80, ["GREEN (PS_ON)", "splice a wire -> J2-3", "(goes to Q2)"], "#69F0AE", w=320, size=15, title_size=18)
        note = ["OPTION B: green is NOT joined", "to black - the Pico switches", "the supply on through Q2."]
    else:
        g, k2 = ys[16], ys[17]
        s += callout_ring(1000, g, 26) + callout_ring(1000, k2, 26)
        s += wire_path(f"M 1000 {g} C 1040 {g}, 1040 {k2}, 1000 {k2}", BLACK, 8)
        s += f'<rect x="985" y="{g-12}" width="30" height="24" rx="6" fill="url(#solder)"/><rect x="985" y="{k2-12}" width="30" height="24" rx="6" fill="url(#solder)"/>'
        s += label(1340, ys[16] + 80, ["GREEN -> BLACK link", "short wire from GREEN (PS_ON)", "to a BLACK wire", "= supply always on"], "#69F0AE", w=320, size=15, title_size=18)
        note = ["OPTION A: the green-to-black link", "keeps the supply on all the time."]
    s += label(60, 800, ["HOW TO SPLICE", "strip ~5 mm of insulation from the middle", "of the wire, wrap your new wire round it,", "solder, cover with heat-shrink or tape."] + [""] + note, "#80DEEA", w=520, size=15, title_size=18)
    s += footer(W, H, "Unplug the PSU from the wall before splicing.  Go by wire COLOUR - you never need to count pins on a colour-coded cable.")
    return svg(W, H, s)

# ------------------------------------------------------------------ TPMS1 Dupont connect
def tpms_connect():
    W, H = 1600, 1120
    base = os.path.join(OUT, "R3_BC250_Top_TPMS1_Pin9.png")
    s = img_embed(base, 0, 0, W, H)
    # cover probe area + add Dupont housing on pin 9
    x0, p, yf = 560, 70, 720
    x9 = x0 + 4 * p
    s += f'<rect x="{x9-120}" y="{yf+40}" width="380" height="330" fill="#0f1a14" opacity="0"/>'
    s += f'<g filter="url(#shadow)"><rect x="{x9-17}" y="{yf-30}" width="34" height="92" rx="4" fill="#111"/><rect x="{x9-13}" y="{yf-26}" width="26" height="26" fill="#262626"/></g>'
    s += wire_path(f"M {x9} {yf+60} C {x9} {yf+160}, {x9+180} {yf+180}, {x9+260} {yf+330}", YELLOW, 13)
    s += label(30, 930, ["CONNECT: yellow Dupont lead", "push it onto pin 9 only, then run it", "to the wake board (J2, 'PC ON')"], "#FFF176", w=430, size=16, title_size=18)
    s = svg(W, H, s)
    return s

# ------------------------------------------------------------------ full system
def crop(src, box, name):
    from PIL import Image
    im = Image.open(os.path.join(OUT, src)).crop(box)
    p = os.path.join(OUT, "_crop_" + name + ".png"); im.save(p); return p, im.size

def system(option):
    B = option == "B"
    W, H = 1800, 1300
    s = title_bar(W, f"OPTION {option}  -  everything connected", "Check every wire against this picture before you plug the PSU back into the wall.")
    bp, bs = crop(f"S_{option}06_Build_Board_Option{option}.png", (316, 136, 1432, 996), "board" + option)
    k = 700 / bs[0]
    BX, BY = 560, 150
    s += img_embed(bp, BX, BY, 700, bs[1] * k)
    s += text(BX + 350, BY - 10, "Wake board", 22, "bold", "middle", "#2b2014")
    s += f'<rect x="{BX}" y="{BY}" width="700" height="{bs[1]*k}" fill="none" stroke="#263238" stroke-width="3" rx="4"/>'
    def pin(c, r):
        return BX + (330 + 32 * (c + 0.5) - 316) * k, BY + (150 + 32 * (r + 0.5) - 136) * k
    def thumb(src, box, name, x, y, w, cap):
        p, sz = crop(src, box, name); h = sz[1] * w / sz[0]
        r = img_embed(p, x, y, w, h) + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#263238" stroke-width="3" rx="4"/>'
        r += text(x + w / 2, y + h + 26, cap, 18, "bold", "middle", "#2b2014")
        return r, (x, y, w, h)
    ext = f"S_{option}07_ATX_Extension.png"
    t1, e1 = thumb(ext, (560, 120, 1310, 800), "ext" + option, 20, 150, 480, "ATX extension cable splices")
    t2, e2 = thumb("R4_BC250_Top_AUTO_PWRON1.png", (180, 380, 640, 660), "apo", 20, 720, 480, "AUTO_PWRON1 jumper on pins 2-3")
    t3, e3 = thumb("R1_BC250_Bottom_PowerButton_Ground.png", (780, 470, 1120, 780), "pb", 1420, 140, 300, "power-button pad (orange)")
    t4, e4 = thumb("R1_BC250_Bottom_PowerButton_Ground.png", (330, 650, 640, 900), "gnd", 1420, 470, 300, "ground pad (black)")
    t5, e5 = thumb("S_10_TPMS1_Connect.png", (620, 560, 1100, 900), "tp", 1420, 770, 300, "TPMS1 pin 9 (yellow Dupont)")
    s += t1 + t2 + t3 + t4 + t5
    j1a, j1b = pin(1, 2), pin(1, 3)
    j2 = [pin(c, 24) for c in ((7, 8, 9, 10) if B else (7, 8, 9))]
    ex = e1[0] + e1[2]
    s += wire_path(f"M {j1a[0]} {j1a[1]} C {j1a[0]-60} {j1a[1]}, {ex+40} {e1[1]+150}, {ex} {e1[1]+140}", PURPLE, 8)
    s += wire_path(f"M {j1b[0]} {j1b[1]} C {j1b[0]-60} {j1b[1]+20}, {ex+40} {e1[1]+330}, {ex} {e1[1]+320}", BLACK, 8)
    s += wire_path(f"M {j2[0][0]} {j2[0][1]} C {j2[0][0]} 780, 1340 780, 1340 {e3[1]+e3[3]/2} L {e3[0]} {e3[1]+e3[3]/2}", ORANGE, 8)
    s += wire_path(f"M {j2[1][0]} {j2[1][1]} C {j2[1][0]} 800, 1370 800, 1370 {e4[1]+e4[3]/2} L {e4[0]} {e4[1]+e4[3]/2}", BLACK, 8)
    if B:
        s += wire_path(f"M {j2[2][0]} {j2[2][1]} C {j2[2][0]} 760, {ex+30} 760, {ex+30} {e1[1]+380} L {ex} {e1[1]+380}", GREEN, 8)
    s += wire_path(f"M {j2[-1][0]} {j2[-1][1]} C {j2[-1][0]} 820, 1395 820, 1395 {e5[1]+e5[3]/2} L {e5[0]} {e5[1]+e5[3]/2}", YELLOW, 8)
    rows = ["J1-1  ->  ATX PURPLE (+5VSB) splice", "J1-2  ->  ATX BLACK (ground) splice",
            "J2-1  ->  BC-250 power-button pad (orange)", "J2-2  ->  BC-250 ground pad (black)"]
    if B: rows.append("J2-3  ->  ATX GREEN (PS_ON) splice")
    rows.append(("J2-4" if B else "J2-3") + "  ->  TPMS1 pin 9 (yellow Dupont)")
    rows.append("AUTO_PWRON1 jumper on pins 2-3")
    rows.append("ATX GREEN linked to BLACK (always on)" if not B else "ATX GREEN NOT linked to black")
    s += label(560, 880, ["CHECKLIST"] + rows, "#FFE000", w=700, size=17, title_size=20)
    s += footer(W, H, "Close-ups are taken from the step pictures earlier in this section.")
    return svg(W, H, s)

# ------------------------------------------------------------------ terminal
def terminal():
    W, H = 1600, 760
    s = title_bar(W, "Bazzite: make 'Sleep' shut down instead (the BC-250 can't wake from sleep)",
                  "Open a terminal on the BC-250 (Desktop Mode -> Konsole) and type these two lines.")
    s += '<g filter="url(#shadow)"><rect x="120" y="140" width="1360" height="470" rx="12" fill="#1e1f22"/></g>'
    s += '<rect x="120" y="140" width="1360" height="44" rx="12" fill="#2d2f33"/>' + text(800, 170, "Terminal", 17, "bold", "middle", "#ccc")
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        s += f'<circle cx="{150+i*28}" cy="162" r="9" fill="{c}"/>'
    lines = [("$ ", "sudo ln -sf /usr/lib/systemd/system/poweroff.target /etc/systemd/system/suspend.target", "#e0e0e0"),
             ("", "[sudo] password:            <- type your password (nothing shows), press Enter", "#9e9e9e"),
             ("$ ", "sudo systemctl daemon-reload", "#e0e0e0"),
             ("", "", "#e0e0e0"),
             ("# ", "To undo later:", "#81c784"),
             ("$ ", "sudo rm /etc/systemd/system/suspend.target", "#bdbdbd"),
             ("$ ", "sudo systemctl daemon-reload", "#bdbdbd")]
    for i, (pr, l, c) in enumerate(lines):
        s += text(150, 240 + i * 46, pr + l, 21, "normal", "start", c, family="DejaVu Sans Mono")
    s += footer(W, H, "Commands from the tfabris/BC-250 and elektricm BC-250 guides; not re-tested for this project.")
    return svg(W, H, s)

# ------------------------------------------------------------------ first test
def first_test(option):
    B = option == "B"
    W, H = 1700, 820
    s = title_bar(W, f"OPTION {option}  -  first real test", "PSU plugged in at the wall, BC-250 off, wait 60 s after any shutdown, then switch the controller on.")
    s += panel(40, 130, 520, 560, "1. Controller ON") + gamepad(300, 420, 1.0, True)
    s += panel(590, 130, 520, 560, "2. Pico LED goes SOLID") + pico_alone(850, 470, 18)
    s += f'<circle cx="{850+18*0.98}" cy="{470-10*18+18*1.6}" r="16" fill="#76ff03" filter="url(#glow)"/>'
    s += panel(1140, 130, 520, 560, "3. BC-250 starts (~1.5 s)")
    for i, (cx, col) in enumerate(((1330, "#66BB6A"), (1470, "#42A5F5"))):
        s += f'<rect x="{cx-50}" y="330" width="100" height="160" rx="16" fill="url(#lightpipe)" stroke="#9fb0b8" stroke-width="3"/>'
        if i == 0: s += f'<rect x="{cx-50}" y="330" width="100" height="160" rx="16" fill="{col}" opacity="0.55" filter="url(#glow)"/>'
    s += text(1400, 540, "power light comes on", 18, "bold", "middle", "#c8e6c9")
    extra = "About 10 s after the PC shuts down, the PSU switches off (Option B)." if B else "The PSU stays on all the time (Option A) - that is normal."
    s += label(40, 705, ["If the controller switched itself off while the PC booted, press its centre button again.", extra], "#80DEEA", w=1620, size=16, title_size=18)
    return svg(W, H, s)

save(OUT, "S_A01_Parts_OptionA", parts_kit("A")); save(OUT, "S_B01_Parts_OptionB", parts_kit("B"))
save(OUT, "S_A02_Prep_Adapters", prep_adapters("A")); save(OUT, "S_B02_Prep_Adapters", prep_adapters("B"))
save(OUT, "S_04_Flash_Firmware", flash())
save(OUT, "S_05_Teach_Controller", teach())
save(OUT, "S_A07_ATX_Extension", atx_ext("A")); save(OUT, "S_B07_ATX_Extension", atx_ext("B"))
save(OUT, "S_A11_System_OptionA", system("A")); save(OUT, "S_B11_System_OptionB", system("B"))
save(OUT, "S_12_Bazzite_Sleep_Fix", terminal())
save(OUT, "S_A13_First_Test", first_test("A")); save(OUT, "S_B13_First_Test", first_test("B"))
print("ok")
