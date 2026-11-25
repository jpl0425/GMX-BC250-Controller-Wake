#!/usr/bin/env python3
"""Automated cross-check: PCB vs BOM vs JLC BOM vs CPL vs ibom vs Gerber drill file."""
import csv, glob, re, json, zipfile, pcbnew, lzstring, sys
PKG = glob.glob("/home/claude/pcbpkg/GMX-BC250-Wake-Board_Rev*_Complete")[0]
b = pcbnew.LoadBoard(glob.glob(PKG + "/Source/*.kicad_pcb")[0])
fails = []; lines = []
def check(name, ok, detail=""):
    lines.append(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    if not ok: fails.append(name)

fps = {f.GetReference(): f for f in b.GetFootprints() if not f.GetReference().startswith("LOGO")}
bom = {r["Ref"]: r for r in csv.DictReader(open(glob.glob(PKG + "/BOM/*.csv")[0])) if r["Ref"] != "(not on PCB)"}
jlc = list(csv.DictReader(open(glob.glob(PKG + "/JLC_BOM/*.csv")[0])))
cpl = {r["Designator"]: r for r in csv.DictReader(open(glob.glob(PKG + "/CPL/*.csv")[0]))}
h = open(glob.glob(PKG + "/ibom/*.html")[0]).read()
ib = json.loads(lzstring.LZString().decompressFromBase64(re.search(r'decompressFromBase64\("([^"]+)"\)', h).group(1)))

check("Every PCB footprint is in the full BOM, and nothing extra", set(fps) == set(bom), f"{len(fps)} refs")
for r, row in bom.items():
    f = fps[r]
    if row["LCSC #"]:
        check(f"{r}: LCSC # on PCB = BOM", f.GetProperty("LCSC") == row["LCSC #"], row["LCSC #"])
    check(f"{r}: footprint on PCB = BOM", str(f.GetFPID().GetLibItemName()) == row["Footprint on PCB"], row["Footprint on PCB"])
smt = {r for r, row in bom.items() if row["Assembly"] == "SMT"}
jlc_refs = {}
for row in jlc:
    for r in row["Designator"].split(","): jlc_refs[r] = row
check("JLC BOM holds exactly the SMT parts", set(jlc_refs) == smt, ",".join(sorted(smt)))
for r in smt:
    j = jlc_refs[r]
    check(f"{r}: JLC BOM LCSC/footprint = full BOM", j["LCSC Part #"] == bom[r]["LCSC #"] and j["Footprint"] == bom[r]["Footprint on PCB"])
check("CPL holds exactly the SMT parts", set(cpl) == smt)
for r in smt:
    p = fps[r].GetPosition(); x, y = pcbnew.ToMM(p.x), -pcbnew.ToMM(p.y)
    c = cpl[r]; cx, cy = float(c["Mid X"][:-2]), float(c["Mid Y"][:-2])
    rot = fps[r].GetOrientationDegrees() % 360
    check(f"{r}: CPL position/rotation = PCB", abs(cx - x) < 0.01 and abs(cy - y) < 0.01 and abs(float(c["Rotation"]) - rot) < 0.1,
          f"{cx:.2f},{cy:.2f} rot {c['Rotation']}")
ib_refs = {r for grp in ib["bom"]["both"] for r, _ in grp}
check("ibom lists every BOM part (wire pads excluded)", ib_refs == {r for r, row in bom.items() if row["LCSC #"]})
fields = ib["bom"]["fields"]
for grp in ib["bom"]["both"]:
    for r, i in grp:
        v = fields[str(i)] if isinstance(fields, dict) else fields[i]
        check(f"{r}: ibom LCSC = BOM", v[-1] == bom[r]["LCSC #"], v[-1])
# drill file: count plated holes
z = zipfile.ZipFile(glob.glob(PKG + "/Gerbers/*.zip")[0])
drl = z.read([n for n in z.namelist() if n.endswith("-PTH.drl")][0]).decode()
hits = len(re.findall(r"^X[-\d.]+Y[-\d.]+", drl, re.M))
pth = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH)
vias = sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA")
check("Drill file hole count = PCB pads + vias", hits == pth + vias, f"{hits} holes = {pth} pads + {vias} vias")
need = ["F_Cu", "B_Cu", "F_Mask", "B_Mask", "F_Silkscreen", "B_Silkscreen", "Edge_Cuts", "F_Paste"]
check("Gerber zip has every layer JLCPCB needs", all(any(n in x for x in z.namelist()) for n in need))
print("\n".join(lines)); print(f"\n{len(lines) - len(fails)} passed, {len(fails)} failed")
open("/home/claude/pcb/cross_check.txt", "w").write("\n".join(lines) + f"\n\n{len(lines) - len(fails)} passed, {len(fails)} failed\n")
sys.exit(1 if fails else 0)
