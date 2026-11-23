import os, math, random
from render_lib import *
OUT = os.path.dirname(os.path.abspath(__file__))

# =====================================================================================
# R1: BC-250 BOTTOM side, rear corner - power-button pad + ground pad
# =====================================================================================
def bottom_corner(mode):
    W, H = 1600, 1120
    b = ""
    # board (rear edge at y=880)
    b += pcb(-30, 100, 1470, 780, rx=26, seed=11)
    # backplate (brushed aluminium) upper-left
    b += ('<g filter="url(#shadow)"><path d="M -30 100 L 1060 100 L 1060 330 Q 1060 360 1030 360 L 330 360 L 300 395 L -30 395 Z" '
          'fill="url(#metal)" filter="url(#brushed)" stroke="#7f878c" stroke-width="2"/></g>')
    b += '<circle cx="520" cy="190" r="34" fill="#9aa1a6" stroke="#6d7479" stroke-width="3"/><circle cx="520" cy="190" r="18" fill="#3a3f42"/>'
    b += text(220, 300, "aluminium back plate", 20, "bold", "middle", "#555c61")
    # silkscreen dashed edge line + some traces
    b += '<line x1="0" y1="858" x2="1400" y2="858" stroke="#e9f1ea" stroke-width="3" stroke-dasharray="6,6" opacity="0.85"/>'
    b += trace([(620, 520), (760, 520), (820, 470), (950, 470)], 3) + trace([(150, 560), (300, 560), (360, 620)], 3)
    # connectors protruding past rear edge (seen from below)
    # USB-A at far left
    b += '<g filter="url(#shadow)"><rect x="-10" y="868" width="170" height="150" rx="6" fill="url(#nickel)"/><rect x="18" y="900" width="114" height="70" rx="4" fill="#1b1b1b"/><rect x="30" y="930" width="90" height="18" fill="#1e5bd8"/></g>'
    # DisplayPort / HDMI shell
    b += ('<g filter="url(#shadow)"><path d="M 225 868 L 470 868 L 470 990 L 450 1012 L 245 1012 L 225 990 Z" fill="url(#nickel)"/>'
          '<path d="M 250 895 L 445 895 L 445 970 L 430 986 L 265 986 L 250 970 Z" fill="#161616"/><rect x="290" y="925" width="115" height="16" fill="#333"/></g>')
    # stacked dual USB
    b += ('<g filter="url(#shadow)"><rect x="545" y="866" width="200" height="200" rx="6" fill="url(#nickel)"/>'
          '<rect x="568" y="890" width="154" height="62" rx="3" fill="#161616"/><rect x="568" y="975" width="154" height="62" rx="3" fill="#161616"/>'
          '<rect x="590" y="912" width="110" height="16" fill="#2a2a2a"/><rect x="590" y="997" width="110" height="16" fill="#2a2a2a"/></g>')
    # two clear light-pipe buttons at the corner
    for i, cx in enumerate((835, 950)):
        b += (f'<g filter="url(#shadow)"><rect x="{cx-46}" y="866" width="92" height="44" rx="6" fill="#d9dfe2" stroke="#8a969c"/>'
              f'<rect x="{cx-34}" y="906" width="68" height="92" rx="14" fill="url(#lightpipe)" stroke="#9fb0b8" stroke-width="2"/>'
              f'<ellipse cx="{cx}" cy="996" rx="34" ry="12" fill="#eef5f8" stroke="#a5b6be" stroke-width="2"/></g>')
    b += text(892, 1050, "two clear light-pipe buttons", 17, "bold", "middle", "#2b2b2b")
    # corner mounting hole (copper ring)
    b += mount_hole(1270, 560, 64)
    # through-hole cluster (button switch legs etc.)
    PB = (930, 610)     # power-button pin (from reference photo)
    XP = (1030, 690)    # round pad with an "X" mark
    GND = (470, 815)    # ground pad used in the reference build
    for (x, y, r) in [(1010, 470, 17), (880, 470, 9), (955, 525, 9), (1000, 575, 9), (1075, 560, 9), (860, 655, 9),
                      (890, 730, 10), (1170, 650, 15), (770, 560, 19), (690, 700, 19), (620, 470, 12), (560, 520, 12),
                      (680, 455, 12), (500, 470, 11), (430, 520, 12), (360, 470, 11), (300, 520, 11), (720, 520, 16),
                      (400, 720, 17), (215, 600, 16), (120, 680, 13), (60, 600, 13), (980, 790, 8)]:
        b += solder_joint(x, y, r)
    b += square_joint(800, 460, 12)
    b += solder_joint(*PB, 10)
    # X pad
    b += f'<circle cx="{XP[0]}" cy="{XP[1]}" r="26" fill="#3d2a1c" filter="url(#softshadow)"/><circle cx="{XP[0]}" cy="{XP[1]}" r="21" fill="#6e4a30"/>'
    b += f'<path d="M {XP[0]-9} {XP[1]-9} L {XP[0]+9} {XP[1]+9} M {XP[0]+9} {XP[1]-9} L {XP[0]-9} {XP[1]+9}" stroke="#efe6da" stroke-width="3"/>'
    # ground pad (large shield leg near edge, left of the stacked USB)
    b += solder_joint(GND[0], GND[1], 16)
    b += f'<rect x="{GND[0]-10}" y="{GND[1]-22}" width="20" height="44" rx="4" fill="url(#solder)" opacity="0.9"/>'

    if mode == "solder":
        b += wire_path(f"M {PB[0]} {PB[1]} C {PB[0]-60} {PB[1]-120}, 700 260, 640 40", "#EF6C00", 11)
        b += wire_path(f"M {GND[0]} {GND[1]} C {GND[0]-40} {GND[1]-200}, 420 300, 380 40", "#1b1b1b", 11)
        b += solder_joint(PB[0], PB[1], 12, False) + solder_joint(GND[0], GND[1], 15, False)
        b += callout_ring(*PB, 30) + callout_ring(*GND, 34)
        b += label(1100, 250, ["POWER-BUTTON PAD", "orange wire  ->  Q1 Drain", "thin pin just up-left of the", "round copper 'X' pad"], "#FFB300", w=360, anchor_pt=(PB[0] + 24, PB[1] - 20))
        b += label(30, 560, ["GROUND PAD", "black wire  ->  shared GND", "big leg at the board edge,", "just left of the stacked USB"], "#FFE000", w=350, anchor_pt=(GND[0] - 30, GND[1] - 10))
        b += label(1130, 780, ["LANDMARKS", "copper-ring corner hole", "round copper 'X' pad", "clear light-pipe buttons"], "#80DEEA", w=330)
        b += title_bar(W, "BC-250  BOTTOM side  -  power-button pad + ground pad",
                       "Rear corner next to the clear light-pipe buttons.  Unplug the PSU from the wall before soldering.")
        b += footer(W, H, "Render based on reference photos (tfabris/BC-250).  Positions approximate - confirm the pad with the meter check first.")
    else:
        b += probe(PB[0] + 3, PB[1] - 3, "#D32F2F", -40, 280)
        b += probe(GND[0] - 3, GND[1] - 3, "#1b1b1b", -140, 260)
        b += callout_ring(*PB, 30) + callout_ring(*GND, 34)
        b += label(1100, 230, ["RED probe here", "PC OFF, PSU plugged in:", "reads some voltage at rest,", "drops to 0 V while a helper", "HOLDS the power button"], "#FF5252", w=360, anchor_pt=(PB[0] + 26, PB[1] - 26))
        b += label(30, 560, ["BLACK probe here", "ground pad"], "#FFE000", w=300, anchor_pt=(GND[0] - 30, GND[1] - 10))
        b += label(1130, 800, ["Meter: DC volts (20 V range)", "Wrong pin? Try the other thin", "pins next to it - only the right", "one drops to 0 V when pressed."], "#80DEEA", w=380, size=15, title_size=18)
        b += title_bar(W, "BC-250  BOTTOM side  -  meter check for the power-button pad",
                       "Do this BEFORE soldering.  Never let a probe touch two pins at once.")
        b += footer(W, H, "The exact idle voltage on your board is not verified - the drop to 0 V while the button is held is what identifies the pad.")
    return svg(W, H, b)

# =====================================================================================
# R2: BC-250 TOP side - TPMS1 header, pin 9 ("3V")
# =====================================================================================
def tpms1(mode="check"):
    W, H = 1600, 1120
    b = pcb(-30, 100, 1660, 830, rx=26, seed=5)
    b += trace([(560, 560), (700, 560), (760, 500), (1000, 500)], 3) + trace([(1150, 600), (1250, 520)], 3)
    # Ethernet jack (metal shell) upper-left
    b += ('<g filter="url(#shadow)"><rect x="40" y="150" width="400" height="390" rx="10" fill="url(#metal)" filter="url(#brushed)" stroke="#80888d" stroke-width="3"/>'
          '<rect x="80" y="190" width="200" height="140" rx="8" fill="#efe6c3" stroke="#bfb38a"/>'
          '<rect x="60" y="450" width="340" height="40" rx="6" fill="#9aa2a7"/></g>')
    b += text(240, 520, "Ethernet jack", 18, "bold", "middle", "#3d4246")
    # small smd parts above header
    r = random.Random(4)
    for i in range(18):
        b += smd(560 + (i % 9) * 62 + r.uniform(-6, 6), 420 + (i // 9) * 46 + r.uniform(-4, 4), 24, 13, "#8a6a45" if i % 3 else "#3b3b3b", 90 if i % 4 == 0 else 0)
    b += ic(760, 300, 110, 80, "", 7)
    b += silk(560, 190, "U30", 18)
    # BIOS chip with sticker
    b += ic(1360, 560, 170, 100, "", 4)
    b += '<rect x="1300" y="525" width="120" height="70" rx="4" fill="#fbfbf6" filter="url(#softshadow)"/>' + text(1360, 572, "P2.00", 26, "bold", "middle", "#111", family="DejaVu Serif")
    b += silk(1290, 660, "BIOS_A1", 18)
    # H9 mounting hole lower-left
    b += mount_hole(250, 800, 74) + silk(345, 808, "H9", 24)
    # board edge stripe at bottom
    b += '<line x1="0" y1="905" x2="1600" y2="905" stroke="#e9f1ea" stroke-width="3" stroke-dasharray="6,6" opacity="0.8"/>'
    # TPMS1 header 2x9, front row (next to label) = odd pins 1..17
    x0, p = 560, 70
    yb, yf = 650, 720   # back row, front row centres
    b += f'<rect x="{x0-50}" y="{yb-50}" width="{p*8+100}" height="{yf-yb+100}" fill="none" stroke="#eef3ee" stroke-width="3"/>'
    b += f'<g filter="url(#shadow)"><rect x="{x0-36}" y="{yb-36}" width="{p*8+72}" height="{yf-yb+72}" rx="4" fill="url(#plastic)"/></g>'
    for col in range(9):
        for row, yy in (("b", yb), ("f", yf)):
            x = x0 + col * p
            b += f'<rect x="{x-31}" y="{yy-31}" width="62" height="62" fill="none" stroke="#000" stroke-opacity="0.5"/>'
            if row == "f" and col == 6:   # pin 13 missing
                b += f'<path d="M {x} {yy-9} L {x+9} {yy} L {x} {yy+9} L {x-9} {yy} Z" fill="#050505" stroke="#444" stroke-width="2"/>'
                continue
            b += f'<rect x="{x-11}" y="{yy-11}" width="22" height="22" fill="url(#gold)" stroke="#7a5a14" stroke-width="1.5"/>'
            b += f'<rect x="{x-7}" y="{yy-7}" width="8" height="8" fill="#fffbe0" opacity="0.8"/>'
    b += silk(x0 - 20, yf + 100, "TPMS1", 30)
    b += f'<polygon points="{x0-60},{yf+90} {x0-38},{yf+78} {x0-38},{yf+102}" fill="#eef3ee"/>'
    pin9 = (x0 + 4 * p, yf)
    gap = (x0 + 6 * p, yf)
    b += callout_ring(*pin9, 30)
    b += f'<circle cx="{gap[0]}" cy="{gap[1]}" r="26" fill="none" stroke="#FFAB40" stroke-width="4" stroke-dasharray="7,5"/>'
    b += f'<circle cx="{x0+5*p}" cy="{yf}" r="22" fill="none" stroke="#ffffff" stroke-width="3" stroke-dasharray="4,5"/>'
    if mode == "check":
        b += probe(pin9[0] + 3, pin9[1] + 4, "#D32F2F", 55, 300)
    else:
        b += (f'<g filter="url(#shadow)"><rect x="{pin9[0]-18}" y="{pin9[1]-34}" width="36" height="96" rx="4" fill="#111"/>'
              f'<rect x="{pin9[0]-13}" y="{pin9[1]-29}" width="26" height="26" fill="#2a2a2a"/></g>')
        b += wire_path(f"M {pin9[0]} {pin9[1]+60} C {pin9[0]} {pin9[1]+150}, {pin9[0]+120} {pin9[1]+150}, {pin9[0]+180} {pin9[1]+330}", "#F9A825", 13)
    b += label(1020, 230, ["PIN 9  =  '3V'", "-> R3 -> Pico pin 6 (GP4)", "row nearest the 'TPMS1' label,", "5th pin from the triangle end"], "#FFE000", w=400, anchor_pt=(pin9[0] + 22, pin9[1] - 24))
    b += label(1150, 760, ["MISSING PIN (pin 13)", "your landmark: from the gap", "skip ONE pin toward the", "triangle - the next is pin 9"], "#FFAB40", w=380, anchor_pt=(gap[0] + 26, gap[1] + 10))
    if mode == "connect":
        b += label(40, 570, ["CONNECT", "push the yellow Dupont lead", "onto pin 9 ONLY.  The other", "end goes to the wake board."], "#FFF176", w=360, size=16, title_size=18)
    else:
      b += label(40, 570, ["METER CHECK (black probe on", "the PSU's black wire / GND):", "PC ON  = about 3.3 V", "PC OFF = 0 V"], "#80DEEA", w=360, size=16, title_size=17)
    b += title_bar(W, "BC-250  TOP side  -  TPMS1 header, pin 9 ('3V' = PC is on)" + ("  -  CONNECT" if mode == "connect" else "  -  METER CHECK"),
                   "Next to the Ethernet jack and the corner mounting hole 'H9'.  A Dupont jumper wire can push straight onto pin 9.")
    b += footer(W, H, "Render based on reference photos (tfabris/BC-250).  If pin 9 reads 3.3 V while the PC is OFF, it is the wrong pin (pin 15 is always 3.3 V).")
    return svg(W, H, b)

# =====================================================================================
# R3: BC-250 TOP side - AUTO_PWRON1 jumper (text upright; board edge at the top)
# =====================================================================================
def auto_pwron():
    W, H = 1600, 1000
    b = pcb(-30, 160, 1660, 900, rx=0, seed=9)
    b += '<line x1="0" y1="190" x2="1600" y2="190" stroke="#e9f1ea" stroke-width="3" stroke-dasharray="6,6" opacity="0.8"/>'
    b += text(800, 150, "BOARD EDGE  (this side)", 18, "bold", "middle", "#4a3a26")
    # CR2032 holder at right
    b += ('<g filter="url(#shadow)"><circle cx="1400" cy="560" r="230" fill="#151515"/>'
          '<circle cx="1400" cy="560" r="195" fill="url(#metal)" filter="url(#brushed)" stroke="#6f777c" stroke-width="3"/></g>')
    b += text(1400, 545, "CR2032", 34, "bold", "middle", "#4b5156") + text(1400, 590, "+", 40, "bold", "middle", "#4b5156")
    b += text(1400, 640, "coin battery", 20, "normal", "middle", "#4b5156")
    def header3(x0, y, p, jumper_cols, name, tri_left=True, hl=False):
        s = f'<g filter="url(#shadow)"><rect x="{x0-40}" y="{y-40}" width="{2*p+80}" height="80" rx="4" fill="url(#plastic)"/></g>'
        for i in range(3):
            x = x0 + i * p
            s += f'<rect x="{x-11}" y="{y-11}" width="22" height="22" fill="url(#gold)" stroke="#7a5a14"/>'
        if jumper_cols:
            a, c = jumper_cols
            s += (f'<g filter="url(#shadow)"><rect x="{x0+a*p-40}" y="{y-52}" width="{(c-a)*p+80}" height="104" rx="8" fill="url(#nylonblack)" stroke="#000" stroke-width="2"/>'
                  f'<rect x="{x0+a*p-28}" y="{y-40}" width="{(c-a)*p+56}" height="20" rx="4" fill="#4a4a4a" opacity="0.6"/></g>')
        s += f'<rect x="{x0-52}" y="{y-52}" width="{2*p+104}" height="104" fill="none" stroke="#eef3ee" stroke-width="3"/>'
        s += silk(x0 + p, y + 98, name, 28, "middle")
        if tri_left:
            s += f'<polygon points="{x0-82},{y-14} {x0-58},{y} {x0-82},{y+14}" fill="#eef3ee"/>'
        return s
    p = 78
    # AUTO_PWRON1 (pin 1 at the triangle, left end) - jumper on pins 2-3 (middle + right)
    ax = 330
    b += header3(ax, 520, p, (1, 2), "AUTO_PWRON1", True)
    for i, n in enumerate(("1", "2", "3")):
        b += text(ax + i * p, 430, n, 24, "bold", "middle", "#FFE000")
    # PCVP15/16 small parts + labels
    b += smd(640, 470, 26, 40, "#8a6a45") + smd(690, 470, 26, 40, "#8a6a45")
    b += silk(625, 545, "PCVP15", 16, rot=-90) + silk(675, 545, "PCVP16", 16, rot=-90)
    # CLRCMOS1 (leave alone)
    cx = 840
    b += header3(cx, 520, p, (0, 1), "CLRCMOS1", True)
    b += label(760, 690, ["CLRCMOS1 - leave it alone", "(this one clears the BIOS)"], "#B0BEC5", w=330, size=15, title_size=17)
    b += (f'<rect x="{ax+p-54}" y="{520-66}" width="{p+108}" height="132" rx="14" fill="none" stroke="#000" stroke-opacity="0.55" stroke-width="9"/>'
          f'<rect x="{ax+p-54}" y="{520-66}" width="{p+108}" height="132" rx="14" fill="none" stroke="#FFE000" stroke-width="5" filter="url(#glow)"/>')
    b += label(20, 690, ["JUMPER ON PINS 2-3", "the two pins FARTHEST from", "the triangle  =  'wait for", "power button' mode"], "#FFE000", w=380, anchor_pt=(ax + p - 54, 540))
    b += label(60, 230, ["Pin 1 = the end with the", "small triangle printed on the board"], "#80DEEA", w=420, size=16, title_size=18,
               anchor_pt=(ax - 70, 505))
    b += title_bar(W, "BC-250  TOP side  -  set the AUTO_PWRON1 jumper to pins 2-3",
                   "Between the coin battery and the board edge.  PSU unplugged from the wall when moving the jumper.")
    b += footer(W, H, "Drawn with the board text upright.  In the reference photo the jumper is on the 2 pins away from the triangle = pins 2-3.")
    return svg(W, H, b)

save(OUT, "R1_BC250_Bottom_PowerButton_Ground", bottom_corner("solder"))
save(OUT, "R2_BC250_Bottom_PowerButton_MeterCheck", bottom_corner("check"))
save(OUT, "R3_BC250_Top_TPMS1_Pin9", tpms1())
save(OUT, "S_10_TPMS1_Connect", tpms1("connect"))
save(OUT, "R4_BC250_Top_AUTO_PWRON1", auto_pwron())
print("ok")
