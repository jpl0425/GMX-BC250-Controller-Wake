"""
GMX BC-250 Wake Board Shell  (Rev 1)  -  for GMX BC-250 Wake Board PCB Rev 1.1
Grumblymanx Mods.  CadQuery source.

Parts: one Base, one Button (plunger for SW1), four Lids (GMX-Mods, Bazzite, BC-250, Blank).

Shell coordinates (mm): board centred at X=0, Y=0. +X = Pico USB end, +Y = wire-pad edge, Z up.
Board coordinate (bx, by) from the KiCad file maps to X = bx - 29.25, Y = 21.5 - by.

Heights used (above the PCB top face):
  female socket 8.5 (ZHOURI PM2.54-1*20, H8.5) + Pico male-header plastic 2.5 + Pico PCB 1.0
  -> Pico top 12.0, micro-USB top 14.75, BOOTSEL top 14.5, SW1 (TS-1187A-B-A-B) top 1.5
Usage: python3 board_shell.py <logo.svg> <out_dir>
"""
import sys, os
import cadquery as cq
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

# ---------------- board ----------------
BL, BWID, BT = 70.5, 43.0, 1.6           # PCB length (X), width (Y), thickness
def bxy(bx, by): return (bx - 29.25, 21.5 - by)
HOLES = [bxy(-2.5, 3.5), bxy(61.0, 3.5), bxy(-2.5, 39.5), bxy(61.0, 39.5)]
SW1 = bxy(8.5, 14.0)
PICO_C = bxy(30.5, 30.89)                 # Pico centre
BOOT = (PICO_C[0] + 13.5, PICO_C[1] + 3.5)   # see docstring mapping (pin-1 side = +Y)
LED = (PICO_C[0] + 20.7, PICO_C[1] + 5.7)
WIRE_X = (bxy(8.0, 0)[0], bxy(49.0, 0)[0])    # J3 .. J8

# ---------------- shell sizes ----------------
CLR, WALL, FLOOR, ROOF = 0.40, 2.0, 2.0, 1.8
IX, IY = BL / 2 + CLR, BWID / 2 + CLR          # 35.65, 21.9
OX, OY = IX + WALL, IY + WALL
STAND = 4.0                                     # room under the board for pins and solder joints
PCB_BOT = FLOOR + STAND                         # 6.0
PCB_TOP = PCB_BOT + BT                          # 7.6
PICO_TOP = PCB_TOP + 12.0
ROOF_BOT = PCB_TOP + 14.75 + 0.85               # 23.2
ROOF_TOP = ROOF_BOT + ROOF                      # 25.0

POST_D, PILOT_D = 6.5, 2.5                      # M3 screw straight into the printed post
LIP_T, LIP_H, LIP_GAP = 1.4, 5.0, 0.20          # lid lip that plugs inside the walls
BUMP, GROOVE_D = 0.45, 0.55                     # snap: 0.25 mm interference
SNAP_Z = (ROOF_BOT - 3.6, ROOF_BOT - 2.4)

# wire slot in the +Y wall (lid tongue closes the top part)
SLOT_X = (WIRE_X[0] - 4.0, WIRE_X[1] + 4.0)
SLOT_Z0 = PCB_TOP + 1.0                         # 8.6
GAP_TOP = SLOT_Z0 + 5.5                         # wire gap 5.5 mm tall
# micro-USB plug opening at the +X end
USB_Y, USB_HW = PICO_C[1], 6.0
USB_Z0 = PCB_TOP + 13.4 - 5.0
USB_ROOF_X = PICO_C[0] + 25.5                   # roof cut-out starts at the Pico's USB end
# SW1 button
SW_TOP = PCB_TOP + 1.5
BTN_HOLE, BTN_SHAFT = 4.6, 4.0
TUBE_OD, TUBE_LEN = 7.6, 5.0
ENGRAVE, LOGO_THICKEN = 0.6, 0.12
ART = (-28.0, 20.0, -21.5, -10.5)              # x0, x1, y0, y1 band for logo / name on the roof (clear of holes)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


# ---------------- BASE ----------------
def make_base():
    b = box(-OX, OX, -OY, OY, 0, ROOF_BOT).cut(box(-IX, IX, -IY, IY, FLOOR, ROOF_BOT + 1))
    for (x, y) in HOLES:
        b = b.union(cyl(x, y, FLOOR - 0.01, PCB_BOT, POST_D))
        b = b.cut(cyl(x, y, FLOOR - 1.0, PCB_BOT + 0.1, PILOT_D))
    # wire slot, open to the top (the lid tongue fills the upper part)
    b = b.cut(box(SLOT_X[0], SLOT_X[1], IY - 0.5, OY + 1, SLOT_Z0, ROOF_BOT + 1))
    # USB opening, open to the top
    b = b.cut(box(IX - 0.5, OX + 1, USB_Y - USB_HW, USB_Y + USB_HW, USB_Z0, ROOF_BOT + 1))
    # snap grooves on the inside of the long walls
    for s in (-1, 1):
        yw = s * IY
        y0, y1 = (yw - 0.01, yw + GROOVE_D) if s > 0 else (yw - GROOVE_D, yw + 0.01)
        for (a, c) in groove_spans(s):
            b = b.cut(box(a, c, y0, y1, SNAP_Z[0] - 0.3, SNAP_Z[1] + 0.3))
    return b


def groove_spans(s):
    if s < 0:
        return [(-30.0, 30.0)]
    return [(-IX + 1.5, SLOT_X[0] - 1.5), (SLOT_X[1] + 1.5, IX - 1.5)]


# ---------------- LID ----------------
def make_lid_body():
    lid = box(-OX, OX, -OY, OY, ROOF_BOT, ROOF_TOP)
    ox, oy = IX - LIP_GAP, IY - LIP_GAP
    lip = box(-ox, ox, -oy, oy, ROOF_BOT - LIP_H, ROOF_BOT + 0.01).cut(
        box(-ox + LIP_T, ox - LIP_T, -oy + LIP_T, oy - LIP_T, ROOF_BOT - LIP_H - 1, ROOF_BOT + 1))
    lid = lid.union(lip)
    # tongue that closes the top of the wire slot, leaving the wire gap below it
    lid = lid.union(box(SLOT_X[0] + 0.25, SLOT_X[1] - 0.25, oy - 0.01, OY, GAP_TOP, ROOF_BOT + 0.01))
    # snap bumps on the lip (long sides)
    for s in (-1, 1):
        for (a, c) in groove_spans(s):
            a, c = a + 1.0, c - 1.0
            yf = s * oy
            pts = [(yf, SNAP_Z[0] - 0.2), (yf + s * BUMP, SNAP_Z[0] + 0.5), (yf + s * BUMP, SNAP_Z[1]), (yf, SNAP_Z[1] + 0.35)]
            lid = lid.union(cq.Workplane("YZ").polyline(pts).close().extrude(c - a).translate((a, 0, 0)))
    # USB plug clearance: lip, roof and tongue cut away over the USB end
    lid = lid.cut(box(USB_ROOF_X, OX + 1, USB_Y - USB_HW, USB_Y + USB_HW, ROOF_BOT - LIP_H - 1, ROOF_TOP + 1))
    # SW1 button: hole through the roof + guide tube underneath
    x, y = SW1
    lid = lid.union(cyl(x, y, ROOF_BOT - TUBE_LEN, ROOF_BOT + 0.01, TUBE_OD))
    lid = lid.cut(cyl(x, y, ROOF_BOT - TUBE_LEN - 1, ROOF_TOP + 1, BTN_HOLE))
    # BOOTSEL hole (press with a pen) and LED window
    lid = lid.cut(cyl(BOOT[0], BOOT[1], ROOF_BOT - 1, ROOF_TOP + 1, 4.0))
    lid = lid.cut(cq.Workplane("XY").slot2D(3.4, 2.6, angle=0).extrude(ROOF + 2).translate((LED[0], LED[1], ROOF_BOT - 1)))
    # small engraved labels next to the button and the BOOTSEL hole
    for txt, (tx, ty) in (("LEARN", (SW1[0], SW1[1] - 6.2)), ("BOOT", (BOOT[0] - 8.6, BOOT[1]))):
        t = cq.Workplane("XY").text(txt, 3.2, ENGRAVE + 1, fontPath=FONTB, halign="center", valign="center")
        lid = lid.cut(t.translate((tx, ty, ROOF_TOP - ENGRAVE)))
    return lid


# ---------------- BUTTON (plunger) ----------------
def make_button():
    """Rests on SW1. Wide body + cone stop it coming out through the roof; shaft sticks up 1.5 mm."""
    x, y = SW1
    z_tip = SW_TOP
    z_body0, z_body1 = z_tip + 1.8, z_tip + 7.0
    z_cone1 = z_body1 + (6.8 - BTN_SHAFT) / 2          # 45 degree cone
    z_top = ROOF_TOP + 1.5
    p = cyl(x, y, z_tip, z_body0 + 0.01, 3.0)
    p = p.union(cyl(x, y, z_body0, z_body1 + 0.01, 6.8))
    p = p.union(cq.Workplane("XY").circle(3.4).workplane(offset=z_cone1 - z_body1).circle(BTN_SHAFT / 2).loft()
                .translate((x, y, z_body1)))
    p = p.union(cyl(x, y, z_cone1 - 0.01, z_top, BTN_SHAFT))
    return p


# ---------------- artwork ----------------
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def shapely_to_cq(geom, z0, depth):
    polys = [geom] if isinstance(geom, Polygon) else list(geom.geoms)
    solid = None
    for p in polys:
        p = p.simplify(0.01)
        if p.area < 0.01:
            continue
        s = cq.Workplane("XY").polyline(list(p.exterior.coords)[:-1]).close().extrude(depth)
        for h in p.interiors:
            s = s.cut(cq.Workplane("XY").polyline(list(h.coords)[:-1]).close().extrude(depth))
        s = s.translate((0, 0, z0))
        solid = s if solid is None else solid.union(s)
    return solid


def logo_geometry(svg_path):
    from svgelements import SVG, Path
    rings = []
    for el in SVG.parse(svg_path).elements():
        if isinstance(el, Path):
            for sub in el.as_subpaths():
                sp = Path(sub); L = sp.length(error=1e-3); n = max(16, int(L / 0.05))
                pts = [(q.x, -q.y) for q in (sp.point(i / n) for i in range(n))]
                if len(pts) >= 3:
                    rings.append(Polygon(pts).buffer(0))
    geom = None
    for r in rings:
        geom = r if geom is None else geom.symmetric_difference(r)
    return geom


def text_geometry(txt):
    t = cq.Workplane("XY").text(txt, 10, 1, fontPath=FONTB, halign="center", valign="center")
    polys = []
    for f in t.faces("<Z").vals():
        ow = f.outerWire(); opts = [ow.positionAt(i / 400.0) for i in range(400)]
        inner = [[(q.x, q.y) for q in (iw.positionAt(i / 200.0) for i in range(200))] for iw in f.innerWires()]
        polys.append(Polygon([(q.x, q.y) for q in opts], inner).buffer(0))
    return unary_union(polys)


def fit_to_box(g, max_h=None):
    x0, x1, y0, y1 = ART
    minx, miny, maxx, maxy = g.bounds
    k = min((x1 - x0) / (maxx - minx), (y1 - y0) / (maxy - miny))
    if max_h:
        k = min(k, max_h / (maxy - miny))
    g = affinity.scale(g, k, k, origin=(0, 0))
    minx, miny, maxx, maxy = g.bounds
    return affinity.translate(g, (x0 + x1) / 2 - (minx + maxx) / 2, (y0 + y1) / 2 - (miny + maxy) / 2)


def engrave(lid, g):
    return lid.cut(shapely_to_cq(g, ROOF_TOP - ENGRAVE, ENGRAVE + 1))


def build(svg):
    base, button, lid0 = make_base(), make_button(), make_lid_body()
    lids = {"Blank": lid0}
    lids["GMX-Mods"] = engrave(lid0, fit_to_box(logo_geometry(svg)).buffer(LOGO_THICKEN, join_style=1))
    for name in ("Bazzite", "BC-250"):
        lids[name] = engrave(lid0, fit_to_box(text_geometry(name), max_h=9.0))
    return base, button, lids


def print_ready(part, flip):
    if flip:
        part = part.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = part.val().BoundingBox()
    return part.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


if __name__ == "__main__":
    svg, out = sys.argv[1], sys.argv[2]
    base, button, lids = build(svg)
    sd, ld = os.path.join(out, "STEP"), os.path.join(out, "STL")
    os.makedirs(sd, exist_ok=True); os.makedirs(ld, exist_ok=True)
    N = "Wake-Board-Shell"
    def exp(part, name, flip):
        cq.exporters.export(part, os.path.join(sd, f"{N}_{name}.step"))
        cq.exporters.export(print_ready(part, flip), os.path.join(ld, f"{N}_{name}.stl"), tolerance=0.01, angularTolerance=0.1)
    exp(base, "Base", False)
    exp(button, "Button", True)        # printed upside down: shaft tip on the bed, cone needs no support
    for n, l in lids.items():
        exp(l, f"Lid_{n}", True)
    print("done")
