"""
GMX BC-250 Controller Wake - Pico W / Pico 2 W Shell  (Rev 1)
Grumblymanx Mods

CadQuery source. Builds one base (shared) and four lids:
  Lid_GMX-Mods (Grumbly logo), Lid_Bazzite, Lid_BC-250, Lid_Blank

Board coordinates (mm), board centred at X=0, Y=0, looking at the
component side with the micro-USB end at +Y:
  PCB 21 x 51 x 1.0, mounting holes 2.1 at (+/-5.7, +/-23.5)
  micro-USB overhangs the top edge by 1.3 (to Y=26.8), top at 2.75 above PCB
  BOOTSEL button centre (-3.5, 13.5), top 2.5 above PCB
  User LED centre (-5.7, 20.7)
Source of these numbers: Raspberry Pi Pico W / Pico 2 W datasheet Figure 3
(outline, holes, pin pitch) and the Ki-Lime Pi Pico W STEP model (parts).

Usage:  python3 pico_shell.py <logo.svg> <out_dir>
"""
import sys, os
import cadquery as cq
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

# ---------------- main dimensions ----------------
CLR      = 0.30          # side clearance board -> wall
WALL     = 1.6
FLOOR    = 1.6
ROOF     = 1.6
IX, IY   = 10.5 + CLR, 25.5 + CLR          # inner half sizes 10.8 x 25.8
OX, OY   = IX + WALL, IY + WALL             # outer half sizes of base 12.4 x 27.4
STAND    = 1.2                               # standoff height under PCB
PCB_BOT  = FLOOR + STAND                     # 2.8
PCB_TOP  = PCB_BOT + 1.0                     # 3.8
ROOF_BOT = PCB_TOP + 2.75 + 0.45             # 7.0  (USB top + 0.45 clearance)
ROOF_TOP = ROOF_BOT + ROOF                   # 8.6
RAIL_TOP = 2.4                               # base side wall height (bottom of wire slot)
LIDWALL_BOT = 5.6                            # lid side wall bottom (top of wire slot)
HOLES    = [(sx*5.7, sy*23.5) for sx in (-1, 1) for sy in (-1, 1)]

# snap fit (skirts on lid ends hook into grooves on base end walls)
SK_GAP, SK_T = 0.15, 1.0      # long thin skirts so they flex without cracking (~1% strain)
SK_BOT   = 0.6
GROOVE_Z = (1.4, 2.7)
GROOVE_D = 0.55
BUMP     = 0.45               # 0.30 mm snap interference

# openings
USB_HW   = 5.75          # half width of USB plug notch (fits ~11 mm wide plug)
BOOT     = (-3.5, 13.5, 4.0)       # x, y, hole diameter
LED      = (-5.7, 20.7, 3.4, 2.6)  # x, y, width(x), length(y) of oval window
ENGRAVE  = 0.6
LOGO_THICKEN = 0.12
TEXT_Y0, TEXT_Y1 = -24.0, 10.5     # usable lid strip for text/logo (along Y)
TEXT_W   = 2 * IX - 1.0            # usable width (across X)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


# ---------------- BASE ----------------
def make_base():
    b = box(-OX, OX, -OY, OY, 0, FLOOR)                       # floor
    for s in (-1, 1):                                          # low side rails
        b = b.union(box(s * IX if s > 0 else -OX, OX if s > 0 else -IX, -IY, IY, 0, RAIL_TOP))
        # full height end walls
        y0, y1 = (IY, OY) if s > 0 else (-OY, -IY)
        b = b.union(box(-OX, OX, y0, y1, 0, ROOF_BOT))
    for (x, y) in HOLES:                                       # standoffs + locating pegs
        b = b.union(cyl(x, y, FLOOR - 0.01, PCB_BOT, 3.4))
        b = b.union(cyl(x, y, PCB_BOT - 0.01, PCB_TOP + 0.6, 1.8))
    # snap grooves on the outer face of both end walls
    for s in (-1, 1):
        yo = s * OY
        g = box(-OX - 1, OX + 1, yo - GROOVE_D if s > 0 else yo, yo if s > 0 else yo + GROOVE_D, *GROOVE_Z)
        b = b.cut(g)
    # micro-USB notch through the +Y end wall
    b = b.cut(box(-USB_HW, USB_HW, IY - 0.5, OY + 1, FLOOR, ROOF_BOT + 1))
    # small chamfer-ish lead-in on the end wall tops is provided by the lid bump ramp
    return b


# ---------------- LID ----------------
def bump_strip(x0, x1, s):
    """Ramp bump on the inside face of a skirt. s=+1 for +Y end."""
    yi = s * (OY + SK_GAP)                        # skirt inner face
    zr0, zr1, zc = GROOVE_Z[0] + 0.1, GROOVE_Z[1] - 0.35, GROOVE_Z[1] - 0.2
    # profile in (y,z): lead-in ramp from the bottom, short flat, small top slope (lets you pry it off)
    pts = [(yi, zr0), (yi - s * BUMP, zr1), (yi - s * BUMP, zc), (yi, zc + 0.15)]
    w = cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0).translate((x0, 0, 0))
    return w


def make_lid_body():
    yl = OY + SK_GAP + SK_T
    lid = box(-OX, OX, -yl, yl, ROOF_BOT, ROOF_TOP)            # roof
    for s in (-1, 1):                                          # side walls over the wire slots
        x0, x1 = (IX, OX) if s > 0 else (-OX, -IX)
        lid = lid.union(box(x0, x1, -IY, IY, LIDWALL_BOT, ROOF_BOT + 0.01))
        # end skirts
        y0, y1 = (OY + SK_GAP, yl) if s > 0 else (-yl, -OY - SK_GAP)
        lid = lid.union(box(-OX, OX, y0, y1, SK_BOT, ROOF_BOT + 0.01))
    # snap bumps: -Y end one long bump, +Y end two bumps beside the USB notch
    lid = lid.union(bump_strip(-OX + 1.5, OX - 1.5, -1))
    for (a, c) in ((-OX + 1.0, -USB_HW - 0.6), (USB_HW + 0.6, OX - 1.0)):
        lid = lid.union(bump_strip(a, c, 1))
    # press posts with recesses that fit over the locating pegs
    for (x, y) in HOLES:
        lid = lid.union(cyl(x, y, PCB_TOP + 0.1, ROOF_BOT + 0.01, 3.0))
        lid = lid.cut(cyl(x, y, PCB_TOP + 0.05, PCB_TOP + 0.6 + 0.35, 2.3))
    # USB notch: skirt + roof beyond Y=26.0 so a cable plug body can reach the connector
    lid = lid.cut(box(-USB_HW, USB_HW, 26.0, yl + 1, SK_BOT - 1, ROOF_TOP + 1))
    # BOOTSEL hole
    lid = lid.cut(cyl(BOOT[0], BOOT[1], ROOF_BOT - 1, ROOF_TOP + 1, BOOT[2]))
    # LED window (oval / slot)
    x, y, w, l = LED
    led = (cq.Workplane("XY").slot2D(w, l, angle=0).extrude(ROOF + 2)
           .translate((x, y, ROOF_BOT - 1)))
    lid = lid.cut(led)
    return lid


# ---------------- artwork ----------------
def shapely_to_cq(geom, z0, depth):
    """Extrude shapely (Multi)Polygon into a CadQuery solid from z0 up by depth."""
    polys = [geom] if isinstance(geom, Polygon) else list(geom.geoms)
    solid = None
    for p in polys:
        p = p.simplify(0.01)
        if p.area < 0.01:
            continue
        wp = cq.Workplane("XY").polyline(list(p.exterior.coords)[:-1]).close()
        s = wp.extrude(depth)
        for h in p.interiors:
            hs = cq.Workplane("XY").polyline(list(h.coords)[:-1]).close().extrude(depth)
            s = s.cut(hs)
        s = s.translate((0, 0, z0))
        solid = s if solid is None else solid.union(s)
    return solid


def logo_geometry(svg_path):
    """Read the potrace SVG and return a shapely MultiPolygon in mm (Y up)."""
    from svgelements import SVG, Path
    svg = SVG.parse(svg_path)
    rings = []
    for el in svg.elements():
        if isinstance(el, Path):
            for sub in el.as_subpaths():
                sp = Path(sub)
                L = sp.length(error=1e-3)
                n = max(16, int(L / 0.05))
                pts = [sp.point(i / n) for i in range(n)]
                pts = [(p.x, -p.y) for p in pts]          # flip SVG Y
                if len(pts) >= 3:
                    rings.append(Polygon(pts).buffer(0))
    # even-odd fill: XOR all rings
    geom = None
    for r in rings:
        geom = r if geom is None else geom.symmetric_difference(r)
    return geom


def fit_to_strip(geom):
    """Rotate so it reads along the lid's length (+Y, USB end = right side of text) and scale to fit."""
    g = affinity.rotate(geom, 90, origin=(0, 0))          # text now runs along +Y
    minx, miny, maxx, maxy = g.bounds
    sx = TEXT_W / (maxx - minx)
    sy = (TEXT_Y1 - TEXT_Y0) / (maxy - miny)
    k = min(sx, sy)
    g = affinity.scale(g, k, k, origin=(0, 0))
    minx, miny, maxx, maxy = g.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    return affinity.translate(g, -cx, (TEXT_Y0 + TEXT_Y1) / 2 - cy), k


def text_geometry(txt, font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max_h=8.5):
    """Make text outline with CadQuery, convert to shapely, fit to strip."""
    t = cq.Workplane("XY").text(txt, 10, 1, fontPath=font, halign="center", valign="center")
    face_polys = []
    for f in t.faces("<Z").vals():
        ow = f.outerWire()
        opts = [ow.positionAt(i / 400.0) for i in range(400)]
        inner = []
        for iw in f.innerWires():
            ip = [iw.positionAt(i / 200.0) for i in range(200)]
            inner.append([(p.x, p.y) for p in ip])
        face_polys.append(Polygon([(p.x, p.y) for p in opts], inner).buffer(0))
    g = unary_union(face_polys)
    g, k = fit_to_strip(g)
    # limit letter height (across the lid) to max_h
    minx, miny, maxx, maxy = g.bounds
    if (maxx - minx) > max_h:
        kk = max_h / (maxx - minx)
        g = affinity.scale(g, kk, kk, origin=((minx + maxx) / 2, (miny + maxy) / 2))
    return g


def engrave(lid, geom):
    # mirror nothing: viewer looks at roof top (+Z). Text must read correctly from above.
    cutter = shapely_to_cq(geom, ROOF_TOP - ENGRAVE, ENGRAVE + 1)
    return lid.cut(cutter)


def main():
    svg, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    base = make_base()
    lid0 = make_lid_body()
    # Artwork reads left-to-right when the shell is viewed from the top with the USB end on the right.
    lids = {"Blank": lid0}
    logo = logo_geometry(svg)
    for name, geom in (("GMX-Mods", logo),):
        g, _ = fit_to_strip(geom)
        # The logo's thinnest lines come out ~0.4 mm at this size, too fine for a
        # 0.4 mm nozzle. Widen every line by 0.12 mm per side (~0.64 mm) so it prints.
        g = g.buffer(LOGO_THICKEN, join_style=1)
        lids[name] = engrave(lid0, g)
    for name, txt in (("Bazzite", "Bazzite"), ("BC-250", "BC-250")):
        g = text_geometry(txt)
        lids[name] = engrave(lid0, g)
    return base, lids


def print_ready(part, flip):
    """Lay the part flat for printing: base as-is, lid flipped roof-down."""
    if flip:
        part = part.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = part.val().BoundingBox()
    return part.translate((0, 0, -bb.zmin))


if __name__ == "__main__":
    base, lids = main()
    out = sys.argv[2]
    step_dir, stl_dir = os.path.join(out, "STEP"), os.path.join(out, "STL")
    os.makedirs(step_dir, exist_ok=True); os.makedirs(stl_dir, exist_ok=True)
    # STEP = assembled orientation (for CAD). STL = print-ready orientation (for the slicer).
    cq.exporters.export(base, os.path.join(step_dir, "Pico-Shell_Base.step"))
    cq.exporters.export(print_ready(base, False), os.path.join(stl_dir, "Pico-Shell_Base.stl"), tolerance=0.01, angularTolerance=0.1)
    for n, l in lids.items():
        cq.exporters.export(l, os.path.join(step_dir, f"Pico-Shell_Lid_{n}.step"))
        cq.exporters.export(print_ready(l, True), os.path.join(stl_dir, f"Pico-Shell_Lid_{n}.stl"), tolerance=0.01, angularTolerance=0.1)
    print("done")
