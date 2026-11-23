import os
from render_lib import *
from board_lib import *
OUT = os.path.dirname(os.path.abspath(__file__))

ORANGE, GREEN, YELLOW, BLACK, RED, PURPLE, BLUE, BLUE2, CYAN = "#EF6C00", "#2E7D32", "#F9A825", "#1b1b1b", "#D32F2F", "#7B1FA2", "#1565C0", "#5C6BC0", "#00838F"

def build(option):
    B = option == "B"
    W, H = 1820, 1200
    b = Board(330, 150, 34, 26, 32)
    s = b.draw()
    # ---- GND bus (black) : J1 GND -> left edge -> row 19 -> col 22 -> Pico pin 8
    s += b.wire([(1, 3), (1, 19), (22, 19), (22, 10), (23, 10)], BLACK)
    s += b.wire([(4, 16), (4, 19)], BLACK) + b.wire([(7, 14), (6, 14), (6, 19)], BLACK)          # R1, Q1 S
    s += b.wire([(8, 19), (8, 24)], BLACK)                                                       # BC-250 GND pin
    if B:
        s += b.wire([(11, 16), (11, 19)], BLACK) + b.wire([(14, 14), (13, 14), (13, 19)], BLACK)  # R2, Q2 S
        s += b.wire([(20, 12), (21, 12), (21, 19)], BLACK)                                         # SW1
    # ---- power: J1 +5VSB -> D1 -> VSYS
    s += b.wire([(1, 2), (4, 2)], PURPLE)
    s += b.wire([(7, 2), (7, 0), (31, 0), (31, 4), (30, 4)], RED)
    # ---- signals from the Pico
    s += b.wire([(23, 6), (7, 6), (7, 13)], BLUE)                     # GP2 -> Q1 gate
    s += b.wire([(7, 13), (6, 13), (4, 13)], BLUE)                    # Q1 gate -> R1
    if B:
        s += b.wire([(23, 7), (14, 7), (14, 13)], BLUE2)              # GP3 -> Q2 gate
        s += b.wire([(14, 13), (13, 13), (11, 13)], BLUE2)            # Q2 gate -> R2
        s += b.wire([(23, 9), (20, 9), (20, 10)], CYAN)               # GP5 -> SW1
    s += b.wire([(23, 8), (19, 8), (19, 13)], YELLOW)                 # GP4 -> R3
    # ---- outputs to J2
    s += b.wire([(7, 15), (7, 24)], ORANGE)                           # Q1 drain -> PWR BTN
    if B:
        s += b.wire([(14, 15), (14, 22), (9, 22), (9, 24)], GREEN)    # Q2 drain -> PS_ON
        s += b.wire([(19, 16), (19, 23), (10, 23), (10, 24)], YELLOW) # R3 -> PC ON
        j2 = [(7, 24), (8, 24), (9, 24), (10, 24)]
    else:
        s += b.wire([(19, 16), (19, 23), (9, 23), (9, 24)], YELLOW)
        j2 = [(7, 24), (8, 24), (9, 24)]
    # ---- parts
    s += chip_adapter(b, 4, 2, 7, 2, "D1  1N5819WS", "diode")
    s += sot23_adapter(b, 7, 13, "Q1")
    s += chip_adapter(b, 4, 13, 4, 16, "R1", "res")
    if B:
        s += sot23_adapter(b, 14, 13, "Q2")
        s += chip_adapter(b, 11, 13, 11, 16, "R2", "res")
        s += tact(b, 20, 10, 12, "SW1")
    s += chip_adapter(b, 19, 13, 19, 16, "R3", "res")
    s += header(b, [(1, 2), (1, 3)]) + header(b, j2)
    s += pico_w(b, 23, 3)
    # board text
    x, y = b.xy(2, 2); s += text(x + 4, y - 22, "J1", 15, "bold", "start", "#1a237e")
    x, y = b.xy(7, 24); s += text(x - 26, y + 6, "J2", 15, "bold", "end", "#1a237e")
    x, y = b.xy(1, 18); s += text(x + 20, y + 4, "GND", 14, "bold", "start", "#2b2b2b")
    # ---- flying leads + labels
    xa, ya = b.xy(1, 2); xb, yb = b.xy(1, 3)
    s += wire_path(f"M {xa} {ya} C {xa-80} {ya}, {xa-120} {ya-40}, {xa-230} {ya-40}", PURPLE, 10)
    s += wire_path(f"M {xb} {yb} C {xb-80} {yb}, {xb-120} {yb+50}, {xb-230} {yb+50}", BLACK, 10)
    s += label(15, ya - 120, ["J1 pin 1  ->  ATX PURPLE", "+5VSB (pin 9 of 24-pin)"], "#CE93D8", w=270, size=14, title_size=16)
    s += label(15, yb + 70, ["J1 pin 2  ->  ATX BLACK", "ground (pin 15 or 17)"], "#FFE000", w=270, size=14, title_size=16)
    outs = [("PWR BTN", ORANGE, ["J2-1  ->  BC-250", "power-button pad", "(orange wire)"], "#FFB74D"),
            ("BC GND", BLACK, ["J2-2  ->  BC-250", "ground pad", "(black wire)"], "#FFE000")]
    if B: outs.append(("PS_ON", GREEN, ["J2-3  ->  ATX GREEN", "PS_ON (pin 16)", "(green wire)"], "#69F0AE"))
    outs.append(("PC ON", YELLOW, [("J2-4" if B else "J2-3") + "  ->  BC-250", "TPMS1 pin 9 ('3V')", "(yellow Dupont)"], "#FFF176"))
    for i, ((c, r), (nm, col, lines, lc)) in enumerate(zip(j2, outs)):
        x, y = b.xy(c, r)
        tx = 360 + i * 270
        s += wire_path(f"M {x} {y} C {x} {y+60}, {tx+110} {y+40}, {tx+110} {y+95}", col, 10)
        s += label(tx, y + 95, lines, lc, w=250, size=14, title_size=16)
    # ---- legend
    leg = ["Q1  BSS138 on SOT-23 adapter", "    pins 1=Gate 2=Source 3=Drain", "    'presses' the power button",
           "R1  10k  Q1 gate -> GND"]
    if B: leg += ["Q2  BSS138 (same adapter)", "    switches the PSU on (PS_ON)", "R2  10k  Q2 gate -> GND"]
    leg += ["R3  1k   TPMS1 pin 9 -> GP4", "D1  1N5819WS, band toward", "    the Pico (VSYS side)"]
    if B: leg += ["SW1 push button (manual on/off)"]
    leg += ["", "Pico pins used:", "  4 GP2 -> Q1 gate (blue)"]
    if B: leg += ["  5 GP3 -> Q2 gate (light blue)"]
    leg += ["  6 GP4 <- R3 (yellow)"]
    if B: leg += ["  7 GP5 -> SW1 (teal)"]
    leg += ["  8 GND (black)", " 39 VSYS <- D1 (red)"]
    s += label(1460, 150, [f"OPTION {option}  PARTS"] + leg, "#80DEEA", w=345, size=14, title_size=18)
    s += title_bar(W, f"OPTION {option}  -  wake board build (top view, Pico plugged in)",
                   "Every wire, part and pin exactly as built.  Blue adapter boards hold the tiny SMD parts.  Pico pin numbers are printed beside its pins.")
    s += footer(W, H, "Render for illustration - hole positions are a suggested layout; any layout with the same connections works.")
    return svg(W, H, s)

save(OUT, "S_A06_Build_Board_OptionA", build("A"))
save(OUT, "S_B06_Build_Board_OptionB", build("B"))
print("ok")
