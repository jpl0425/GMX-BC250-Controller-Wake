# Generates all wiring diagram pictures (SVG -> PNG via rsvg-convert)
import subprocess, os
OUT = os.path.dirname(os.path.abspath(__file__))
F = "DejaVu Sans"

C = dict(purple="#7B2FBE", black="#222222", green="#1E9E3A", red="#D32F2F", blue="#1565C0",
         orange="#EF6C00", yellow="#C9A400", grey="#777777", pcb="#1F6F43", pico="#2E7D32",
         bg="#FFFFFF", box="#F4F6F8", edge="#455A64", hl="#FFEB3B")

def svg(w, h, body, title=None):
    t = f'<text x="{w/2}" y="40" font-family="{F}" font-size="28" font-weight="bold" text-anchor="middle" fill="#111">{title}</text>' if title else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#fff"/>{t}{body}</svg>'

def text(x, y, s, size=18, weight="normal", anchor="start", fill="#111", italic=False):
    st = ' font-style="italic"' if italic else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-family="{F}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}"{st}>{s}</text>'

def box(x, y, w, h, head, lines, color, width=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{C["box"]}" stroke="{color}" stroke-width="3"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="10" fill="{color}"/><rect x="{x}" y="{y+20}" width="{w}" height="14" fill="{color}"/>'
    s += text(x + w/2, y + 24, head, 17, "bold", "middle", "#fff")
    for i, l in enumerate(lines):
        s += text(x + 10, y + 58 + i*22, l, 16)
    return s

def wire(pts, color, w=6, dash=None):
    d = " ".join(f"{x},{y}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>'

def dot(x, y, color="#222", r=7):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'

def resistor(x, y, label, val, vertical=False):
    # body centred at x,y
    if vertical:
        s = f'<rect x="{x-14}" y="{y-35}" width="28" height="70" rx="6" fill="#D7C9A7" stroke="#333" stroke-width="2"/>'
        s += text(x + 24, y - 4, label, 17, "bold") + text(x + 24, y + 18, val, 15)
    else:
        s = f'<rect x="{x-35}" y="{y-14}" width="70" height="28" rx="6" fill="#D7C9A7" stroke="#333" stroke-width="2"/>'
        s += text(x, y - 22, f"{label}  {val}", 16, "bold", "middle")
    return s

def gnd(x, y, label=True):
    s = wire([(x, y), (x, y + 18)], C["black"], 4)
    s += f'<line x1="{x-18}" y1="{y+18}" x2="{x+18}" y2="{y+18}" stroke="#222" stroke-width="4"/>'
    s += f'<line x1="{x-11}" y1="{y+26}" x2="{x+11}" y2="{y+26}" stroke="#222" stroke-width="4"/>'
    s += f'<line x1="{x-4}" y1="{y+34}" x2="{x+4}" y2="{y+34}" stroke="#222" stroke-width="4"/>'
    if label: s += text(x, y + 56, "GND", 14, "bold", "middle")
    return s

def sot23(x, y, ref, part):
    """SOT-23 MOSFET drawn as top view. Returns svg and pin coords dict.
    Body centred at x,y. Pin 3 (Drain) top centre, pins 1 (Gate) bottom-left, 2 (Source) bottom-right."""
    s = f'<rect x="{x-40}" y="{y-26}" width="80" height="52" rx="5" fill="#333" stroke="#000" stroke-width="2"/>'
    s += f'<circle cx="{x-28}" cy="{y+14}" r="4" fill="#ddd"/>'  # pin-1 dot
    for (px, py, n) in [(x, y-26, 3), (x-22, y+26, 1), (x+22, y+26, 2)]:
        dy = -16 if n == 3 else 0
        s += f'<rect x="{px-6}" y="{py+dy}" width="12" height="16" fill="#BDBDBD" stroke="#555"/>'
    s += text(x, y + 6, ref, 17, "bold", "middle", "#fff")
    s += text(x + 50, y - 30, f"{ref} = {part}", 15, "bold")
    s += text(x + 50, y - 10, "(top view)", 13, italic=True)
    s += text(x + 12, y - 48, "3 Drain", 14, "bold", "start", C["orange"])
    s += text(x - 34, y + 62, "1 Gate", 14, "bold", "end", C["blue"])
    s += text(x + 34, y + 62, "2 Source", 14, "bold", "start", "#222")
    pins = {"D": (x, y - 42), "G": (x - 22, y + 42), "S": (x + 22, y + 42)}
    return s, pins

def diode(x, y, ref, part):
    # horizontal, anode left, cathode (band) right; body centred x,y
    s = f'<rect x="{x-32}" y="{y-14}" width="64" height="28" rx="4" fill="#333"/>'
    s += f'<rect x="{x+18}" y="{y-14}" width="10" height="28" fill="#E0E0E0"/>'
    s += f'<polygon points="{x-14},{y-9} {x-14},{y+9} {x+6},{y}" fill="#fff"/><line x1="{x+7}" y1="{y-9}" x2="{x+7}" y2="{y+9}" stroke="#fff" stroke-width="3"/>'
    s += text(x, y - 24, f"{ref}  {part}", 16, "bold", "middle")
    s += text(x - 36, y + 38, "anode", 13, anchor="end") + text(x + 36, y + 38, "band = cathode", 13)
    return s

def save(name, content):
    p = os.path.join(OUT, name + ".svg")
    open(p, "w").write(content)
    subprocess.run(["rsvg-convert", "-z", "1", "-o", os.path.join(OUT, name + ".png"), p], check=True)

# ---------------------------------------------------------------------------
# Figure 2: wiring, one connection group per strip
# ---------------------------------------------------------------------------
def fig_wiring():
    W, H = 1600, 1940
    b = ""
    def strip(y, h, n, title, note, color):
        s = f'<rect x="20" y="{y}" width="{W-40}" height="{h}" rx="14" fill="#FAFAFA" stroke="#CFD8DC" stroke-width="2"/>'
        s += f'<circle cx="58" cy="{y+36}" r="22" fill="{color}"/>' + text(58, y + 43, str(n), 22, "bold", "middle", "#fff")
        s += text(92, y + 44, title, 24, "bold")
        if note: s += text(W - 40, y + 44, note, 16, anchor="end", italic=True, fill="#555")
        return s

    # 1 power
    y = 70
    b += strip(y, 210, 1, "Power for the Pico (always on, even when the PC is off)", "", C["purple"])
    b += box(60, y + 70, 330, 110, "ATX 24-pin plug", ["PURPLE wire  =  pin 9", "+5VSB (standby 5 V)"], C["purple"])
    b += wire([(390, y + 125), (640, y + 125)], C["purple"])
    b += diode(700, y + 125, "D1", "1N5819WS")
    b += wire([(760, y + 125), (1150, y + 125)], C["red"])
    b += box(1150, y + 70, 390, 110, "Pico W  -  pin 39  VSYS", ["5 V power input", "(2nd pin from the top, USB side)"], C["pico"])
    b += text(900, y + 112, "about 4.7 V", 15, anchor="middle", fill=C["red"])

    # 2 ground
    y = 300
    b += strip(y, 290, 2, "Ground (all three must be joined)", "Every GND on the wake board is one shared ground", C["black"])
    b += box(60, y + 70, 330, 110, "ATX 24-pin plug", ["BLACK wire  =  pin 15 or 17", "COM (ground)"], C["black"])
    b += wire([(390, y + 125), (1150, y + 125)], C["black"])
    b += dot(770, y + 125)
    b += wire([(770, y + 125), (770, y + 185)], C["black"])
    b += box(1150, y + 70, 390, 110, "Pico W  -  pin 38  GND", ["(3rd pin from the top, USB side)", "pins 3, 8 and 13 are GND too"], C["pico"])
    b += box(575, y + 185, 390, 90, "BC-250  ground pad", ["(see BC-250 picture, panel C)"], C["black"])
    # 3 power button
    y = 610
    b += strip(y, 330, 3, "Power button  (Q1 'presses' the BC-250 power button)", "Q1 drain + source go across the button", C["orange"])
    b += box(60, y + 80, 330, 110, "Pico W  -  pin 4  GP2", ["Power-button output", "(4th pin from the top, left)"], C["pico"])
    s, p = sot23(700, y + 170, "Q1", "BSS138LT1G")
    b += s
    b += wire([(390, y + 135), (560, y + 135), (560, y + 250), (p["G"][0], y + 250), p["G"]], C["blue"])
    b += dot(560, y + 250, C["blue"])
    b += wire([(560, y + 250), (470, y + 250)], C["blue"], 4)
    b += resistor(430, y + 250, "R1", "10k")
    b += wire([(395, y + 250), (330, y + 250), (330, y + 262)], C["black"], 4) + gnd(330, y + 262, False)
    b += text(80, y + 290, "R1 keeps Q1 off", 14, italic=True, fill="#555")
    b += text(80, y + 308, "while the Pico starts", 14, italic=True, fill="#555")
    b += wire([p["S"], (p["S"][0], y + 262)], C["black"], 4) + gnd(p["S"][0], y + 262)
    b += wire([p["D"], (p["D"][0], y + 100), (1150, y + 100), (1150, y + 135)], C["orange"])
    b += box(1150, y + 80, 390, 120, "BC-250  power-button pad", ["found with the meter test", "(BC-250 picture, panel C)"], C["orange"])
    b += text(980, y + 92, "orange wire", 15, anchor="middle", fill=C["orange"])

    # 4 PS_ON
    y = 960
    b += strip(y, 330, 4, "Power supply ON/OFF  (Q2 - only for Option B)", "Option A: leave Q2 + R2 out, keep your PS_ON jumper", C["green"])
    b += box(60, y + 80, 330, 110, "Pico W  -  pin 5  GP3", ["PS_ON output", "(5th pin from the top, left)"], C["pico"])
    s, p = sot23(700, y + 170, "Q2", "BSS138LT1G")
    b += s
    b += wire([(390, y + 135), (560, y + 135), (560, y + 250), (p["G"][0], y + 250), p["G"]], C["blue"])
    b += dot(560, y + 250, C["blue"])
    b += wire([(560, y + 250), (470, y + 250)], C["blue"], 4)
    b += resistor(430, y + 250, "R2", "10k")
    b += wire([(395, y + 250), (330, y + 250), (330, y + 262)], C["black"], 4) + gnd(330, y + 262, False)
    b += wire([p["S"], (p["S"][0], y + 262)], C["black"], 4) + gnd(p["S"][0], y + 262)
    b += wire([p["D"], (p["D"][0], y + 100), (1150, y + 100), (1150, y + 135)], C["green"])
    b += box(1150, y + 80, 390, 110, "ATX 24-pin plug", ["GREEN wire  =  pin 16", "PS_ON (ground it = supply on)"], C["green"])
    b += text(980, y + 92, "green wire", 15, anchor="middle", fill=C["green"])

    # 5 sense
    y = 1310
    b += strip(y, 220, 5, "'PC is on' signal  (3.3 V only while the BC-250 is running)", "", C["yellow"])
    b += box(60, y + 70, 330, 120, "BC-250  TPMS1  pin 9", ["the '3V' pin", "(see BC-250 picture)"], C["yellow"])
    b += wire([(390, y + 130), (665, y + 130)], C["yellow"])
    b += resistor(700, y + 130, "R3", "1k")
    b += wire([(735, y + 130), (1150, y + 130)], C["yellow"])
    b += box(1150, y + 70, 390, 120, "Pico W  -  pin 6  GP4", ["PC-on input", "(6th pin from the top, left)"], C["pico"])
    b += text(700, y + 180, "R3 protects the Pico pin", 14, "normal", "middle", "#555", True)

    # 6 optional
    y = 1550
    b += strip(y, 360, 6, "Optional: your own button and status LED", "Not needed - the Pico's BOOTSEL button also works", C["grey"])
    b += box(60, y + 70, 330, 110, "Pico W  -  pin 7  GP5", ["Button input", "(7th pin from the top, left)"], C["pico"])
    b += wire([(390, y + 125), (640, y + 125)], C["grey"])
    # push button symbol
    bx = 700
    b += dot(bx - 50, y + 125, "#222", 6) + dot(bx + 50, y + 125, "#222", 6)
    b += wire([(bx - 50, y + 105), (bx + 50, y + 105)], "#222", 4) + wire([(bx, y + 105), (bx, y + 82)], "#222", 4)
    b += wire([(bx - 20, y + 82), (bx + 20, y + 82)], "#222", 4)
    b += text(bx, y + 66, "SW1  momentary push button", 15, "bold", "middle")
    b += wire([(bx + 50, y + 125), (bx + 200, y + 125), (bx + 200, y + 140)], C["black"], 4) + gnd(bx + 200, y + 140)
    b += box(60, y + 210, 330, 110, "Pico W  -  pin 9  GP6", ["Status LED output", "(9th pin from the top, left)"], C["pico"])
    b += wire([(390, y + 265), (665, y + 265)], C["grey"])
    b += resistor(700, y + 265, "R4", "470R")
    b += wire([(735, y + 265), (830, y + 265)], C["grey"])
    lx = 870
    b += f'<polygon points="{lx-25},{y+250} {lx-25},{y+280} {lx},{y+265}" fill="#43A047"/><line x1="{lx+1}" y1="{y+248}" x2="{lx+1}" y2="{y+282}" stroke="#222" stroke-width="4"/>'
    b += text(lx - 12, y + 238, "LED1", 16, "bold", "middle") + text(lx - 12, y + 310, "long leg (+) left", 13, anchor="middle")
    b += wire([(lx + 2, y + 265), (lx + 80, y + 265), (lx + 80, y + 280)], C["black"], 4) + gnd(lx + 80, y + 280)

    return svg(W, H, b, "GMX BC-250 Controller Wake  -  Wiring (Rev 1)")

# ---------------------------------------------------------------------------
# Figure 3: Pico W pin map
# ---------------------------------------------------------------------------
def fig_pico():
    W, H = 1500, 1110
    left = ["GP0", "GP1", "GND", "GP2", "GP3", "GP4", "GP5", "GND", "GP6", "GP7", "GP8", "GP9", "GND", "GP10", "GP11", "GP12", "GP13", "GND", "GP14", "GP15"]
    right = ["VBUS", "VSYS", "GND", "3V3_EN", "3V3(OUT)", "ADC_VREF", "GP28", "GND", "GP27", "GP26", "RUN", "GP22", "GND", "GP21", "GP20", "GP19", "GP18", "GND", "GP17", "GP16"]
    use = {4: ("Q1 gate  (strip 3)", C["orange"]), 5: ("Q2 gate  (strip 4)", C["green"]), 6: ("from R3 - TPMS1 pin 9  (strip 5)", C["yellow"]),
           7: ("button SW1 (optional)", C["grey"]), 8: ("GND", C["black"]), 9: ("R4 - LED (optional)", C["grey"]),
           39: ("from D1 - ATX purple +5VSB  (strip 1)", C["purple"]), 38: ("GND - ATX black COM  (strip 2)", C["black"])}
    bx, by, bw = 560, 150, 360
    pitch = 42
    bh = pitch * 20 + 60
    b = f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="{C["pico"]}" stroke="#123" stroke-width="3"/>'
    b += f'<rect x="{bx+bw/2-50}" y="{by-30}" width="100" height="55" rx="6" fill="#B0BEC5" stroke="#555" stroke-width="2"/>'
    b += text(bx + bw/2, by - 40, "micro-USB end", 16, "bold", "middle")
    b += f'<rect x="{bx+bw/2-70}" y="{by+330}" width="140" height="140" rx="6" fill="#263238"/>' + text(bx + bw/2, by + 408, "RP2040 / RP2350", 14, "bold", "middle", "#fff")
    b += f'<rect x="{bx+bw/2-70}" y="{by+520}" width="140" height="110" rx="6" fill="#B0BEC5" stroke="#555"/>' + text(bx + bw/2, by + 582, "wireless chip", 14, "bold", "middle", "#333")
    b += f'<circle cx="{bx+bw/2}" cy="{by+120}" r="18" fill="#ECEFF1" stroke="#333" stroke-width="2"/>' + text(bx + bw/2, by + 158, "BOOTSEL", 13, "bold", "middle", "#fff")
    b += text(bx + bw/2, by + bh - 20, "TOP VIEW  (parts side up)", 15, "bold", "middle", "#fff")
    for i in range(20):
        y = by + 50 + i * pitch
        for side, names, num in (("L", left, i + 1), ("R", right, 40 - i)):
            x = bx + 22 if side == "L" else bx + bw - 22
            hl = num in use
            col = use[num][1] if hl else "#C8A64B"
            b += f'<circle cx="{x}" cy="{y}" r="{11 if hl else 8}" fill="{col}" stroke="#000" stroke-width="{3 if hl else 1}"/>'
            nm = names[i]
            if side == "L":
                b += text(x + 20, y + 6, f"{num}  {nm}", 15, "bold" if hl else "normal", "start", "#fff")
                if hl:
                    b += wire([(bx - 4, y), (bx - 40, y)], use[num][1], 4)
                    b += text(bx - 48, y + 6, f"pin {num} {nm} - {use[num][0]}", 16, "bold", "end", "#111")
            else:
                b += text(x - 20, y + 6, f"{nm}  {num}", 15, "bold" if hl else "normal", "end", "#fff")
                if hl:
                    b += wire([(bx + bw + 4, y), (bx + bw + 40, y)], use[num][1], 4)
                    b += text(bx + bw + 48, y + 6, f"pin {num} {nm} - {use[num][0]}", 16, "bold", "start", "#111")
    b += text(W/2, H - 18, "Same pin layout on the Pico W and the Pico 2 W.  Pin 1 is top-left with the USB end at the top.", 17, anchor="middle", italic=True, fill="#333")
    return svg(W, H, b, "Pico W / Pico 2 W  -  pins used")

# ---------------------------------------------------------------------------
# Figure 4: BC-250 connection points (illustrations)
# ---------------------------------------------------------------------------
def fig_bc250():
    W, H = 1600, 1250
    b = ""
    # --- panel A: TPMS1 header
    b += f'<rect x="30" y="70" width="760" height="560" rx="14" fill="{C["pcb"]}" stroke="#0B3D24" stroke-width="3"/>'
    b += text(50, 105, "A.  TPMS1 header  (top side of the board)", 22, "bold", fill="#fff")
    hx, hy, p = 110, 300, 70
    b += f'<rect x="{hx-35}" y="{hy-40}" width="{p*9+10}" height="{p+80}" rx="6" fill="none" stroke="#fff" stroke-width="3"/>'
    b += text(hx - 25, hy + p + 85, "TPMS1", 26, "bold", fill="#fff")
    b += f'<polygon points="{hx-45},{hy+p+40} {hx-25},{hy+p+30} {hx-25},{hy+p+50}" fill="#fff"/>'
    b += text(hx + 90, hy + p + 82, "<- triangle = pin 1 end", 15, fill="#fff", italic=True)
    gap_row = 0   # the row that holds the missing pin (drawn on top here)
    for col in range(9):
        for row in range(2):
            x = hx + col * p - 10
            y = hy + (p if row == 1 else 0)
            if row == gap_row and col == 6:
                b += f'<rect x="{x-12}" y="{y-12}" width="24" height="24" fill="none" stroke="#FFCC80" stroke-width="3" stroke-dasharray="5,4"/>'
                b += text(x, y - 44, "MISSING", 14, "bold", "middle", "#FFCC80") + text(x, y - 26, "PIN", 14, "bold", "middle", "#FFCC80")
                continue
            hl = (row == gap_row and col == 4)
            mid = (row == gap_row and col == 5)
            b += f'<rect x="{x-15}" y="{y-15}" width="30" height="30" fill="#111"/>'
            b += f'<rect x="{x-6}" y="{y-6}" width="12" height="12" fill="{C["hl"] if hl else "#D4AF37"}"/>'
            if mid: b += text(x, y - 26, "skip", 14, "bold", "middle", "#fff")
            if row == gap_row and col == 7: b += text(x, y - 26, "pin 15", 13, "normal", "middle", "#FFCC80")
    x9 = hx + 4 * p - 10; y9 = hy
    b += f'<circle cx="{x9}" cy="{y9}" r="26" fill="none" stroke="{C["hl"]}" stroke-width="5"/>'
    b += text(x9, y9 - 34, "PIN 9", 16, "bold", "middle", C["hl"])
    b += text(50, 150, "1. Find the MISSING pin (pin 13).", 17, "bold", fill="#fff")
    b += text(50, 174, "2. In the SAME row, move toward the triangle end: skip one pin,", 16, fill="#fff")
    b += text(50, 198, "   the next one is PIN 9 = '3V'  ->  goes to R3 (strip 5).", 16, "bold", fill=C["hl"])
    b += text(50, 480, "3. CHECK with a meter before soldering/connecting (PSU plugged in):", 16, "bold", fill="#fff")
    b += text(70, 504, "BC-250 OFF  ->  pin 9 reads 0 V", 16, fill="#fff")
    b += text(70, 528, "BC-250 ON    ->  pin 9 reads about 3.3 V", 16, fill="#fff")
    b += text(70, 552, "If it reads 3.3 V while the PC is OFF, it is the wrong pin.", 16, fill="#FFCC80")
    b += text(50, 612, "Drawn illustration - which row is on top may be mirrored on your board.", 14, italic=True, fill="#fff")

    # --- panel B: AUTO_PWRON1
    b += f'<rect x="810" y="70" width="760" height="560" rx="14" fill="{C["pcb"]}" stroke="#0B3D24" stroke-width="3"/>'
    b += text(830, 105, "B.  AUTO_PWRON1 jumper  (top side, near battery)", 22, "bold", fill="#fff")
    jx, jy, jp = 1010, 330, 80
    for i in range(3):
        x = jx + i * jp
        b += f'<rect x="{x-22}" y="{jy-22}" width="44" height="44" fill="#111"/><rect x="{x-7}" y="{jy-7}" width="14" height="14" fill="#D4AF37"/>'
        b += text(x, jy + 60, str(i + 1), 22, "bold", "middle", "#fff")
    b += f'<polygon points="{jx-50},{jy+52} {jx-30},{jy+42} {jx-30},{jy+62}" fill="#fff"/>'
    b += f'<rect x="{jx+jp-34}" y="{jy-40}" width="{jp+68}" height="80" rx="8" fill="#212121" stroke="{C["hl"]}" stroke-width="5" opacity="0.92"/>'
    b += text(jx + jp*1.5, jy + 6, "JUMPER", 18, "bold", "middle", C["hl"])
    b += text(jx + jp, jy + 120, "AUTO_PWRON1", 24, "bold", "middle", "#fff")
    b += text(840, 480, "Put the jumper on pins 2-3 (the two pins AWAY from the triangle).", 18, "bold", fill=C["hl"])
    b += text(840, 508, "= 'wait for power button' mode.  Needed for BOTH wiring options.", 16, fill="#fff")
    b += text(840, 540, "Pins 1-2 = board turns itself on whenever it gets 12 V", 16, fill="#fff")
    b += text(840, 564, "(do NOT use that with this wake board).", 16, fill="#fff")

    # --- panel C: power button pads (underside)
    b += f'<rect x="30" y="650" width="1540" height="560" rx="14" fill="{C["pcb"]}" stroke="#0B3D24" stroke-width="3"/>'
    b += text(50, 685, "C.  Power-button pad + ground pad  (BOTTOM side of the board, rear edge)", 22, "bold", fill="#fff")
    b += text(50, 722, "Drawn illustration, NOT a photo - exact pad positions may differ on your board.", 16, "bold", fill="#FFCC80")
    b += text(50, 746, "Reference photo: GitHub tfabris/BC-250, 'Power Button Solder Points'.  Pads can lift - use strain relief.", 16, fill="#fff")
    b += text(50, 770, "SOLDER only with the power supply UNPLUGGED from the wall.  Never let a probe touch two legs at once.", 16, "bold", fill="#fff")
    # instructions (left)
    b += text(50, 820, "Find the power-button pad (meter on DC volts):", 18, "bold", fill=C["hl"])
    for i, l in enumerate(["1. PSU plugged in, BC-250 OFF, black probe on a USB shield (ground).",
                           "2. Touch each leg of the power button with the red probe.",
                           "3. Have a helper HOLD the real power button down.",
                           "4. The leg that drops to 0 V while held, and comes back",
                           "    when released, is the power-button pad  ->  orange wire (Q1 drain).",
                           "    (The PC will start when the button is pressed - that is OK.)"]):
        b += text(60, 850 + i * 24, l, 16, "bold" if i in (3, 4) else "normal", fill="#fff")
    # board edge + ports along bottom
    b += f'<rect x="30" y="1150" width="1540" height="60" fill="#B0BEC5"/>' + text(800, 1190, "REAR EDGE  (I/O ports side)", 18, "bold", "middle", "#333")
    for px, w, lab in [(120, 200, "USB"), (360, 170, "HDMI / DP"), (580, 200, "USB")]:
        b += f'<rect x="{px}" y="{1080}" width="{w}" height="70" fill="#9E9E9E" stroke="#555" stroke-width="2"/>' + text(px + w/2, 1122, lab, 16, "bold", "middle", "#222")
    # ground pad
    b += f'<circle cx="680" cy="1040" r="18" fill="#C0C0C0" stroke="#666" stroke-width="3"/><circle cx="680" cy="1040" r="7" fill="#555"/>'
    b += wire([(662, 1040), (560, 1040)], C["black"], 5)
    b += text(550, 1035, "ground pad", 16, "bold", "end", "#fff")
    b += text(550, 1057, "(a USB shield leg) - black wire", 14, anchor="end", fill="#fff")
    # buttons
    for i, (lab, col) in enumerate([("POWER (green)", "#66BB6A"), ("RESET (blue)", "#42A5F5")]):
        cx = 960 + i * 200
        b += f'<rect x="{cx-45}" y="1065" width="90" height="85" rx="8" fill="#ECEFF1" stroke="#555" stroke-width="2"/>'
        b += f'<circle cx="{cx}" cy="1105" r="26" fill="{col}" opacity="0.8"/>'
        b += text(cx, 1170 + 0, "", 1)
        b += text(cx + 55, 1100, lab, 15, "bold", "start", "#fff") if i == 1 else text(cx - 55, 1100, lab, 15, "bold", "end", "#fff")
    # legs of power button
    for (lx, ly) in [(925, 1000), (995, 1000), (925, 940), (995, 940)]:
        b += f'<circle cx="{lx}" cy="{ly}" r="14" fill="#C0C0C0" stroke="#666" stroke-width="2"/><circle cx="{lx}" cy="{ly}" r="5" fill="#555"/>'
    b += f'<rect x="895" y="910" width="130" height="120" rx="8" fill="none" stroke="{C["hl"]}" stroke-width="4" stroke-dasharray="10,6"/>'
    b += wire([(1025, 970), (1110, 970)], C["orange"], 5)
    b += text(1120, 950, "Power-button legs (solder joints", 16, "bold", fill=C["hl"])
    b += text(1120, 972, "behind the green-lit button).", 16, "bold", fill=C["hl"])
    b += text(1120, 996, "There may be extra legs for the", 15, fill="#fff")
    b += text(1120, 1018, "button's LED - use the meter test.", 15, fill="#fff")
    return svg(W, H, b, "BC-250  -  where to connect")

# ---------------------------------------------------------------------------
# Figure 5: ATX 24-pin plug
# ---------------------------------------------------------------------------
def fig_atx():
    W, H = 1300, 620
    b = ""
    px, py, p = 180, 230, 78
    b += f'<rect x="{px-30}" y="{py-40}" width="{p*12+20}" height="{p*2+30}" rx="12" fill="#ECEFF1" stroke="#333" stroke-width="3"/>'
    b += f'<rect x="{px+p*5.5-60}" y="{py-80}" width="140" height="42" rx="6" fill="#B0BEC5" stroke="#333" stroke-width="2"/>' + text(px + p*5.5 + 10, py - 52, "CLIP", 18, "bold", "middle")
    cols = {9: (C["purple"], "+5VSB"), 15: (C["black"], "COM"), 16: (C["green"], "PS_ON"), 17: (C["black"], "COM")}
    for i in range(12):
        for row in range(2):
            num = (13 + i) if row == 0 else (1 + i)
            x = px + i * p
            y = py + row * p
            col, lab = cols.get(num, ("#9E9E9E", ""))
            hl = num in cols
            b += f'<rect x="{x-26}" y="{y-26}" width="52" height="52" rx="8" fill="{col if hl else "#CFD8DC"}" stroke="#333" stroke-width="{4 if hl else 1}"/>'
            b += text(x, y + 7, str(num), 18, "bold", "middle", "#fff" if hl else "#333")
            if hl:
                b += text(x, (y - 38) if row == 0 else (y + 50), lab, 16, "bold", "middle", col)
    b += text(W/2, 450, "Pin numbers for reference only - the view may be mirrored on yours. Clip-side row = pins 13-24.", 18, "bold", "middle")
    b += text(W/2, 480, "Easiest: go by wire colour - the single PURPLE wire (+5VSB) and the single GREEN wire (PS_ON).", 17, anchor="middle")
    b += text(W/2, 510, "Black wires next to the green one (pins 15 / 17) are ground.", 17, anchor="middle")
    b += text(W/2, 548, "Use a 24-pin ATX breakout / female socket so you don't cut the power supply's cable.", 17, "bold", "middle", C["red"])
    return svg(W, H, b, "ATX 24-pin plug from your flex ATX power supply")

# ---------------------------------------------------------------------------
# Figure 1: overview
# ---------------------------------------------------------------------------
def fig_overview():
    W, H = 1600, 760
    b = ""
    b += box(60, 120, 360, 200, "Flex ATX power supply", ["24-pin plug: +5VSB, GND, PS_ON", "PCIe 8-pin -> BC-250 J1000", "(stays plugged in at the wall)"], C["black"])
    b += box(620, 120, 360, 200, "Wake board", ["Pico W  or  Pico 2 W", "Q1 + Q2 MOSFETs, D1, R1-R3", "listens for the controller"], C["pico"])
    b += box(1180, 120, 360, 200, "AMD BC-250", ["power-button pad + ground", "TPMS1 pin 9 'PC on' 3.3 V", "AUTO_PWRON1 on pins 2-3"], C["orange"])
    b += box(620, 480, 360, 170, "Xbox Series X|S controller", ["already paired to the BC-250", "sends a Bluetooth LE 'hello'", "when you switch it on"], C["blue"])
    b += wire([(420, 180), (620, 180)], C["purple"]) + text(520, 168, "+5VSB  (power)", 15, "bold", "middle", C["purple"])
    b += wire([(420, 230), (620, 230)], C["black"]) + text(520, 220, "GND", 15, "bold", "middle")
    b += wire([(620, 280), (420, 280)], C["green"], 6, "14,8") + text(520, 302, "PS_ON  (Option B only)", 15, "bold", "middle", C["green"])
    b += wire([(980, 180), (1180, 180)], C["orange"]) + text(1080, 168, "presses power button", 15, "bold", "middle", C["orange"])
    b += wire([(980, 230), (1180, 230)], C["black"]) + text(1080, 220, "GND", 15, "bold", "middle")
    b += wire([(1180, 280), (980, 280)], C["yellow"]) + text(1080, 302, "'PC is on' signal", 15, "bold", "middle", C["yellow"])
    b += wire([(800, 480), (800, 320)], C["blue"], 4, "6,8") + text(815, 410, "Bluetooth LE (listen only)", 16, "bold", fill=C["blue"])
    b += wire([(980, 565), (1360, 565), (1360, 320)], C["blue"], 4, "6,8") + text(1375, 450, "normal connection", 16, "bold", fill=C["blue"])
    b += text(1375, 472, "to the BC-250", 16, "bold", fill=C["blue"])
    b += text(60, 400, "Sequence when you switch the controller on:", 18, "bold")
    for i, l in enumerate(["1. Pico hears a SAVED controller", "2. PS_ON on (Option B), wait 1 s", "3. 'press' power button 0.5 s", "4. wait for the 'PC is on' signal", "5. controller connects to BC-250"]):
        b += text(60, 432 + i*28, l, 17)
    return svg(W, H, b, "How it works  -  overview")

# ---------------------------------------------------------------------------
# Figure 6: part orientation close-up
# ---------------------------------------------------------------------------
def fig_parts():
    W, H = 1300, 520
    b = ""
    s, p = sot23(250, 270, "Q", "BSS138LT1G")
    b += s
    b += text(250, 420, "Printed marking on top is usually 'J1' + date code.", 15, anchor="middle", italic=True)
    b += text(250, 445, "1 pin on one side (3 = Drain), 2 pins on the other.", 15, anchor="middle")
    b += diode(800, 260, "D1", "1N5819WS")
    b += text(800, 340, "SOD-323: the painted BAND end is the cathode.", 15, anchor="middle")
    b += text(800, 365, "Band end points TOWARD the Pico (VSYS).", 15, "bold", "middle", C["red"])
    b += text(W/2, 470, "Tip: tack SOT-23 parts onto a SOT-23-to-DIP adapter or solder thin wires to them directly.", 16, anchor="middle", italic=True, fill="#333")
    return svg(W, H, b, "Part orientation  (surface-mount parts)")

save("Fig1_Overview", fig_overview())
save("Fig2_Wiring", fig_wiring())
save("Fig3_PicoW_Pins", fig_pico())
save("Fig4_BC250_Connection_Points", fig_bc250())
save("Fig5_ATX_24pin", fig_atx())
save("Fig6_Part_Orientation", fig_parts())
print("done")
