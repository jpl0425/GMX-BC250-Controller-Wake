"""GMX BC-250 Controller Wake - install guide Rev 1.2 (two fully separate install options)."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
                                KeepTogether, Flowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from PIL import Image as PILImage

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DVB"); addMapping("DV", 0, 1, "DV"); addMapping("DV", 1, 1, "DVB")

HERE = os.path.dirname(os.path.abspath(__file__))
REN = os.path.join(HERE, "..", "renders")
OUT = os.path.join(HERE, "GMX-BC250-Controller-Wake_Rev1.2_Guide.pdf")

ss = getSampleStyleSheet()
B = ParagraphStyle("B", parent=ss["Normal"], fontName="DV", fontSize=11, leading=15, spaceAfter=4)
SMALL = ParagraphStyle("S", parent=B, fontSize=9.5, leading=12.5)
H1 = ParagraphStyle("H1", parent=B, fontName="DVB", fontSize=20, leading=25, spaceAfter=6, textColor=colors.HexColor("#1F4E3D"))
H2 = ParagraphStyle("H2", parent=B, fontName="DVB", fontSize=14.5, leading=19, spaceBefore=2, spaceAfter=5, textColor=colors.HexColor("#263238"))
TITLE = ParagraphStyle("T", parent=B, fontName="DVB", fontSize=26, leading=32, alignment=1, spaceAfter=4)
SUB = ParagraphStyle("Sub", parent=B, fontSize=12.5, alignment=1, textColor=colors.HexColor("#455A64"))
CODE = ParagraphStyle("C", parent=B, fontName="DVM", fontSize=9.3, leading=13, backColor=colors.HexColor("#ECEFF1"),
                      borderPadding=6, leftIndent=6, rightIndent=6, spaceBefore=3, spaceAfter=6)
CELL = ParagraphStyle("cell", parent=B, fontSize=10, leading=13, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="DVB")
STEP = ParagraphStyle("step", parent=B, leftIndent=18, firstLineIndent=-18, spaceAfter=3)
W = letter[0] - 1.2 * inch

PAGES = {}

class Anchor(Flowable):
    def __init__(self, name): super().__init__(); self.name = name; self.width = self.height = 0
    def draw(self): PAGES[self.name] = self.canv.getPageNumber()

def pg(name): return str(PAGES.get(name, "?"))
def P(t, s=B): return Paragraph(t, s)
def steps(items): return [P(f"<b>{i+1}.</b>&nbsp;&nbsp;{t}", STEP) for i, t in enumerate(items)]
def img(name, maxh=5.6 * inch):
    path = os.path.join(REN, name)
    w, h = PILImage.open(path).size
    sc = min(W / w, maxh / h)
    return Image(path, width=w * sc, height=h * sc)
def box(t, bg="#FFF8E1", edge="#F9A825"):
    tb = Table([[P(t, CELL)]], colWidths=[W])
    tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor(edge)),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return tb
def warn(t): return box(t, "#FFEBEE", "#C62828")
def info(t): return box(t, "#E3F2FD", "#1565C0")
def table(rows, widths):
    data = [[P(str(c), CELLB if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CFE8DA")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
    return t

def step_page(tag, title, lines, picture, maxh=5.6 * inch, extra=None):
    f = [P(f"{tag}.&nbsp;&nbsp;{title}", H2)] + steps(lines)
    if extra: f += extra
    f += [Spacer(1, 4), img(picture, maxh)]
    return [KeepTogether(f), PageBreak()]

# ============================================================ content
def section(opt):
    A = opt == "A"
    o = opt
    name = "Option A  -  power supply always on" if A else "Option B  -  Pico switches the power supply"
    s = [Anchor(o), P(name, H1)]
    if A:
        s.append(P("In this option the ATX power supply stays switched on all the time (its green PS_ON wire is linked to a black "
                   "ground wire). The wake board only presses the BC-250's power button. The BC-250's own rear power button keeps working."))
    else:
        s.append(P("In this option the power supply is completely off while the PC is off. When the controller is switched on, the "
                   "wake board first switches the supply on (PS_ON), then presses the BC-250's power button. After the PC shuts down, "
                   "the board switches the supply off again."))
        s.append(warn("<b>Option B behaviour to know:</b> while the supply is off, the BC-250's own rear power button does nothing. "
                      "To start the PC without the controller, use the push button SW1 on the wake board (short press). "
                      "Don't unplug or re-flash the Pico while the PC is running - the supply would switch off."))
    s.append(Spacer(1, 6))
    s.append(P(f"Steps in this section: {o}1 to {o}14 - one step per page, each with a picture.", B))
    s.append(PageBreak())

    # ---- step 1 parts
    rows = [["Ref", "Part", "Qty", "What it does"],
            ["-", "Raspberry Pi Pico W  or  Pico 2 W", "1", "Runs the wake firmware"],
            ["Q1", "BSS138LT1G N-MOSFET, SOT-23 (LCSC C82045) on a SOT-23-to-DIP adapter", "1", "Presses the BC-250 power button"],
            ["R1", "10k resistor, 0603 (RC0603FR-0710KL, LCSC C98220) on a 2-pin SMD adapter", "1", "Keeps Q1 off while the Pico starts"]]
    if not A:
        rows += [["Q2", "BSS138LT1G on a SOT-23-to-DIP adapter", "1", "Switches the power supply on (PS_ON)"],
                 ["R2", "10k resistor, 0603 on a 2-pin SMD adapter", "1", "Keeps Q2 off while the Pico starts"]]
    rows += [["R3", "1k resistor, 0603 (RC0603FR-071KL, LCSC C22548) on a 2-pin SMD adapter", "1", "Protects the Pico input (PC-on signal)"],
             ["D1", "1N5819WS Schottky diode, SOD-323 (LCSC C191023) on a 2-pin SMD adapter", "1", "Feeds +5VSB to the Pico (VSYS)"]]
    if not A:
        rows += [["SW1", "Momentary push button (2-leg)", "1", "Manual PC on / off"]]
    rows += [["J1", "1x2 male pin header", "1", "Power in (+5VSB, GND)"],
             ["J2", f"1x{4 if not A else 3} male pin header", "1", "Outputs to BC-250" + ("" if A else " and PS_ON")],
             ["-", "24-pin ATX EXTENSION cable, colour-coded wires (not all-black)", "1", "Splice point - the PSU's own cable is never cut"],
             ["-", "Perfboard ~7 x 5 cm, hook-up wire, 1 female Dupont lead, heat-shrink", "-", ""]]
    s += [KeepTogether([P(f"{o}1.&nbsp;&nbsp;Get the parts", H2), table(rows, [0.5 * inch, 3.6 * inch, 0.5 * inch, W - 4.6 * inch]),
                        Spacer(1, 6), img(f"S_{o}01_Parts_Option{o}.png", 4.3 * inch)]), PageBreak()]
    # ---- 2 adapters
    s += step_page(f"{o}2", "Solder the SMD parts onto their adapter boards",
                   [("Solder the BSS138 onto a SOT-23 adapter (Q1)" if A else "Solder each BSS138 onto a SOT-23 adapter (Q1, Q2)") + ", each 0603 resistor and the diode onto a 2-pin adapter.",
                    "Check each MOSFET with the meter in diode mode: RED on adapter pin 2, BLACK on pin 3 shows a diode reading; reversed shows open (OL).",
                    "Mark the diode adapter pin on the BAND side - that pin goes toward the Pico."], f"S_{o}02_Prep_Adapters.png")
    # ---- 3 flash
    s += step_page(f"{o}3", "Flash the firmware onto the Pico",
                   ["Hold the white BOOTSEL button on the Pico.",
                    "While holding it, plug the Pico into your computer with a micro-USB data cable. Let go.",
                    "A new drive appears: <b>RPI-RP2</b> (Pico W) or <b>RP2350</b> (Pico 2 W).",
                    "Drag the matching file from the <b>Firmware</b> folder onto it: <b>GMX-BC250-Wake_Rev1_PicoW.uf2</b> for a Pico W, "
                    "<b>GMX-BC250-Wake_Rev1_Pico2W.uf2</b> for a Pico 2 W. The drive closes by itself = done."], "S_04_Flash_Firmware.png")
    # ---- 4 teach
    s += step_page(f"{o}4", "Teach the Pico your controller, then bench-test it",
                   ["Pico on USB only (no wiring yet). BC-250 OFF.",
                    "Hold BOOTSEL 5-10 seconds, let go: fast blinking = learn mode.",
                    "Hold the Xbox Series X|S controller next to the Pico and switch it on with its centre button. 3 long blinks = saved.",
                    "Switch the controller off, wait 30 s, switch it on: the Pico LED goes solid. ~21 s later one long flash = correct (no PC connected yet)."],
                   "S_05_Teach_Controller.png", 5.0 * inch)
    # ---- 5 AUTO_PWRON1
    s += step_page(f"{o}5", "Set the BC-250 AUTO_PWRON1 jumper to pins 2-3",
                   ["Unplug the power supply from the wall.",
                    "Find AUTO_PWRON1 on the top of the BC-250, near the coin battery.",
                    "Put the jumper on the two pins FARTHEST from the small printed triangle (pins 2-3). "
                    "The BC-250 then waits for its power button instead of starting by itself.",
                    "Leave CLRCMOS1 alone."], "R4_BC250_Top_AUTO_PWRON1.png")
    # ---- 6 build board
    s += step_page(f"{o}6", "Build the wake board",
                   ["Solder the Pico (on its pin headers), J1, J2" + (" and the adapters" if A else ", the adapters and SW1") + " where the picture shows them.",
                    "Run the wires exactly as shown - each colour is one connection. Wires end on the pin they touch.",
                    ("Q1 adapter" if A else "Q1 and Q2 adapters") + ": pin 1 = Gate, 2 = Source, 3 = Drain. D1 band toward the red wire (Pico pin 39).",
                    "All black wires join into the one ground wire, which goes to Pico pin 8.",
                    "J1 and J2 are solder posts: in the next steps the outside wires are soldered straight onto their pins."],
                   f"S_{o}06_Build_Board_Option{o}.png", 5.7 * inch)
    # ---- 7 ATX
    if A:
        s += step_page("A7", "Splice into the ATX extension cable (power + always-on link)",
                       ["Unplug the power supply from the wall. Plug its 24-pin plug into the extension cable. The extension's far end is not used.",
                        "PURPLE wire (+5VSB): splice a wire to it and solder the other end to J1 pin 1.",
                        "BLACK wire (any black = ground): splice a wire to it and solder the other end to J1 pin 2.",
                        "GREEN wire (PS_ON): link it to a BLACK wire with a short wire. This keeps the supply on."],
                       "S_A07_ATX_Extension.png")
    else:
        s += step_page("B7", "Splice into the ATX extension cable (power + PS_ON)",
                       ["Unplug the power supply from the wall. Plug its 24-pin plug into the extension cable. The extension's far end is not used.",
                        "PURPLE wire (+5VSB): splice a wire to it and solder the other end to J1 pin 1.",
                        "BLACK wire (any black = ground): splice a wire to it and solder the other end to J1 pin 2.",
                        "GREEN wire (PS_ON): splice a wire to it and solder the other end to J2 pin 3. Do NOT link green to black."],
                       "S_B07_ATX_Extension.png")
    # ---- 8 meter power button
    s += step_page(f"{o}8", "Find the BC-250 power-button pad with the meter",
                   ["BC-250 bottom side, rear corner behind the clear light-pipe buttons.",
                    ("Power supply plugged in, BC-250 off. Meter on DC volts." if A else
                     "The supply must be on for this test: temporarily link the GREEN wire to a BLACK wire on the extension cable "
                     "(remove the link afterwards). Plug the supply in, BC-250 off. Meter on DC volts."),
                    "Black probe on the ground pad. Red probe on the thin pin up-left of the round copper 'X' pad.",
                    "Have a helper hold the BC-250 power button: the right pin drops to 0 V while it is held (the PC will start - that's fine, shut it down afterwards).",
                    "Unplug the power supply again before soldering."], "R2_BC250_Bottom_PowerButton_MeterCheck.png")
    # ---- 9 solder
    s += step_page(f"{o}9", "Solder the power-button and ground wires",
                   ["Power supply unplugged.",
                    "Solder an ORANGE wire between J2 pin 1 and the power-button pad you found in step " + f"{o}8.",
                    "Solder a BLACK wire between J2 pin 2 and the ground pad (big leg at the board edge, left of the stacked USB).",
                    "Glue or tape the wires down so they can't pull the pads off."], "R1_BC250_Bottom_PowerButton_Ground.png")
    # ---- 10 meter TPMS1
    s += step_page(f"{o}10", "Find TPMS1 pin 9 with the meter",
                   ["BC-250 top side, TPMS1 header next to the Ethernet jack.",
                    "Find the missing pin in the row nearest the 'TPMS1' label. Same row, toward the triangle: skip one pin, the next is pin 9.",
                    "Black probe on any ground (the ground pad from step " + f"{o}9" + ", or a black wire on the extension cable). Red probe on pin 9.",
                    ("PC off: reads 0 V. Now turn the PC on with the BC-250's own power button: reads about 3.3 V. Shut the PC down again." if A else
                     "Temporarily link GREEN to BLACK on the extension cable and plug the supply in (BC-250 stays off): pin 9 reads 0 V. "
                     "Press the BC-250's own power button: about 3.3 V. Shut the PC down, unplug the supply, remove the link."),
                    "If it reads 3.3 V while the PC is off, it is the wrong pin (pin 15, right after the gap, is always 3.3 V)."],
                   "R3_BC250_Top_TPMS1_Pin9.png")
    # ---- 11 connect TPMS1
    s += step_page(f"{o}11", "Connect TPMS1 pin 9",
                   ["Power supply unplugged.",
                    "Push the female Dupont lead onto pin 9 only.",
                    f"Run it to J2 pin {3 if A else 4} on the wake board (yellow 'PC ON')."], "S_10_TPMS1_Connect.png")
    # ---- 12 everything
    s += step_page(f"{o}12", "Check everything against the full picture",
                   ["Go down the checklist in the picture and touch each wire end.",
                    "Only when everything matches: plug the power supply back into the wall."], f"S_{o}11_System_Option{o}.png", 6.0 * inch)
    # ---- 13 bazzite
    s += step_page(f"{o}13", "Bazzite: make 'Sleep' shut down instead",
                   ["The BC-250 can't wake from sleep, so 'Sleep' must do a normal shutdown.",
                    ("Start the PC with the BC-250's own power button." if A else "Start the PC with a short press on SW1 (the wake board's push button)."),
                    "On the BC-250: Desktop Mode, open a terminal (Konsole) and type the two commands below (it asks for your password; nothing shows while typing)."],
                   "S_12_Bazzite_Sleep_Fix.png", 3.6 * inch,
                   extra=[P("sudo ln -sf /usr/lib/systemd/system/poweroff.target /etc/systemd/system/suspend.target<br/>sudo systemctl daemon-reload", CODE),
                          P("To undo later: <font name='DVM'>sudo rm /etc/systemd/system/suspend.target</font> then <font name='DVM'>sudo systemctl daemon-reload</font>", SMALL)])
    # ---- 14 test
    lines = ["Power supply plugged in, BC-250 off. If the PC was just shut down, wait 60 seconds.",
             "Switch the controller on: the Pico LED goes solid and about 1.5 s later the BC-250 starts.",
             "When Bazzite is up, the controller connects to it as normal. If the controller switched itself off while the PC booted, press its centre button again."]
    lines.append("The power supply stays on all the time - that is normal for Option A." if A else
                 "After you shut the PC down, the power supply switches off about 10 seconds later.")
    s += step_page(f"{o}14", "First real test", lines, f"S_{o}13_First_Test.png", 4.6 * inch,
                   extra=[info(f"<b>Done.</b> If something didn't work, see Troubleshooting on page {pg('REF')}.")])
    return s

def build():
    s = []
    s += [Spacer(1, 8), P("GMX BC-250 Controller Wake", TITLE),
          P("Install guide Rev 1.2  -  firmware Rev 1  -  Grumblymanx Mods", SUB), Spacer(1, 10),
          P("Turns an AMD BC-250 running Bazzite <b>on</b> when you switch on an <b>Xbox Series X|S controller</b>. "
            "A Raspberry Pi Pico W or Pico 2 W, powered from the ATX supply's always-on +5VSB wire, listens for the "
            "controller's Bluetooth broadcast and presses the BC-250's power button for you. The controller still pairs and "
            "connects to the BC-250 itself, exactly as before."),
          box("<b>Status:</b> the firmware compiles for both boards but has not yet been tested on real hardware. "
              "Do the bench test (step 4) before installing. The BC-250 pictures are renders based on reference photos - "
              "positions are close, not exact; the meter checks in steps 8 and 10 confirm them."),
          Spacer(1, 10), P("Choose ONE install option", H1)]
    opt = Table([
        [P("<b>OPTION A</b><br/>Power supply always on", CELLB), P("<b>OPTION B</b><br/>Pico switches the power supply", CELLB)],
        [P("- Green PS_ON wire linked to black: the supply's 12 V stays on all the time.<br/>"
           "- Wake board presses the BC-250 power button only.<br/>"
           "- The BC-250's own power button still works.<br/>"
           "- Fewer parts (1 MOSFET).<br/>- Simplest.", CELL),
         P("- Supply completely off while the PC is off; the Pico switches it on.<br/>"
           "- Wake board switches PS_ON, then presses the power button.<br/>"
           "- While off, the BC-250's own button does nothing; a push button on the wake board is used instead.<br/>"
           "- 2 MOSFETs + push button.", CELL)],
        [P(f"<b>Go to page {pg('A')}</b>  (steps A1 - A14)", CELLB), P(f"<b>Go to page {pg('B')}</b>  (steps B1 - B14)", CELLB)]],
        colWidths=[W / 2, W / 2])
    opt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#4E7D66")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                             ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E8F5E9")), ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#E3F2FD")),
                             ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#FFF8E1")),
                             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    s += [opt, Spacer(1, 10),
          P(f"Each option is complete on its own - follow only the section you chose, from its first step to its last. "
            f"<b>Reference</b> (LED meanings, buttons, troubleshooting, credits): page {pg('REF')}."), PageBreak()]
    s += section("A")
    s += section("B")
    # ---------------- reference
    s += [Anchor("REF"), P("Reference", H1), P("Pico LED", H2),
          table([["LED", "Meaning"],
                 ["Double flash every 2 s", "Running, no controller saved yet"],
                 ["Single short flash every 2 s", "Listening for saved controllers (PC off)"],
                 ["Solid on", "PC is on, or the wake sequence is running"],
                 ["Fast blinking", "Learn mode (up to 30 s)"],
                 ["3 long blinks", "Controller saved"],
                 ["6 quick blinks", "All saved controllers forgotten"],
                 ["One long 2-second flash", "Learn mode found nothing, or wake failed (no 'PC is on' signal)"]], [2.4 * inch, W - 2.4 * inch]),
          Spacer(1, 6), P("Buttons", H2),
          table([["Button", "Hold, then release", "Does"],
                 ["BOOTSEL (both options) or SW1 (Option B)", "5 - 10 seconds", "Learn mode (teach a controller)"],
                 ["BOOTSEL (both options) or SW1 (Option B)", "over 10 seconds", "Forget all saved controllers"],
                 ["SW1 (Option B)", "short press, PC off", "Switch the supply on and start the PC"],
                 ["SW1 (Option B)", "short press, PC on", "Press the BC-250 power button once (normal shutdown)"]], [2.4 * inch, 1.6 * inch, W - 4.0 * inch]),
          P("Up to 4 controllers can be saved; a 5th replaces the oldest. Saved controllers survive power cuts and re-flashing the same firmware.", SMALL),
          Spacer(1, 6), P("Troubleshooting", H2),
          table([["Problem", "Check"],
                 ["Pico LED does nothing", "+5VSB reaching Pico pin 39? D1 band toward the Pico? Correct .uf2 for your board?"],
                 ["Learn mode ends with a long flash", "Controller right next to the Pico, switched on normally (not pairing). BC-250 off."],
                 ["LED goes solid but the PC doesn't start", "AUTO_PWRON1 on pins 2-3? Orange wire on the right pad (redo the meter test)? Q1 pins 1-2-3 = G-S-D? "
                  "Option B: green wire on Q2's drain, link removed?"],
                 ["PC starts, then a long flash after 20 s", "'PC is on' signal missing: TPMS1 pin 9 (3.3 V with PC on) and R3 to Pico pin 6."],
                 ["Option B: PC dies a few seconds after starting", "Same as above - without the 'PC is on' signal the Pico switches the supply off again."],
                 ["PC turns back on right after shutdown", "Controller still on after the 60 s ignore time - switch it off when you shut down."],
                 ["Anything else", "Open a serial monitor at 115200 baud on the Pico's USB port - it prints every step it takes."]],
                [2.3 * inch, W - 2.3 * inch]),
          Spacer(1, 6), P("Credits", H2),
          P("Wake method (listen for the controller's Bluetooth LE broadcast, then press the power button): dexikdex "
            "(ESP32-BC250-LOP_PSU-PowerON-Xbox) and GreatApo (BC250_ESP32_ATX_PSU). This Pico firmware is new code using their method. "
            "BC-250 details: tfabris/BC-250 and the elektricm amd-bc250-docs; BC-250 renders were drawn from tfabris's reference photos. "
            "ATX 24-pin layout: AESTECHNO pinout reference. BOOTSEL reading: Raspberry Pi pico-examples (BSD-3-Clause). "
            "Bluetooth: BTstack via the Raspberry Pi Pico SDK 2.2.0.", SMALL),
          P("https://github.com/tfabris/BC-250<br/>https://github.com/GreatApo/BC250_ESP32_ATX_PSU<br/>"
            "https://elektricm.github.io/amd-bc250-docs/hardware/pinouts<br/>https://www.aestechno.com/en/resources/pinouts/pc-power-atx-pcie-fan/", CODE)]
    return s

def footer(c, d):
    c.saveState(); c.setFont("DV", 8); c.setFillColor(colors.HexColor("#78909C"))
    c.drawString(0.6 * inch, 0.42 * inch, "GMX BC-250 Controller Wake  -  install guide Rev 1.2  -  Grumblymanx Mods")
    c.drawRightString(letter[0] - 0.6 * inch, 0.42 * inch, f"Page {d.page}")
    c.restoreState()

def make():
    doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.6 * inch, rightMargin=0.6 * inch, topMargin=0.55 * inch,
                            bottomMargin=0.65 * inch, title="GMX BC-250 Controller Wake - install guide Rev 1.2", author="Grumblymanx Mods")
    doc.build(build(), onFirstPage=footer, onLaterPages=footer)

make()            # pass 1: record page numbers
first = dict(PAGES)
make()            # pass 2: print them
assert first == PAGES, (first, PAGES)
print(OUT, PAGES)
