#!/usr/bin/env python3
"""Readable wiring diagrams (one per option) for the GMX BC-250 Wake Board.
Rule: every word must be readable without zooming when the picture fills a page width."""
import sys, pcbnew
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/pcb/renders"
PCB = "/home/claude/pcb/out/GMX-BC250-Wake-Board_Rev1.1.kicad_pcb"
BF = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; NF = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def F(s, bold=True): return ImageFont.truetype(BF if bold else NF, s)

PURPLE, BLACK, GREEN, ORANGE, YELLOW, GREY = (142, 68, 173), (30, 30, 30), (39, 174, 96), (243, 136, 28), (230, 180, 0), (150, 150, 150)
b = pcbnew.LoadBoard(PCB)
padx = {f.GetReference(): pcbnew.ToMM(f.GetPosition().x) - 100.0 for f in b.GetFootprints()}

def make(option):
    A = option == "A"
    rows = [  # pad, name, colour, destination
        ("J3", "GND", BLACK, "BC-250 ground pad"),
        ("J4", "PC ON", YELLOW, "BC-250 TPMS1 pin 9"),
        ("J5", "PS_ON", GREY if A else GREEN, "NOT USED - leave empty" if A else "ATX GREEN wire (pin 16)"),
        ("J6", "PWR BTN", ORANGE, "BC-250 power-button pad"),
        ("J7", "GND", BLACK, "ATX BLACK wire (pin 15)"),
        ("J8", "+5VSB", PURPLE, "ATX PURPLE wire (pin 9)"),
    ]
    W, H = 1900, 1500
    c = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(c)
    d.text((W / 2, 50), f"GMX BC-250 Wake Board - wiring, OPTION {option}", font=F(56), fill=(20, 20, 20), anchor="mm")
    d.text((W / 2, 112), "power supply always ON" if A else "the Pico switches the power supply",
           font=F(38, False), fill=(60, 60, 60), anchor="mm")
    name = "top_with_Pico_OptionA" if A else "top_with_Pico"
    im = Image.open(f"/home/claude/pcb/renders/GMX-BC250-Wake-Board_Rev1.1_{name}.png").convert("RGB")
    im = im.crop((70, 70, im.width - 70, im.height - 130))
    BW = 1000; s = BW / im.width; im = im.resize((BW, round(im.height * s)))
    bx, by = 40, H - im.height - 150
    c.paste(im, (bx, by))
    import subprocess, re as _re
    subprocess.run(["kicad-cli", "pcb", "export", "svg", "--page-size-mode", "2", "--exclude-drawing-sheet", "-l", "Edge.Cuts",
                    "-o", "/tmp/_e.svg", PCB], check=True, capture_output=True)
    vbw = float(_re.search(r'width="([\d.]+)mm"', open("/tmp/_e.svg").read(600)).group(1))
    bb = b.GetBoardEdgesBoundingBox(); bw = pcbnew.ToMM(bb.GetWidth()); x0 = pcbnew.ToMM(bb.GetX()) - 100.0
    mm = BW / vbw; offx = (vbw - bw) / 2 - x0
    lanes = [200 + i * 92 for i in range(6)]
    for i, (ref, nm, col, dest) in enumerate(rows):
        px = bx + (padx[ref] + offx) * mm; py = by + (4.8 + 0.039) * mm
        ly = lanes[i]
        unused = A and ref == "J5"
        if not unused:
            pts = [(px, py), (px, ly), (1060, ly)]
            d.line(pts, fill=(0, 0, 0), width=17, joint="curve")
            d.line(pts, fill=col if col != BLACK else (60, 60, 60), width=11, joint="curve")
            r = 17; d.ellipse([px - r, py - r, px + r, py + r], outline=(255, 200, 0), width=6)
        x0, y0, x1, y1 = d.textbbox((px, py + 48), ref, font=F(30), anchor="mm")
        d.rounded_rectangle([x0 - 8, y0 - 6, x1 + 8, y1 + 6], radius=8, fill=(255, 255, 255), outline=(20, 20, 20), width=3)
        d.text((px, py + 48), ref, font=F(30), fill=(20, 20, 20), anchor="mm")
        bx0, bx1 = 1060, W - 30
        d.rounded_rectangle([bx0, ly - 40, bx1, ly + 40], radius=12, fill=(255, 255, 255), outline=col, width=6)
        d.text((bx0 + 20, ly), f"{ref} {nm}", font=F(34), fill=(20, 20, 20), anchor="lm")
        d.text((bx0 + 290, ly), "->  " + dest, font=F(30, not unused), fill=(110, 110, 110) if unused else (20, 20, 20), anchor="lm")
    foot = ("Option A: at the ATX extension cable, link GREEN (pin 16) to BLACK (pin 15)." if A else
            "Option B: do NOT link green to black. Q2 and R2 must be fitted.")
    d.rectangle([0, H - 130, W, H], fill=(255, 243, 205))
    d.text((W / 2, H - 88), foot, font=F(36), fill=(120, 60, 0), anchor="mm")
    d.text((W / 2, H - 38), "Unplug the power supply from the wall before soldering any wire.", font=F(32, False), fill=(40, 40, 40), anchor="mm")
    p = f"{OUT}/GMX-BC250-Wake-Board_Rev1.1_Wiring_Option{option}.png"
    c.save(p); print(p)

make("A"); make("B")
