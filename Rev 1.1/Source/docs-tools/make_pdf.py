import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
from reportlab.lib.fonts import addMapping
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DVB"); addMapping("DV", 0, 1, "DV"); addMapping("DV", 1, 1, "DVB")

HERE = os.path.dirname(os.path.abspath(__file__))
DIA = os.path.join(HERE, "..", "diagrams")
REN = os.path.join(HERE, "..", "renders")
OUT = os.path.join(HERE, "GMX-BC250-Controller-Wake_Rev1.1_Guide.pdf")

ss = getSampleStyleSheet()
B = ParagraphStyle("B", parent=ss["Normal"], fontName="DV", fontSize=11, leading=15.5, spaceAfter=5)
H1 = ParagraphStyle("H1", parent=B, fontName="DVB", fontSize=17, leading=22, spaceBefore=10, spaceAfter=8, textColor=colors.HexColor("#1F4E3D"))
H2 = ParagraphStyle("H2", parent=B, fontName="DVB", fontSize=13, leading=17, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#263238"))
TITLE = ParagraphStyle("T", parent=B, fontName="DVB", fontSize=24, leading=30, alignment=1, spaceAfter=6)
SUB = ParagraphStyle("S", parent=B, fontSize=13, alignment=1, textColor=colors.HexColor("#455A64"))
CODE = ParagraphStyle("C", parent=B, fontName="DVM", fontSize=9.5, leading=13, backColor=colors.HexColor("#ECEFF1"),
                      borderPadding=6, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8)
CELL = ParagraphStyle("cell", parent=B, fontSize=9.5, leading=12.5, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="DVB")
STEP = ParagraphStyle("step", parent=B, leftIndent=18, firstLineIndent=-18)

W = letter[0] - 1.3 * inch

def P(t, s=B): return Paragraph(t, s)
def steps(items):
    return [P(f"<b>{i+1}.</b>&nbsp;&nbsp;{t}", STEP) for i, t in enumerate(items)]
def img(name, maxh=8.4 * inch):
    path = os.path.join(REN if name.startswith("R") else DIA, name)
    w, h = PILImage.open(path).size
    sc = min(W / w, maxh / h)
    return Image(path, width=w * sc, height=h * sc)
def note(t, color="#FFF8E1", edge="#F9A825"):
    t = Table([[P(t, CELL)]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(color)),
                           ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor(edge)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t
def table(rows, widths, head=True):
    data = [[P(str(c), CELLB if (head and r == 0) else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CFE8DA")))
    t.setStyle(TableStyle(st))
    return t

s = []
# ---------------- cover ----------------
s += [Spacer(1, 30), P("GMX BC-250 Controller Wake", TITLE), P("Rev 1.1  -  Build, Flash &amp; Install Guide  (firmware Rev 1)", SUB), Spacer(1, 6),
      P("Turn your AMD BC-250 (Bazzite) on with an Xbox Series X|S controller, using a Raspberry Pi Pico W or Pico 2 W", SUB),
      P("Grumblymanx Mods", SUB), Spacer(1, 16)]
s.append(note("<b>Please read first - what has and has NOT been tested</b><br/>"
              "- Both firmware files were compiled successfully and checked to be built for the right chip (Pico W = RP2040, Pico 2 W = RP2350).<br/>"
              "- The firmware has <b>NOT</b> been run on real hardware yet. Your bench test (Section 5) is the first real test.<br/>"
              "- The wake method (listen for the controller's Bluetooth LE broadcast, then press the power button) comes from two "
              "published ESP32 projects for the BC-250 (credits at the end). I have not tested it with your controller.<br/>"
              "- The BC-250 and ATX pictures (R1-R5) are <b>renders made from reference photos</b>, not photos of your board. Positions are close but not exact - "
              "use the meter checks to confirm every BC-250 point before soldering.<br/>"
              "- New in Rev 1.1: realistic renders R1-R5 replace the old drawn BC-250 and ATX pictures. The firmware is unchanged (still Rev 1)."))
s.append(Spacer(1, 10))
s.append(P("What's in this guide", H2))
s += steps(["How it works", "Choose your wiring option (A or B)", "Parts list", "Flash the firmware (.UF2)",
            "Bench test + teach it your controller", "Set the BC-250 jumper", "Wire it up", "Bazzite: make 'Sleep' shut down instead",
            "First real test", "LED + button reference", "Troubleshooting", "Credits"])
s.append(PageBreak())

# ---------------- 1 ----------------
s += [P("1.  How it works", H1), img("Fig1_Overview.png", 4.2 * inch)]
s += [P("While the BC-250 is off, the Pico stays powered from the power supply's always-on <b>+5VSB</b> (standby) wire and "
        "quietly <b>listens</b> for Bluetooth LE broadcasts. When you switch on a controller it has been taught (Section 5), it:"),
      *steps(["switches the power supply on (only if you use Option B), waits 1 second,",
              "'presses' the BC-250 power button for 0.5 seconds (Q1 does this),",
              "waits up to 20 seconds for the BC-250's 'PC is on' signal (TPMS1 pin 9)."]),
      P("The Pico never connects to the controller. Your controller still pairs and connects to the BC-250 exactly like it does now. "
        "After the PC shuts down, the Pico ignores the controller for 60 seconds so a controller that is still on can't turn the PC straight back on.")]

# ---------------- 2 ----------------
s += [P("2.  Choose your wiring option", H1),
      P("The firmware works with <b>both</b> options - you choose by how you wire it. Both options need the BC-250's "
        "AUTO_PWRON1 jumper on pins 2-3 (Section 6)."),
      table([["", "Option A  -  power supply always on", "Option B  -  Pico switches the power supply"],
             ["How", "Keep (or add) a permanent jumper from the green PS_ON wire to a black ground wire. Leave out Q2 + R2 (strip 4).",
              "No PS_ON jumper. Q2 lets the Pico turn the power supply on and off."],
             ["Good", "Simplest. The BC-250's own power button still works. A Pico reset can never cut power to a running PC.",
              "The power supply's main outputs are fully off while the PC is off (less standby power, quieter)."],
             ["Watch out", "The power supply's main 12 V output stays on all the time (it is just not loaded much).",
              "With the supply off, the BC-250's own rear button does nothing - use the controller, or the optional SW1 button on the Pico. "
              "Don't unplug or re-flash the Pico while the PC is running: the supply would switch off."]],
            [0.9 * inch, (W - 0.9 * inch) / 2, (W - 0.9 * inch) / 2]),
      Spacer(1, 6),
      note("I have not picked one for you. If you are not sure, Option A is the simplest to get working first - you can add Q2 later "
           "and move to Option B without changing the firmware.", "#E3F2FD", "#1565C0")]

# ---------------- 3 ----------------
s += [P("3.  Parts list", H1),
      P("I searched your <b>Xbox Stuff - All BOM Components.xlsx</b>. The parts below are listed there (the 'From' column is the project "
        "folder the spreadsheet lists). <b>Please confirm you still physically have them before you start.</b>"),
      table([["Ref", "Part", "Qty", "From (your spreadsheet)", "Notes"],
             ["-", "Raspberry Pi Pico W  or  Pico 2 W", "1", "you have both", "Use the matching .UF2 file"],
             ["Q1", "BSS138LT1G N-MOSFET, SOT-23 (LCSC C82045)", "1", "Anik recreated / Xblast Lite", "Power-button switch. Pins: 1 Gate, 2 Source, 3 Drain (onsemi datasheet)"],
             ["Q2", "BSS138LT1G (same as Q1)", "1", "Anik recreated / Xblast Lite", "Option B only"],
             ["R1, R2", "10k resistor 0603 (RC0603FR-0710KL, C98220)", "2", "Anik recreated / Xblast Lite", "R2 only for Option B"],
             ["R3", "1k resistor 0603 (RC0603FR-071KL, C22548)", "1", "Anik recreated / Xblast Lite", "Protects the Pico input"],
             ["D1", "1N5819WS Schottky diode, SOD-323 (C191023)", "1", "Darkone Customs (Pico ModXo)", "Band (cathode) toward Pico VSYS"],
             ["R4", "470 ohm resistor 0805 (RC0805FR-07470RL)", "1", "OGX Mini / Anik recreated", "Optional status LED"],
             ["LED1", "any LED", "1", "-", "Optional"],
             ["SW1", "momentary push button", "1", "not in the spreadsheet", "Optional (BOOTSEL works too). Useful for Option B"],
             ["-", "24-pin ATX breakout board or female 24-pin socket", "1", "not in the spreadsheet", "So you don't cut your power supply's cable"],
             ["-", "Thin hook-up wire, perfboard, heat-shrink", "-", "-", ""]],
            [0.55 * inch, 2.0 * inch, 0.45 * inch, 1.45 * inch, W - 4.45 * inch]),
      Spacer(1, 6),
      note("The MOSFETs, resistors and diode are tiny surface-mount parts. Easiest: solder each SOT-23 MOSFET onto a "
           "SOT-23-to-DIP adapter, or solder thin wires straight to the part. If you'd rather use through-hole parts, tell me "
           "and I'll check stock and minimum order quantities before giving part numbers. I have not picked an ATX breakout "
           "or push button part number yet for the same reason.", "#E3F2FD", "#1565C0"),
      Spacer(1, 6), img("Fig6_Part_Orientation.png", 2.6 * inch)]
s.append(PageBreak())

# ---------------- 4 ----------------
s += [P("4.  Flash the firmware (.UF2)", H1),
      table([["Your board", "Firmware file (Firmware folder)", "USB drive name it shows"],
             ["Raspberry Pi Pico W", "GMX-BC250-Wake_Rev1_PicoW.uf2", "RPI-RP2"],
             ["Raspberry Pi Pico 2 W", "GMX-BC250-Wake_Rev1_Pico2W.uf2", "RP2350"]],
            [1.6 * inch, 2.9 * inch, W - 4.5 * inch]),
      Spacer(1, 6),
      *steps(["Unplug the Pico from everything (USB and wiring).",
              "Hold down the white <b>BOOTSEL</b> button on the Pico.",
              "While holding it, plug the Pico into your PC with a micro-USB <b>data</b> cable. Then let go.",
              "A new USB drive appears (name in the table above).",
              "Drag the matching .UF2 file onto that drive. The drive disappears by itself when it's done - that's normal.",
              "The Pico restarts and runs the wake firmware. Its LED gives a <b>double flash every 2 seconds</b> (= running, no controller taught yet)."]),
      note("Wrong file? Nothing gets damaged - the board just won't run it. Repeat the steps with the other file. "
           "Your old OGX-Mini firmware on that Pico will be replaced.")]

# ---------------- 5 ----------------
s += [P("5.  Bench test + teach it your controller", H1),
      P("Do this on your desk with the Pico powered from USB only (no wiring yet). Have the BC-250 <b>off</b> so the controller "
        "doesn't connect to it during this test."),
      P("Teach (learn) the controller", H2),
      *steps(["Make sure the Pico has been running for a few seconds (LED double-flashing).",
              "Press and <b>hold BOOTSEL for 5 to 10 seconds</b>, then let go. (Count it. Under 5 s does nothing; over 10 s forgets all controllers.)",
              "The LED blinks fast = learn mode (lasts up to 30 seconds).",
              "Hold the controller right next to the Pico (a few cm) and switch it on with the Xbox button - a normal switch-on, "
              "<b>not</b> the pairing button on top.",
              "About 3 seconds later the LED gives <b>3 long blinks</b> = controller saved. The LED then changes to a single short "
              "flash every 2 seconds (= listening).",
              "If you get one long 2-second flash instead, nothing was heard - try again closer, or see Troubleshooting."]),
      P("Test the wake (no PC needed)", H2),
      *steps(["Switch the controller off (hold the Xbox button about 6 s) and wait 30 seconds (the Pico ignores controllers for 30 s after learning).",
              "Switch it on again.",
              "The Pico LED goes <b>solid on</b> = it heard the controller and is running the wake sequence.",
              "Because nothing is wired, it gets no 'PC is on' signal: after about 21 seconds you see one long flash (= wake failed). "
              "<b>On the bench that is the correct result.</b>"]),
      note("Optional: watch the Pico's log. Open Arduino IDE (or PuTTY), pick the Pico's COM port, Serial Monitor at 115200. "
           "You'll see lines like '[BT] saved controller ... heard -> turning PC on'.", "#E3F2FD", "#1565C0"),
      note("<b>Not verified:</b> the reference project says the controller must support Bluetooth LE. If the Pico never hears the "
           "controller in this test, the controller's own firmware may matter - tell me what you see in the log and I'll look into it.")]
s.append(PageBreak())

# ---------------- 6 ----------------
s += [P("6.  Set the BC-250 AUTO_PWRON1 jumper", H1),
      P("Unplug the power supply from the wall first. Move the AUTO_PWRON1 jumper to <b>pins 2-3</b> "
        "('wait for power button' mode - render R4 below). This is needed for both options: "
        "the BC-250 then stays off until its power button is pressed, and the Pico is what presses it."),
      note("If your jumper is currently on pins 1-2 (the default), your BC-250 has been turning itself on whenever 12 V arrives. With the wake "
           "board, leave it on 2-3."), Spacer(1, 6), img("R4_BC250_Top_AUTO_PWRON1.png", 4.6 * inch)]

# ---------------- 7 ----------------
s += [P("7.  Wire it up", H1),
      note("<b>Unplug the power supply from the wall for all soldering and wiring.</b> Only plug it in for the meter checks, "
           "and never let a probe touch two pins/legs at once.", "#FFEBEE", "#C62828"),
      P("Work through the wiring picture one numbered strip at a time. Where each wire goes on the BC-250 and the ATX plug is shown in renders R1-R5:"),
      table([["Strip", "What it does", "Option A", "Option B"],
             ["1", "+5VSB (purple) -> D1 -> Pico pin 39 VSYS", "yes", "yes"],
             ["2", "Ground: ATX black + Pico pin 38 + BC-250 ground pad", "yes", "yes"],
             ["3", "Q1 across the BC-250 power button (Pico pin 4 GP2)", "yes", "yes"],
             ["4", "Q2 on the green PS_ON wire (Pico pin 5 GP3)", "NO - keep PS_ON jumpered", "yes - remove PS_ON jumper"],
             ["5", "TPMS1 pin 9 -> R3 -> Pico pin 6 GP4", "yes", "yes"],
             ["6", "Optional button (pin 7) + LED (pin 9)", "optional", "recommended (button)"]],
            [0.6 * inch, 3.4 * inch, 1.3 * inch, W - 5.3 * inch]),
      PageBreak(), img("Fig2_Wiring.png", 9.0 * inch), PageBreak(),
      P("Order of work", H2),
      *steps(["<b>TPMS1 pin 9</b> (render R3): do the meter check first (PC on = about 3.3 V, PC off = 0 V). Only then connect strip 5 "
              "- a Dupont jumper wire pushes straight onto the pin, no soldering needed.",
              "<b>Power-button pad</b> (renders R1 + R2): do the meter test in R2. Unplug, then solder the orange wire (Q1 drain) to that "
              "pin and the black wire to the ground pad (R1). Add strain relief (glue/tape) - the pads can lift.",
              "<b>ATX plug</b> (render R5): connect purple, black (and green for Option B) through your breakout - go by wire colour.",
              "Build the small board (strips 1-6) and connect it to the Pico pins shown in the Pico picture.",
              "Double-check D1's band points toward the Pico, and each MOSFET's Drain/Gate/Source."]),
      img("R3_BC250_Top_TPMS1_Pin9.png", 4.6 * inch), PageBreak(),
      img("R1_BC250_Bottom_PowerButton_Ground.png", 4.6 * inch), Spacer(1, 6),
      img("R2_BC250_Bottom_PowerButton_MeterCheck.png", 4.6 * inch), PageBreak(),
      img("R5_ATX24_Plug_Wires.png", 8.0 * inch),
      PageBreak(), img("Fig3_PicoW_Pins.png", 8.0 * inch)]
s.append(PageBreak())

# ---------------- 8 ----------------
s += [P("8.  Bazzite: make 'Sleep' shut down instead", H1),
      P("The BC-250 can't sleep - choosing 'Sleep' in Steam leaves it hung with a black screen. Two BC-250 guides "
        "(tfabris/BC-250 and the elektricm BC-250 docs) use this fix so 'Sleep' does a normal shutdown instead. "
        "Then the controller can turn it back on. Open a terminal (Konsole) on the BC-250 and run:"),
      P("sudo ln -sf /usr/lib/systemd/system/poweroff.target /etc/systemd/system/suspend.target<br/>sudo systemctl daemon-reload", CODE),
      P("To undo it later:"),
      P("sudo rm /etc/systemd/system/suspend.target<br/>sudo systemctl daemon-reload", CODE),
      note("These are the exact commands from those guides. I haven't run them on your machine. It asks for your password "
           "after 'sudo' - nothing shows while you type it, that's normal.")]

# ---------------- 9 ----------------
s += [P("9.  First real test", H1),
      *steps(["Plug the power supply in at the wall. The Pico LED starts (single short flash every 2 s if a controller is saved).",
              "Option A only: the BC-250 stays off (AUTO_PWRON1 on 2-3). Option B: the power supply fan stays off.",
              "Wait at least 60 seconds if the PC was just shut down.",
              "Switch on the controller. Pico LED goes solid; about 1.5 s later the BC-250 starts.",
              "When Bazzite is up, the controller connects to the BC-250 as normal. If the controller timed out and switched "
              "itself off while the PC was booting, just press the Xbox button again.",
              "Shut down from Steam (or use 'Sleep' after Section 8). Pico LED goes back to the short flash. "
              "Option B: about 10 seconds after the PC is off, the power supply switches off."])]

# ---------------- 10 ----------------
s += [P("10.  LED + button reference", H1),
      table([["Pico LED (and optional LED1)", "Meaning"],
             ["Double flash every 2 s", "Running, no controller saved yet"],
             ["Single short flash every 2 s", "Listening for saved controllers (PC off)"],
             ["Solid on", "PC is on, or the wake sequence is running"],
             ["Fast blinking", "Learn mode (up to 30 s)"],
             ["3 long blinks", "Controller saved"],
             ["6 quick blinks", "All saved controllers forgotten"],
             ["One long 2-second flash", "Learn mode found nothing, or wake failed (no 'PC is on' signal)"]],
            [2.4 * inch, W - 2.4 * inch]),
      Spacer(1, 8),
      table([["Button", "Hold time, then release", "Does"],
             ["BOOTSEL or SW1", "5 - 10 seconds", "Learn mode (teach a controller)"],
             ["BOOTSEL or SW1", "over 10 seconds", "Forget all saved controllers"],
             ["SW1 only", "short press (under 3 s), PC off", "Turn the PC on (same as the controller)"],
             ["SW1 only", "short press (under 3 s), PC on", "Presses the BC-250 power button once (normal shutdown request)"]],
            [1.4 * inch, 2.0 * inch, W - 3.4 * inch]),
      P("Up to 4 controllers can be saved. Saving a 5th replaces the oldest. Saved controllers survive power cuts and "
        "re-flashing the same firmware.")]

# ---------------- 11 ----------------
s += [P("11.  Troubleshooting", H1),
      table([["Problem", "Check"],
             ["LED does nothing at all", "USB/5VSB power reaching pin 39 VSYS? D1 the right way round (band toward the Pico)? Right .UF2 for your board?"],
             ["Learn mode ends with a long flash", "Controller must be right next to the Pico and switched on (not pairing mode). BC-250 off so it doesn't connect first. Check the log."],
             ["Controller heard, LED solid, PC doesn't start", "AUTO_PWRON1 on pins 2-3? Orange wire on the correct power-button leg (redo the meter test)? Q1 pin order? Option B: green PS_ON on Q2 drain, and supply really switches on?"],
             ["PC starts, then the Pico shows a long flash after 20 s", "The 'PC is on' signal isn't arriving: check TPMS1 pin 9 (meter: 3.3 V with PC on) and R3 to pin 6 GP4."],
             ["PC turns back on right after shutdown", "Controller still on after the 60 s ignore window. Switch the controller off when shutting down."],
             ["Option B: PC dies a few seconds after it starts", "The 'PC is on' signal isn't reaching the Pico, so it switches the supply off again. Fix strip 5."],
             ["Something else", "Copy the Serial Monitor log (115200) and send it to me."]],
            [2.1 * inch, W - 2.1 * inch])]

# ---------------- 12 ----------------
s += [P("12.  Credits", H1),
      P("- Wake method (BLE listen + press power button, cooldown timings): <b>dexikdex</b> - ESP32-BC250-LOP_PSU-PowerON-Xbox, and "
        "<b>GreatApo</b> - BC250_ESP32_ATX_PSU (both GPL-3.0, ESP32). This Pico firmware is new code written for this project; "
        "it uses their method, not their code."),
      P("- BC-250 details (AUTO_PWRON1, power-button pads, TPMS1 3V pin): <b>tfabris/BC-250</b> on GitHub and the "
        "<b>elektricm amd-bc250-docs</b> pinout page. Renders R1-R4 were drawn from tfabris's reference photos (not copies of them)."),
      P("- ATX 24-pin layout (contact side, latch up: top row 13-24, bottom row 1-12): AESTECHNO ATX pinout page."),
      P("- BOOTSEL button reading: Raspberry Pi pico-examples (BSD-3-Clause). Bluetooth: BTstack via the Raspberry Pi Pico SDK 2.2.0."),
      Spacer(1, 6),
      P("Sources", H2),
      P("https://github.com/tfabris/BC-250<br/>https://github.com/GreatApo/BC250_ESP32_ATX_PSU<br/>"
        "https://elektricm.github.io/amd-bc250-docs/hardware/pinouts<br/>https://www.aestechno.com/en/resources/pinouts/pc-power-atx-pcie-fan/", CODE)]

def footer(c, d):
    c.saveState(); c.setFont("DV", 8); c.setFillColor(colors.HexColor("#78909C"))
    c.drawString(0.65 * inch, 0.45 * inch, "GMX BC-250 Controller Wake  -  Rev 1.1 guide  -  Grumblymanx Mods")
    c.drawRightString(letter[0] - 0.65 * inch, 0.45 * inch, f"Page {d.page}")
    c.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.65 * inch, rightMargin=0.65 * inch,
                        topMargin=0.6 * inch, bottomMargin=0.7 * inch, title="GMX BC-250 Controller Wake Rev 1.1",
                        author="Grumblymanx Mods")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
