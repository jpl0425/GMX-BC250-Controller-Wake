#!/usr/bin/env python3
"""Realistic renders of the GMX BC-250 Wake Board from the real KiCad layers."""
import subprocess, io, os, math, sys, pcbnew
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REV = "1.0"; NAME = "GMX-BC250-Wake-Board"
PCB = f"/home/claude/pcb/out/{NAME}_Rev{REV}.kicad_pcb"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/pcb/renders"
os.makedirs(OUT, exist_ok=True)
S = 40.0                       # px per mm
VBW, VBH = 58.0898, 43.0784    # kicad-cli "board area" page
OFFX, OFFY = (VBW - 58.0) / 2, (VBH - 43.0) / 2
W, H = round(VBW * S), round(VBH * S)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def layer(names, mirror=False, drill=2):
    a = ["kicad-cli", "pcb", "export", "svg", "--page-size-mode", "2", "--black-and-white",
         "--exclude-drawing-sheet", "--drill-shape-opt", str(drill), "-l", names, "-o", "/tmp/_l.svg", PCB]
    if mirror: a.insert(4, "--mirror")
    subprocess.run(a, check=True, capture_output=True)
    png = subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), "-b", "white", "/tmp/_l.svg"],
                         check=True, capture_output=True).stdout
    g = np.asarray(Image.open(io.BytesIO(png)).convert("L"), dtype=np.float32) / 255.0
    return 1.0 - g             # 1 = drawn

def col(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)

def bare(side):
    m = side == "back"; s = "B" if m else "F"
    cu = layer(f"{s}.Cu", m); cu0 = layer(f"{s}.Cu", m, 0)
    holes = np.clip(cu0 - cu, 0, 1)
    mask_open = layer(f"{s}.Mask", m)
    silk = layer(f"{s}.SilkS", m) * (1 - mask_open)
    img = np.zeros((H, W, 3), np.float32) + col("#17552c")            # solder mask over bare FR4
    img = img * (1 - cu[..., None]) + col("#23733c") * cu[..., None]  # copper under mask (lighter)
    # copper edges catch light a little
    edge = np.asarray(Image.fromarray((cu * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES), np.float32) / 255
    img += col("#3c9a58") * 0.35 * edge[..., None]
    pad = mask_open * (1 - holes)
    yy, xx = np.mgrid[0:H, 0:W]
    shine = 0.88 + 0.12 * np.sin((xx + yy) / 37.0)
    img = img * (1 - pad[..., None]) + (col("#d4d6d2") * shine[..., None]) * pad[..., None]  # HASL
    img = img * (1 - silk[..., None]) + col("#f4f4ef") * silk[..., None]
    img = img * (1 - holes[..., None]) + col("#20201e") * holes[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

b = pcbnew.LoadBoard(PCB)
def px(x, y):  # board mm (KiCad absolute) -> image px, front view
    return ((x - 100.0 + OFFX) * S, (y - 100.0 + OFFY) * S)
FP = {}
for f in b.GetFootprints():
    p = f.GetPosition(); FP[f.GetReference()] = (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), f.GetOrientationDegrees())

def body(d, cx, cy, w, h, rot, fill, r=0.15, outline=None):
    """Rotated rectangle in mm, centred on (cx,cy) board coords."""
    a = math.radians(-rot); pts = []
    for (x, y) in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        pts.append(px(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    d.polygon(pts, fill=fill, outline=outline)

def shadow(base, draw_fn, off=(0.35, 0.45), blur=5):
    sh = Image.new("L", base.size, 0); draw_fn(ImageDraw.Draw(sh), 255)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    dark = Image.new("RGB", base.size, (0, 0, 0))
    base.paste(dark, (round(off[0] * S), round(off[1] * S)), sh.point(lambda v: v * 0.55))

def text(d, x, y, s, size, fill, rot=0, img=None):
    f = ImageFont.truetype(FONT, round(size * S))
    if rot == 0:
        X, Y = px(x, y); d.text((X, Y), s, font=f, fill=fill, anchor="mm")
    else:
        t = Image.new("RGBA", (round(len(s) * size * S), round(size * S * 1.6)), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((t.width / 2, t.height / 2), s, font=f, fill=fill, anchor="mm")
        t = t.rotate(rot, expand=True); X, Y = px(x, y)
        img.paste(t, (round(X - t.width / 2), round(Y - t.height / 2)), t)

def parts(img, with_pico, omit=()):
    d = ImageDraw.Draw(img)
    smd = [(r, FP[r]) for r in ("Q1", "Q2", "R1", "R2", "R3", "D1", "SW1") if r not in omit]
    def outlines(dd, v):
        for r, (x, y, rot) in smd:
            w, h = {"Q": (2.9, 1.3), "R": (1.6, 0.8), "D": (1.8, 1.3), "S": (5.1, 5.1)}[r[0]]
            if r[0] == "Q": w, h = 1.3, 2.9; w, h = (h, w) if rot % 180 else (w, h)
            body(dd, x, y, w, h, 0 if r[0] == "Q" else rot, v)
    shadow(img, outlines, (0.15, 0.2), 3)
    d = ImageDraw.Draw(img)
    for r, (x, y, rot) in smd:
        if r[0] == "Q":   # SOT-23: legs then body
            for lx, ly in [(-0.95, 1.1), (0.95, 1.1), (0, -1.1)]:      # rot 270: G,S bottom; D top
                body(d, x + lx, y + ly, 0.42, 0.75, 0, (205, 207, 203))
            body(d, x, y, 2.9, 1.3, 0, (28, 28, 30)); body(d, x, y - 0.1, 2.6, 0.9, 0, (40, 40, 43))
        elif r[0] == "R":
            body(d, x, y, 1.6, 0.85, rot, (196, 198, 194))
            body(d, x, y, 1.0, 0.85, rot, (22, 22, 24))
        elif r[0] == "D":  # cathode band on pad 1 side (right, rot 180)
            body(d, x - 1.15, y, 0.6, 0.35, 0, (200, 200, 196)); body(d, x + 1.15, y, 0.6, 0.35, 0, (200, 200, 196))
            body(d, x, y, 1.75, 1.3, 0, (25, 25, 27)); body(d, x + 0.55, y, 0.3, 1.3, 0, (170, 170, 170))
        else:  # tactile switch
            for lx, ly in [(-3.0, -1.85), (3.0, -1.85), (-3.0, 1.85), (3.0, 1.85)]:
                body(d, x + lx, y + ly, 1.2, 0.6, 0, (200, 200, 196))
            body(d, x, y, 5.1, 5.1, 0, (190, 192, 190)); body(d, x, y, 4.6, 4.6, 0, (160, 162, 160))
            X, Y = px(x, y); R = 1.3 * S
            d.ellipse([X - R, Y - R, X + R, Y + R], fill=(30, 30, 32), outline=(70, 70, 75), width=3)
    # sockets
    for r in ("J1", "J2"):
        x, y, rot = FP[r]
        def so(dd, v, x=x, y=y): body(dd, x, y, 50.8, 2.54, 0, v)
        shadow(img, so, (0.5, 0.7), 6); d = ImageDraw.Draw(img)
        body(d, x, y, 50.8, 2.54, 0, (24, 24, 26))
        for i in range(20):
            hx = x - 24.13 + i * 2.54; X, Y = px(hx, y); R = 0.45 * S
            body(d, hx, y, 1.0, 1.0, 0, (12, 12, 12)); d.ellipse([X - R * 0.5, Y - R * 0.5, X + R * 0.5, Y + R * 0.5], fill=(150, 125, 60))
            if i: d.line([px(hx - 1.27, y - 1.27), px(hx - 1.27, y + 1.27)], fill=(40, 40, 44), width=2)
    if with_pico: pico(img)

def pico(img):
    x1, y1 = FP["J1"][0], FP["J1"][1]; y2 = FP["J2"][1]
    cx, cy = x1, (y1 + y2) / 2
    def so(dd, v): body(dd, cx, cy, 51.0, 21.0, 0, v)
    shadow(img, so, (1.2, 1.6), 14); d = ImageDraw.Draw(img)
    body(d, cx, cy, 51.0, 21.0, 0, (31, 110, 64)); body(d, cx, cy, 50.4, 20.4, 0, (36, 124, 72))
    for i in range(20):  # castellated pads, both rows
        for yy in (y1, y2):
            hx = cx - 24.13 + i * 2.54; X, Y = px(hx, yy); R = 0.8 * S
            d.ellipse([X - R, Y - R, X + R, Y + R], fill=(214, 186, 92)); r2 = 0.5 * S
            d.ellipse([X - r2, Y - r2, X + r2, Y + r2], fill=(110, 92, 40))
    # USB at the right end, overhanging slightly
    body(d, cx + 24.6, cy, 5.6, 8.0, 0, (190, 192, 196)); body(d, cx + 25.6, cy, 3.4, 7.2, 0, (150, 152, 156))
    # RP2040 / RP2350
    body(d, cx + 6.0, cy, 7.0, 7.0, 0, (30, 30, 33)); text(d, cx + 6.0, cy, "RP", 1.2, (120, 120, 120))
    # radio module can
    body(d, cx - 11.0, cy - 0.5, 10.5, 11.0, 0, (198, 200, 202)); body(d, cx - 11.0, cy - 0.5, 9.7, 10.2, 0, (214, 216, 218))
    # BOOTSEL button
    body(d, cx + 16.0, cy + 4.2, 3.5, 4.2, 0, (220, 220, 220)); X, Y = px(cx + 16.0, cy + 4.2); R = 0.9 * S
    d.ellipse([X - R, Y - R, X + R, Y + R], fill=(248, 248, 248), outline=(180, 180, 180), width=2)
    text(d, cx + 16.0, cy + 7.4, "BOOTSEL", 0.75, (240, 240, 240))
    text(d, cx - 2.0, cy + 7.6, "Pico W / Pico 2 W", 1.0, (240, 240, 240))
    # pin 1 mark on the Pico (pin 1 = USB end, top row)
    X, Y = px(cx + 24.13, y1 + 1.6); d.text((X, Y), "1", font=ImageFont.truetype(FONT, round(0.9 * S)), fill=(255, 255, 255), anchor="mm")

def frame(img, title):
    pad = 70
    out = Image.new("RGB", (img.width + 2 * pad, img.height + 2 * pad + 60), (245, 245, 242))
    sh = Image.new("L", out.size, 0); ImageDraw.Draw(sh).rectangle([pad + 12, pad + 16, pad + img.width + 12, pad + img.height + 16], fill=140)
    out.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 0.5))
    out.paste(img, (pad, pad))
    ImageDraw.Draw(out).text((out.width / 2, out.height - 45), title, font=ImageFont.truetype(FONT, 34), fill=(40, 40, 40), anchor="mm")
    return out

front = bare("front"); back = bare("back")
frame(front, f"{NAME} Rev {REV} - top, bare board").save(f"{OUT}/{NAME}_Rev{REV}_top_bare.png")
frame(back, f"{NAME} Rev {REV} - bottom, bare board").save(f"{OUT}/{NAME}_Rev{REV}_bottom.png")
a = front.copy(); parts(a, False)
frame(a, f"{NAME} Rev {REV} - top, parts fitted (Pico not plugged in)").save(f"{OUT}/{NAME}_Rev{REV}_top_parts.png")
a = front.copy(); parts(a, True)
frame(a, f"{NAME} Rev {REV} - top, Pico plugged in (parts side up, USB to the right)").save(f"{OUT}/{NAME}_Rev{REV}_top_with_Pico.png")
a = front.copy(); parts(a, False, ("Q2", "R2"))
frame(a, f"{NAME} Rev {REV} - Option A: parts fitted (Q2, R2 left off)").save(f"{OUT}/{NAME}_Rev{REV}_top_parts_OptionA.png")
a = front.copy(); parts(a, True, ("Q2", "R2"))
frame(a, f"{NAME} Rev {REV} - Option A: Pico plugged in").save(f"{OUT}/{NAME}_Rev{REV}_top_with_Pico_OptionA.png")
print("renders in", OUT)
