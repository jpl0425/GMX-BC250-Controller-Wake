"""Fit check: simple solid model of the populated Wake Board vs the shell parts."""
import sys, os, cadquery as cq, trimesh, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_shell as S
from board_shell import box, cyl, bxy

def board_model():
    m = box(-S.BL / 2, S.BL / 2, -S.BWID / 2, S.BWID / 2, S.PCB_BOT, S.PCB_TOP)
    for (x, y) in S.HOLES:
        m = m.cut(cyl(x, y, S.PCB_BOT - 1, S.PCB_TOP + 1, 3.2))
        m = m.union(cyl(x, y, S.PCB_TOP, S.PCB_TOP + 2.4, 5.6))            # M3 pan-head screw head
    pcx = S.PICO_C[0]
    for row_by in (22.0, 39.78):
        _, y = bxy(30.5, row_by)
        m = m.union(box(pcx - 25.4, pcx + 25.4, y - 1.27, y + 1.27, S.PCB_TOP, S.PCB_TOP + 8.5))         # socket
        m = m.union(box(pcx - 25.4, pcx + 25.4, y - 1.27, y + 1.27, S.PCB_TOP + 8.5, S.PCB_TOP + 11.0))  # header plastic
        m = m.union(box(pcx - 25.4, pcx + 25.4, y - 0.4, y + 0.4, S.PCB_BOT - 3.2, S.PCB_BOT))            # pins under board
    px, py = S.PICO_C
    z0 = S.PCB_TOP + 11.0
    m = m.union(box(px - 25.5, px + 25.5, py - 10.5, py + 10.5, z0, z0 + 1.0))                          # Pico PCB
    m = m.union(box(px + 21.5, px + 26.8, py - 4.0, py + 4.0, z0 + 1.0, z0 + 3.75))                     # micro-USB
    m = m.union(box(px - 16.0, px - 5.5, py - 6.0, py + 5.0, z0 + 1.0, z0 + 2.9))                       # radio can
    m = m.union(box(S.BOOT[0] - 1.75, S.BOOT[0] + 1.75, S.BOOT[1] - 2.1, S.BOOT[1] + 2.1, z0 + 1.0, z0 + 3.5))
    x, y = S.SW1
    m = m.union(box(x - 3.0, x + 3.0, y - 2.55, y + 2.55, S.PCB_TOP, S.PCB_TOP + 1.5))                  # SW1
    for bx in (8.0, 16.2, 24.4, 32.6, 40.8, 49.0):                                                       # wire stubs + joints
        wx, wy = bxy(bx, 4.8)
        m = m.union(cyl(wx, wy, S.PCB_BOT - 1.5, S.PCB_TOP + 3.0, 2.2))
        m = m.union(box(wx - 0.8, wx + 0.8, wy, S.IY - 0.3, S.PCB_TOP + 2.0, S.PCB_TOP + 3.6))           # wire to the slot
    return m

if __name__ == "__main__":
    base, button, lids = S.build(sys.argv[1])
    lid = lids["Blank"]
    bm = board_model().val()
    for name, part in (("Base", base), ("Lid", lid), ("Button", button)):
        print(f"board+Pico model vs {name:6s}: overlap {part.val().intersect(bm).Volume():8.4f} mm^3")
    print(f"Base vs Lid    overlap {base.val().intersect(lid.val()).Volume():.4f} mm^3")
    print(f"Base vs Button overlap {base.val().intersect(button.val()).Volume():.4f} mm^3")
    print(f"Lid vs Button  overlap {lid.val().intersect(button.val()).Volume():.4f} mm^3")
    # button must still clear the lid when pressed 0.5 mm, and must not touch SW1 top early
    pressed = button.translate((0, 0, -0.5))
    print(f"Lid vs Button pressed 0.5 mm overlap {lid.val().intersect(pressed.val()).Volume():.4f} mm^3")
    up = button.translate((0, 0, 1.2))
    print(f"Button lifted 1.2 mm vs Lid (should be >0 = it stops) {lid.val().intersect(up.val()).Volume():.4f} mm^3")
    print(f"Clearances: Pico top {S.PICO_TOP:.2f}, USB top {S.PCB_TOP + 14.75:.2f}, roof underside {S.ROOF_BOT:.2f}")
    print(f"Wire gap in +Y wall: z {S.SLOT_Z0:.1f} to {S.GAP_TOP:.1f} (= {S.GAP_TOP - S.SLOT_Z0:.1f} mm) x {S.SLOT_X[1] - S.SLOT_X[0]:.1f} mm wide")
    for f in sorted(glob.glob(os.path.join(sys.argv[2], "STL", "*.stl"))):
        t = trimesh.load(f); e = t.extents
        print(f"{os.path.basename(f):38s} watertight={t.is_watertight} {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm")
    cq.exporters.export(board_model(), "/tmp/board_model.stl", tolerance=0.02, angularTolerance=0.2)
