"""Pictures of the Wake Board Shell. Big, readable titles (no zooming needed)."""
import sys, os, numpy as np, trimesh, cadquery as cq
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_shell as S
from board_shell import box, cyl, bxy
from raster import render

svg, ren = sys.argv[1], sys.argv[2]
os.makedirs(ren, exist_ok=True)
base, button, lids = S.build(svg)

def mesh(wp):
    t = "/tmp/_m.stl"; cq.exporters.export(wp, t, tolerance=0.02, angularTolerance=0.2); return trimesh.load(t)

# simple coloured model of the fitted board
pcb = box(-S.BL / 2, S.BL / 2, -S.BWID / 2, S.BWID / 2, S.PCB_BOT, S.PCB_TOP)
for (x, y) in S.HOLES:
    pcb = pcb.cut(cyl(x, y, S.PCB_BOT - 1, S.PCB_TOP + 1, 3.2))
dark = None
px, py = S.PICO_C
for row_by in (22.0, 39.78):
    _, y = bxy(30.5, row_by)
    s = box(px - 25.4, px + 25.4, y - 1.27, y + 1.27, S.PCB_TOP, S.PCB_TOP + 11.0)
    dark = s if dark is None else dark.union(s)
heads = None
for (x, y) in S.HOLES:
    h = cyl(x, y, S.PCB_TOP, S.PCB_TOP + 2.4, 5.6); heads = h if heads is None else heads.union(h)
z0 = S.PCB_TOP + 11.0
pico = box(px - 25.5, px + 25.5, py - 10.5, py + 10.5, z0, z0 + 1.0)
metal = box(px + 21.5, px + 26.8, py - 4.0, py + 4.0, z0 + 1.0, z0 + 3.75).union(box(px - 16.0, px - 5.5, py - 6.0, py + 5.0, z0 + 1.0, z0 + 2.9)).union(heads)
x, y = S.SW1
sw = box(x - 2.55, x + 2.55, y - 2.55, y + 2.55, S.PCB_TOP, S.PCB_TOP + 1.5)
BOARD = [(mesh(pcb), (0.10, 0.45, 0.22)), (mesh(dark), (0.10, 0.10, 0.11)), (mesh(pico), (0.15, 0.55, 0.30)),
         (mesh(metal), (0.75, 0.76, 0.78)), (mesh(sw), (0.70, 0.70, 0.70))]
WCOL = [(0.12, 0.12, 0.12), (0.95, 0.75, 0.05), (0.15, 0.68, 0.38), (0.95, 0.53, 0.11), (0.12, 0.12, 0.12), (0.56, 0.27, 0.68)]
WIRES = []
for i, bx in enumerate((8.0, 16.2, 24.4, 32.6, 40.8, 49.0)):
    wx, wy = bxy(bx, 4.8); zc = S.PCB_TOP + 4.5
    w = cyl(wx, wy, S.PCB_TOP, zc + 0.8, 1.6).union(
        cq.Workplane("XZ").circle(0.8).extrude(-(S.OY + 10 - wy)).translate((wx, wy, zc)))
    WIRES.append((mesh(w), WCOL[i]))
BOARD += WIRES
BASE = (mesh(base), (0.30, 0.32, 0.36))
BTN = (mesh(button), (0.95, 0.55, 0.10))
L = {n: mesh(l) for n, l in lids.items()}
LIDC = (0.22, 0.47, 0.85)

def cam_from(fwd, up=(0, 0, 1)):
    f = np.asarray(fwd, float); f /= np.linalg.norm(f)
    r = np.cross(up, f); r /= np.linalg.norm(r); u = np.cross(f, r); return r, u, f
TOP = ((1, 0, 0), (0, 1, 0), (0, 0, 1))          # looking straight down, USB end on the right, wire slot at the top
ISO = cam_from((0.35, -0.75, 0.65))              # from the front-right, above
BACK = cam_from((-0.25, 0.85, 0.5))              # from the wire-slot side
UNDER = cam_from((0.3, -0.6, -0.75))
END = cam_from((1, -0.15, 0.25))                 # looking at the USB end
F1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
F2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)

def moved(m, dz):
    c = m[0].copy(); c.apply_translation((0, 0, dz)); return (c, m[1])

def save(meshes, cam, fname, title, sub=None, W=1600, H=1000):
    im = render(meshes, W=W, H=H, cam=cam)
    top = 150 if sub else 90
    c = Image.new("RGB", (W, H + top), "white"); c.paste(im, (0, top)); d = ImageDraw.Draw(c)
    d.text((40, 22), title, fill=(20, 20, 20), font=F1)
    if sub:
        d.text((40, 90), sub, fill=(60, 60, 60), font=F2)
    c.save(os.path.join(ren, f"Wake-Board-Shell_{fname}"))

for n in lids:
    save([(L[n], LIDC)], TOP, f"Lid_{n}_top.png", f"Lid - {n}", "Top view. USB end on the right. Wire slot at the top.", H=760)
save([(L["Blank"], LIDC)], UNDER, "Lid_underside.png", "Lid - underside", "Guide tube for the button. This side faces UP when printing.")
save([BASE], ISO, "Base.png", "Base", "4 screw posts (M3). Wire slot at the back, USB opening at the right end.")
save([BASE] + BOARD, ISO, "Base_with_board.png", "Board screwed into the base", "4 x M3 screws through the board corners into the posts.")
save([BASE] + BOARD + [moved(BTN, 14), moved((L["GMX-Mods"], LIDC), 14)], ISO, "Exploded.png",
     "Exploded view", "Button (orange) sits in the lid's guide tube. Lid pushes straight down and clicks.", H=1150)
for n in lids:
    save([BASE] + BOARD + [BTN, (L[n], LIDC)], ISO, f"Assembled_{n}.png", f"Assembled - {n} lid")
save([BASE] + BOARD + [BTN, (L["Blank"], LIDC)], BACK, "Wire_slot.png", "Wire slot", "The 6 wires leave through this slot (5.5 mm tall).")
save([BASE] + BOARD + [BTN, (L["Blank"], LIDC)], END, "USB_end.png", "USB end", "Micro-USB cable plugs in here to re-flash the Pico.", W=1300, H=900)
save([BTN], cam_from((0.6, -0.6, 0.3)), "Button.png", "Button (prints shaft-down)", "Wide end rests on SW1. The shaft sticks out of the lid.", W=900, H=900)
print("renders done")
