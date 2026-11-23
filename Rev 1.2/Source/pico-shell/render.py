import sys, os, numpy as np, trimesh, cadquery as cq
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import pico_shell as P
from raster import render

out, ren, picostep = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(ren, exist_ok=True)
tmp = "/tmp/pico_w.stl"
cq.exporters.export(cq.importers.importStep(picostep).translate((0, 0, P.PCB_BOT)), tmp, tolerance=0.02, angularTolerance=0.2)
pico = trimesh.load(tmp)
def stepmesh(path):
    t = "/tmp/_r.stl"; cq.exporters.export(cq.importers.importStep(path), t, tolerance=0.01, angularTolerance=0.1); return trimesh.load(t)
base = stepmesh(os.path.join(out, "STEP", "Pico-Shell_Base.step"))
NAMES = ("GMX-Mods", "Bazzite", "BC-250", "Blank")
lids = {n: stepmesh(os.path.join(out, "STEP", f"Pico-Shell_Lid_{n}.step")) for n in NAMES}
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
FONT_S = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

SHELL = (0.30, 0.32, 0.36); LIDC = (0.22, 0.47, 0.85); PCB = (0.12, 0.55, 0.25)


def cam_from(fwd, up=(0, 0, 1)):
    f = np.asarray(fwd, float); f /= np.linalg.norm(f)
    r = np.cross(up, f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    return r, u, f


TOP = ((0, 1, 0), (-1, 0, 0), (0, 0, 1))          # USB end on the right, looking straight down
ISO = cam_from((0.60, -0.35, 0.70))                # from the front, above (text reads upright)
UNDER = cam_from((0.45, -0.35, -0.75))
SIDE = cam_from((1, 0, 0.05))                      # looking at a long side
END = cam_from((0, 1, 0.12))                       # looking at the USB end


def save(meshes, cam, fname, title, sub=None, W=1400, H=900):
    im = render(meshes, W=W, H=H, cam=cam)
    canvas = Image.new("RGB", (W, H + 110), "white")
    canvas.paste(im, (0, 110))
    d = ImageDraw.Draw(canvas)
    d.text((30, 18), title, fill=(20, 20, 20), font=FONT)
    if sub:
        d.text((30, 64), sub, fill=(70, 70, 70), font=FONT_S)
    canvas.save(os.path.join(ren, fname))


def moved(m, dz):
    c = m.copy(); c.apply_translation((0, 0, dz)); return c


for n, m in lids.items():
    save([(m, LIDC)], TOP, f"Lid_{n}_top.png", f"Lid - {n}", "Top view. USB end on the RIGHT. Round hole = BOOTSEL, small oval = LED window.", H=700)
save([(lids["Blank"], LIDC)], UNDER, "Lid_underside.png", "Lid - underside",
     "Press posts (fit over the base pegs) and snap bumps on the end skirts. This side faces UP on the print bed.")
save([(base, SHELL)], ISO, "Base_3D.png", "Base (same base for all 4 versions)", "Floor, 4 pegs, low side rails (wire slots above them), end walls with snap grooves.")
save([(base, SHELL), (pico, PCB)], ISO, "Base_with_Pico.png", "Pico W / Pico 2 W placed on the base", "Mounting holes drop over the 4 pegs. USB end goes into the notched end wall.")
save([(base, SHELL), (pico, PCB), (moved(lids["GMX-Mods"], 12), LIDC)], ISO, "Exploded.png", "Exploded view", "Lid presses straight down until both ends click.", H=1000)
for n, m in lids.items():
    save([(base, SHELL), (pico, PCB), (m, LIDC)], ISO, f"Assembled_{n}.png", f"Assembled - {n}")
save([(base, SHELL), (pico, PCB), (lids["Blank"], LIDC)], SIDE, "Side_wire_slot.png", "Side view - wire slot",
     "The open gap along each long side lines up with the Pico's edge pads, so wires exit sideways.", H=500)
save([(base, SHELL), (pico, PCB), (lids["Blank"], LIDC)], END, "USB_end.png", "USB end", "Opening for a micro-USB cable (flashing firmware without opening the shell).", W=900, H=600)
print("renders done")
