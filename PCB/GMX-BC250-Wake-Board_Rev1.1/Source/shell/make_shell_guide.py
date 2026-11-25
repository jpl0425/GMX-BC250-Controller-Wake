"""Print + assembly guide for the GMX BC-250 Wake Board Shell Rev 1."""
import sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PI

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
ren, outpdf = sys.argv[1], sys.argv[2]
ss = getSampleStyleSheet()
B = ParagraphStyle("b", parent=ss["Normal"], fontName="DV", fontSize=12, leading=16.5, spaceAfter=4)
H1 = ParagraphStyle("h1", parent=B, fontName="DVB", fontSize=22, leading=27, spaceAfter=6, textColor=colors.HexColor("#1F4E3D"))
H2 = ParagraphStyle("h2", parent=B, fontName="DVB", fontSize=16, leading=21, spaceBefore=4, spaceAfter=6, textColor=colors.HexColor("#263238"))
STEP = ParagraphStyle("st", parent=B, leftIndent=20, firstLineIndent=-20)
CELL = ParagraphStyle("c", parent=B, fontSize=11, leading=14, spaceAfter=0)
CELLB = ParagraphStyle("cb", parent=CELL, fontName="DVB")
W = letter[0] - 1.2 * inch

def P(t, s=B): return Paragraph(t, s)
def img(name, maxh=5.2 * inch):
    p = os.path.join(ren, name); w, h = PI.open(p).size; k = min(W / w, maxh / h)
    return Image(p, width=w * k, height=h * k)
def box(t, bg="#FFF8E1", edge="#F9A825"):
    tb = Table([[P(t, CELL)]], colWidths=[W])
    tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor(edge)),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return tb
def table(rows, widths):
    t = Table([[P(str(c), CELLB if r == 0 else CELL) for c in row] for r, row in enumerate(rows)], colWidths=widths)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CFE8DA"))]))
    return t
N = "Wake-Board-Shell_"
def step(n, title, lines, pic, maxh=5.0 * inch):
    f = [P(f"Step {n}.&nbsp;&nbsp;{title}", H2)] + [P(f"<b>{i + 1}.</b>&nbsp;&nbsp;{t}", STEP) for i, t in enumerate(lines)]
    return [KeepTogether(f + [Spacer(1, 6), img(pic, maxh)]), PageBreak()]

s = [P("GMX BC-250 Wake Board - 3D-printed shell (Rev 1)", H1),
     P("For the <b>GMX BC-250 Wake Board PCB Rev 1.1</b> (the board with 4 corner screw holes). "
       "It does not fit PCB Rev 1.0, which has no screw holes. Grumblymanx Mods."),
     box("<b>Not test-printed yet.</b> The shell was checked in 3D against a model of the fitted board "
         "(sockets, Pico, screw heads, SW1, wires): nothing touches. Print the Base and the Blank lid first as a fit test."),
     Spacer(1, 6), img(N + "Assembled_GMX-Mods.png", 3.3 * inch),
     P("What to print", H2),
     table([["File (STL folder)", "How many", "Notes"],
            ["Wake-Board-Shell_Base.stl", "1", "Floor down on the bed, as the file is laid out"],
            ["Wake-Board-Shell_Button.stl", "1", "Prints shaft-down (as laid out). No supports needed"],
            ["Wake-Board-Shell_Lid_...stl", "1 (pick one)", "GMX-Mods, Bazzite, BC-250 or Blank. Prints top-down (as laid out)"]],
           [2.6 * inch, 1.1 * inch, W - 3.7 * inch]),
     Spacer(1, 6),
     P("Print settings: PLA or PETG, 0.2 mm layers, 3 walls, 20% infill, <b>no supports</b>. Size: 75.3 x 47.8 x 25.0 mm assembled."),
     P("You also need", H2),
     table([["Part", "Qty", "Why"],
            ["M3 x 6 mm pan-head screw", "4", "Holds the board to the base (screws straight into the printed posts)"]],
           [2.6 * inch, 0.7 * inch, W - 3.3 * inch]),
     PageBreak()]
s += step(1, "Screw the board into the base",
          ["The board is finished: parts soldered, Pico plugged in, the six outside wires soldered to J3-J8.",
           "Lay the board in the base with the <b>wire pads toward the wall that has the long slot</b> and the Pico's USB end at the end with the opening.",
           "Put an M3 x 6 mm screw through each corner hole (H1-H4) into the post below. Tighten gently - the posts are plastic."],
          N + "Base_with_board.png")
s += step(2, "Lead the wires out of the slot",
          ["Bend each wire up from its pad and out through the long slot in the back wall.",
           "Keep the wires low, under the top edge of the slot opening (5.5 mm tall)."],
          N + "Wire_slot.png")
s += step(3, "Put the button into the lid",
          ["Turn the lid upside down (as in the picture).",
           "Drop the orange button into the round tube, <b>thin end first</b>. The thin end pokes out of the top of the lid."],
          N + "Lid_underside.png")
s += step(4, "Close the shell",
          ["Hold the lid upside down with the button in it, then turn it over onto the base in one move.",
           "The cut-out corner of the lid goes over the USB end.",
           "Push the lid straight down until both long sides click. To open, pull the long sides of the base outward a little and lift the lid."],
          N + "Exploded.png")
s += step(5, "Using it",
          ["<b>LEARN</b> button = SW1 on the board: hold 5-10 s to teach a controller, over 10 s to forget all; short press switches the PC on.",
           "<b>BOOT</b> hole: press the Pico's BOOTSEL button with a pen tip (only needed when flashing new firmware).",
           "The small oval window shows the Pico's LED. The micro-USB cable plugs in at the end with the opening."],
          N + "Assembled_GMX-Mods.png", 4.6 * inch)

def footer(c, d):
    c.saveState(); c.setFont("DV", 9); c.setFillColor(colors.HexColor("#78909C"))
    c.drawString(0.6 * inch, 0.42 * inch, "GMX BC-250 Wake Board Shell Rev 1 - Grumblymanx Mods")
    c.drawRightString(letter[0] - 0.6 * inch, 0.42 * inch, f"Page {d.page}"); c.restoreState()

SimpleDocTemplate(outpdf, pagesize=letter, leftMargin=0.6 * inch, rightMargin=0.6 * inch, topMargin=0.55 * inch, bottomMargin=0.65 * inch,
                  title="GMX BC-250 Wake Board Shell Rev 1", author="Grumblymanx Mods").build(s, onFirstPage=footer, onLaterPages=footer)
print(outpdf)
