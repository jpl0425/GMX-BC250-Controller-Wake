import sys, cadquery as cq, trimesh, glob, os
sys.path.insert(0, os.path.dirname(__file__))
import pico_shell as P

pico = cq.importers.importStep(sys.argv[1]).translate((0, 0, P.PCB_BOT))
out = sys.argv[2]
base = cq.importers.importStep(os.path.join(out, "STEP", "Pico-Shell_Base.step"))
lid = cq.importers.importStep(os.path.join(out, "STEP", "Pico-Shell_Lid_Blank.step"))
pv = pico.val()
for name, part in (("Base", base), ("Lid", lid)):
    inter = part.val().intersect(pv)
    print(f"Pico W model vs {name}: overlap volume = {inter.Volume():.4f} mm^3")
print(f"Base vs Lid overlap = {base.val().intersect(lid.val()).Volume():.4f} mm^3")
# vertical gap checks
pb = pv.BoundingBox()
print(f"Pico model z top {pb.zmax:.2f}, lid roof underside {P.ROOF_BOT:.2f}, clearance {P.ROOF_BOT-pb.zmax:.2f}")
print(f"Pico model y range {pb.ymin:.2f}..{pb.ymax:.2f}; base inner wall at +/-{P.IY}")
for f in sorted(glob.glob(os.path.join(out, "STL", "*.stl"))):
    m = trimesh.load(f)
    e = m.extents
    print(f"{os.path.basename(f):22s} watertight={m.is_watertight} size={e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f} mm vol={m.volume:.0f}")
