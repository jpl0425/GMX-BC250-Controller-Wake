#!/usr/bin/env python3
"""Gerbers, drill, BOM, JLC BOM, CPL, ibom for the GMX BC-250 Wake Board."""
import os, subprocess, csv, shutil, zipfile, glob, pcbnew

REV = "1.0"; NAME = "GMX-BC250-Wake-Board"
SRC = "/home/claude/pcb/out"
PCB = f"{SRC}/{NAME}_Rev{REV}.kicad_pcb"
PKG = f"/home/claude/pcbpkg/{NAME}_Rev{REV}_Complete"
shutil.rmtree(PKG, ignore_errors=True)
for d in ["Gerbers", "BOM", "JLC_BOM", "CPL", "ibom", "Renders", "Source", "Docs"]:
    os.makedirs(f"{PKG}/{d}", exist_ok=True)
os.environ["INTERACTIVE_HTML_BOM_NO_DISPLAY"] = "1"
def run(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(1)

# ---------- parts (one place, used by every output) ----------
PARTS = {  # ref: (value, manufacturer, mpn, lcsc, assembly, note)
 "Q1": ("BSS138LT1G", "onsemi", "BSS138LT1G", "C82045", "SMT", "Presses the BC-250 power button"),
 "Q2": ("BSS138LT1G", "onsemi", "BSS138LT1G", "C82045", "SMT", "Option B only: switches the PSU on (PS_ON)"),
 "R1": ("10k", "YAGEO", "RC0603FR-0710KL", "C98220", "SMT", "Q1 gate pull-down"),
 "R2": ("10k", "YAGEO", "RC0603FR-0710KL", "C98220", "SMT", "Option B only: Q2 gate pull-down"),
 "R3": ("1k", "YAGEO", "RC0603FR-071KL", "C22548", "SMT", "Protects the Pico input (PC ON)"),
 "D1": ("1N5819WS", "Guangdong Hottech", "1N5819WS", "C191023", "SMT", "+5VSB to Pico VSYS"),
 "SW1": ("TS-1187A-B-A-B", "XKB Connection", "TS-1187A-B-A-B", "C318884", "SMT", "Learn / manual on-off button"),
 "J1": ("Female socket 1x20 2.54mm", "ZHOURI", "PM2.54-1*20", "C5224030", "Hand solder", "Pico pins 1-20. Alternative: BOOMELE 2.54-1*20P, C50984"),
 "J2": ("Female socket 1x20 2.54mm", "ZHOURI", "PM2.54-1*20", "C5224030", "Hand solder", "Pico pins 21-40. Alternative: BOOMELE 2.54-1*20P, C50984"),
}
WIRE = {"J3": "GND", "J4": "PC ON", "J5": "PS_ON (Option B only)", "J6": "PWR BTN", "J7": "GND", "J8": "+5VSB"}

b = pcbnew.LoadBoard(PCB)
fps = {f.GetReference(): f for f in b.GetFootprints()}
# --- cross-check: every PCB part is in PARTS/WIRE, and nothing extra ---
pcb_refs = {r for r in fps if not r.startswith("LOGO")}
assert pcb_refs == set(PARTS) | set(WIRE), (pcb_refs ^ (set(PARTS) | set(WIRE)))

# ---------- Gerbers + drill ----------
g = f"{SRC}/gerb"; shutil.rmtree(g, ignore_errors=True); os.makedirs(g)
run("kicad-cli", "pcb", "export", "gerbers", "-o", g + "/", "--layers",
    "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts", "--subtract-soldermask", PCB)
run("kicad-cli", "pcb", "export", "drill", "-o", g + "/", "--format", "excellon", "--excellon-separate-th",
    "--generate-map", "--map-format", "pdf", PCB)
gz = f"{PKG}/Gerbers/{NAME}_Rev{REV}_Gerber.zip"
with zipfile.ZipFile(gz, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(glob.glob(g + "/*")):
        if not f.endswith(".pdf"): z.write(f, os.path.basename(f))

# ---------- full BOM ----------
with open(f"{PKG}/BOM/{NAME}_Rev{REV}_BOM_full.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Ref", "Value", "Manufacturer part", "Footprint on PCB", "LCSC #", "Side", "Assembly", "Note"])
    for r in sorted(PARTS, key=lambda r: (r.rstrip("0123456789"), int(r.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))):
        v, man, mpn, lcsc, asm, note = PARTS[r]
        w.writerow([r, v, f"{man} {mpn}", str(fps[r].GetFPID().GetLibItemName()), lcsc, "Top", asm, note])
    for r, lab in WIRE.items():
        w.writerow([r, "Wire pad", "(no part)", "WirePad_D2.2_Drill1.1", "", "Top", "None", f"Solder the outside wire here: {lab}"])
    w.writerow(["(not on PCB)", "Raspberry Pi Pico W or Pico 2 W", "with male pin headers fitted", "", "", "", "Plug in", "Plugs into J1/J2, parts side up, USB end to the right"])

# ---------- JLC BOM (SMT parts only) ----------
groups = {}
for r, (v, man, mpn, lcsc, asm, note) in PARTS.items():
    if asm != "SMT": continue
    groups.setdefault((v, str(fps[r].GetFPID().GetLibItemName()), lcsc), []).append(r)
with open(f"{PKG}/JLC_BOM/{NAME}_Rev{REV}_BOM_JLC.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (v, fp, lcsc), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
        w.writerow([v, ",".join(sorted(refs)), fp, lcsc])

# ---------- CPL (SMT parts only, JLC format) ----------
pos = f"{SRC}/pos.csv"
run("kicad-cli", "pcb", "export", "pos", "-o", pos, "--format", "csv", "--units", "mm", "--side", "front", "--smd-only", PCB)
smt = {r for r, p in PARTS.items() if p[4] == "SMT"}
rows = list(csv.DictReader(open(pos)))
cpl_refs = set()
with open(f"{PKG}/CPL/{NAME}_Rev{REV}_CPL_JLC.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in rows:
        if r["Ref"] not in smt: continue
        cpl_refs.add(r["Ref"])
        w.writerow([r["Ref"], f'{float(r["PosX"]):.4f}mm', f'{float(r["PosY"]):.4f}mm', "Top", f'{float(r["Rot"]) % 360:.1f}'])
assert cpl_refs == smt, cpl_refs ^ smt

# ---------- ibom ----------
for r in PARTS:  # LCSC field on the board must match the BOM
    assert fps[r].GetProperty("LCSC") == PARTS[r][3], (r, fps[r].GetProperty("LCSC"))
ib = f"{SRC}/ibom_src.kicad_pcb"; b.Save(ib)
run("generate_interactive_bom", ib, "--no-browser", "--dest-dir", f"{PKG}/ibom",
    "--name-format", f"{NAME}_Rev{REV}_ibom", "--extra-fields", "LCSC", "--dark-mode",
    "--blacklist", "LOGO*", "--include-tracks", "--include-nets")

# ---------- Source ----------
for f in [PCB, PCB.replace(".kicad_pcb", ".kicad_pro"), f"{SRC}/fp-lib-table"]:
    shutil.copy(f, f"{PKG}/Source/")
shutil.copytree(f"{SRC}/lib", f"{PKG}/Source/lib")
os.makedirs(f"{PKG}/Source/scripts", exist_ok=True)
for f in ["make_board.py", "make_outputs.py", "drc.py", "render_board.py", "wiring_diagram.py", "cross_check.py"]:
    shutil.copy(f"/home/claude/pcb/{f}", f"{PKG}/Source/scripts/")
print("ok", PKG)
