import sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from PIL import Image as PI

ren, outpdf = sys.argv[1], sys.argv[2]
ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=14, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#1d4fa3"))
B = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10.5, leading=14.5)
NOTE = ParagraphStyle("n", parent=B, backColor=colors.HexColor("#fff4d6"), borderPadding=6, borderColor=colors.HexColor("#e0b400"), borderWidth=0.6)


def img(name, w=6.8 * inch):
    p = os.path.join(ren, name)
    iw, ih = PI.open(p).size
    return Image(p, width=w, height=w * ih / iw)


CELL = ParagraphStyle("c", parent=B, fontSize=9.5, leading=12)
CELLH = ParagraphStyle("ch", parent=CELL, fontName="Helvetica-Bold")


def table(rows, widths):
    rows = [[Paragraph(str(c), CELLH if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10), ("FONT", (0, 1), (-1, -1), "Helvetica", 9.5),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe8f7")), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


s = []
s.append(Paragraph("GMX BC-250 Controller Wake - Pico Shell (Rev 1)", H1))
s.append(Paragraph("3D-printed shell for the Raspberry Pi Pico W and Pico 2 W. Grumblymanx Mods.", B))
s.append(Spacer(1, 6))
s.append(Paragraph("<b>Not test-printed yet.</b> The shell was checked in 3D against a Pico W 3D model "
                   "(no parts collide) and against the official Pico 2 W drawing (same outline, holes and pin rows). "
                   "Printers vary, so print one Base and the Blank lid first as a fit test before printing the others.", NOTE))

s.append(Paragraph("What is in the zip", H2))
s.append(table([
    ["Folder", "What it is", "What to do with it"],
    ["STL", "Print-ready files, already laid flat the right way up", "Open in your slicer and print"],
    ["STEP", "CAD files (assembled orientation)", "Only needed if you want to edit in CAD"],
    ["Source", "Python script that makes the model", "Only needed to change sizes"],
    ["Renders", "Pictures of every part", "For reference"],
    ["Docs", "This guide", "Read it"],
], [0.9 * inch, 2.9 * inch, 3.0 * inch]))

s.append(Paragraph("Which files to print", H2))
s.append(Paragraph("Every version uses the <b>same base</b>. Only the lid changes. For one complete shell, print "
                   "<b>Pico-Shell_Base.stl</b> plus <b>one</b> lid:", B))
s.append(table([
    ["Lid file", "Top of the lid says"],
    ["Pico-Shell_Lid_GMX-Mods.stl", "Grumbly logo + GMX MODS"],
    ["Pico-Shell_Lid_Bazzite.stl", "Bazzite"],
    ["Pico-Shell_Lid_BC-250.stl", "BC-250"],
    ["Pico-Shell_Lid_Blank.stl", "Nothing (plain)"],
], [3.0 * inch, 3.8 * inch]))
s.append(Spacer(1, 6))
g = [[img("Lid_GMX-Mods_top.png", 3.3 * inch), img("Lid_Bazzite_top.png", 3.3 * inch)],
     [img("Lid_BC-250_top.png", 3.3 * inch), img("Lid_Blank_top.png", 3.3 * inch)]]
s.append(Table(g, colWidths=[3.4 * inch, 3.4 * inch]))
s.append(PageBreak())

s.append(Paragraph("Print settings", H2))
s.append(table([
    ["Setting", "Use this"],
    ["Material", "PLA or PETG"],
    ["Nozzle / layer height", "0.4 mm nozzle, 0.2 mm layers (0.12-0.16 mm makes the logo crisper)"],
    ["Walls / perimeters", "At least 3 (the walls are 1.6 mm thick, 4 perimeters fills them solid)"],
    ["Infill", "Any (20% is fine), the parts are mostly solid walls"],
    ["Supports", "None"],
    ["Orientation", "Leave as loaded. Base: floor on the bed. Lid: flat top (with the writing) on the bed"],
    ["Elephant foot", "Turn on elephant-foot compensation if your slicer has it, so the writing on the bed side does not fill in"],
], [1.8 * inch, 5.0 * inch]))
s.append(Spacer(1, 4))
s.append(Paragraph("The writing on the lid is cut 0.6 mm into the top. Because the top prints against the bed, the writing comes "
                   "out on the smooth bed side. The Grumbly logo's thinnest lines were widened slightly (to about 0.6 mm) "
                   "so a 0.4 mm nozzle can print them.", B))
s.append(img("Lid_underside.png", 5.0 * inch))
s.append(Paragraph("Putting it together", H2))
steps = [
    "<b>Solder your wires to the Pico first.</b> Solder them to the edge pads so they stick straight out sideways from the board edge (not straight up).",
    "<b>Set the Pico on the base.</b> Components facing up, micro-USB end at the end wall with the big notch. The 4 small pegs go through the Pico's 4 mounting holes.",
    "<b>Lay the wires in the side gaps.</b> Each long side has an open gap that runs the full length of the pin rows. Wires leave through that gap.",
    "<b>Press the lid straight down.</b> The notch in the lid goes over the USB end. Push until both ends click. The 4 posts under the lid hold the Pico down.",
    "<b>To open it,</b> pull the lid's end flaps outward a little with a fingernail and lift.",
]
for i, t in enumerate(steps, 1):
    s.append(Paragraph(f"{i}. {t}", B)); s.append(Spacer(1, 3))
s.append(Table([[img("Base_with_Pico.png", 3.35 * inch), img("Exploded.png", 3.35 * inch)]], colWidths=[3.45 * inch, 3.45 * inch]))
s.append(Paragraph("Openings", H2))
s.append(table([
    ["Opening", "Where", "What it is for"],
    ["Side wire gaps", "Both long sides, full length of the pins, 3.2 mm tall", "Wires out from any GPIO / power pad"],
    ["Micro-USB notch", "USB end, 11.5 mm wide", "Plug in USB to load firmware without opening the shell"],
    ["Round hole (4 mm)", "Lid, over the BOOTSEL button", "Press BOOTSEL with a toothpick or pen tip"],
    ["Small oval (3.4 x 2.6 mm)", "Lid, near the USB end", "See the Pico's onboard LED"],
], [1.6 * inch, 2.5 * inch, 2.7 * inch]))
s.append(img("Side_wire_slot.png", 6.6 * inch))
s.append(img("USB_end.png", 3.0 * inch))

s.append(Paragraph("Size", H2))
s.append(Paragraph("Closed shell: about 24.8 x 57.1 x 8.6 mm. It is plastic only (no metal), so it does not block the Pico's "
                   "WiFi/Bluetooth antenna. Keep metal away from the antenna end (the end opposite the USB) when you mount it.", B))

s.append(Paragraph("What was checked, and what was not", H2))
s.append(Paragraph("<b>Checked:</b> Pico W 3D model (Ki-Lime Pi Pico library) placed in the shell: 0 overlap with the base and the lid; "
                   "0.45 mm gap between the tallest part (micro-USB) and the lid. Base and lid don't overlap when closed, and the snap bumps "
                   "do overlap the base wall while the lid is going on (that is the click). All STL files are closed, printable solids. "
                   "Pico 2 W outline, hole spacing and pin rows checked against Figure 3 of the official Pico 2 W datasheet.", B))
s.append(Spacer(1, 4))
s.append(Paragraph("<b>Not checked:</b> no test print yet. The Pico 2 W BOOTSEL button and LED positions were only compared by eye with the "
                   "Pico 2 W datasheet drawing (it shows the same layout as the Pico W). The holes were made a bit oversized to allow for this. "
                   "How tight the snap feels depends on your printer.", B))
SimpleDocTemplate(outpdf, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                  title="GMX BC-250 Pico Shell Rev 1 Guide").build(s)
print("pdf ok")
