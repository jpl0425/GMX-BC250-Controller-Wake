#!/usr/bin/env python3
"""GMX BC-250 Wake Board Rev 1.0 - builds the KiCad 7 PCB from scratch."""
import pcbnew, os, sys

REV = "1.1"
NAME = "GMX-BC250-Wake-Board"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/pcb/out"
os.makedirs(OUT, exist_ok=True)
LIB = "/home/claude/pcb/lib/easyeda.pretty"
LOGO_LIB = "/home/claude/pcb/lib/GMX_Logo.pretty"
OX, OY = 100.0, 100.0
W, H = 58.0, 43.0
X0, X1 = -6.0, 64.5          # Rev 1.1: board widened 6.0 mm left, 6.5 mm right for M3 holes

b = pcbnew.BOARD()
mm = pcbnew.FromMM
def P(x, y): return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

# ---- design rules (inside JLCPCB standard capability) ----
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = mm(0.15)
ds.m_MinClearance = mm(0.2)
ds.m_ViasMinSize = mm(0.5)
ds.m_MinThroughDrill = mm(0.3)
ds.m_CopperEdgeClearance = mm(0.4)
ds.m_SilkClearance = mm(0.15)
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.2)); nc.SetTrackWidth(mm(0.25)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
def net(n):
    if n not in nets:
        ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni
    return nets[n]
for n in ["GND", "+5VSB", "VSYS", "GP2_PWRBTN", "GP3_PSON", "GP4_SENSE", "GP5_SW", "PWR_BTN", "PS_ON", "PC_ON"]:
    net(n)

def place(lib, name, ref, x, y, rot=0, value="", back=False):
    fp = pcbnew.FootprintLoad(lib, name)
    fp.SetReference(ref); fp.SetValue(value or name)
    fp.SetFPID(pcbnew.LIB_ID("GMX_BC250", name))
    fp.Value().SetVisible(False)
    fp.SetPosition(P(x, y))
    if rot: fp.SetOrientationDegrees(rot)
    if back: fp.Flip(P(x, y), False)
    for g in list(fp.GraphicalItems()):       # drop sub-printable marks (<0.1 mm lines) and pin-1 dots on non-polar parts
        if g.GetClass() in ("FP_SHAPE", "MGRAPHIC") and g.GetLayer() == pcbnew.F_SilkS and g.GetShape() == pcbnew.SHAPE_T_CIRCLE and g.GetWidth() < mm(0.1):
            fp.Remove(g)
    b.Add(fp); return fp

def dot(x, y, r=0.22):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(P(x, y)); s.SetEnd(P(x + r / 2, y))
    s.SetWidth(mm(r)); s.SetLayer(pcbnew.F_SilkS); b.Add(s)

def pad(fp, num): return [p for p in fp.Pads() if p.GetNumber() == str(num)][0]
def setnet(fp, num, n): pad(fp, num).SetNet(net(n))
def pxy(fp, num):
    v = pad(fp, num).GetPosition(); return (pcbnew.ToMM(v.x) - OX, pcbnew.ToMM(v.y) - OY)

def ref_at(fp, x, y, size=0.8, rot=0):
    r = fp.Reference(); r.SetPosition(P(x, y)); r.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    r.SetTextThickness(mm(0.15)); r.SetTextAngleDegrees(rot); r.SetLayer(pcbnew.F_SilkS); r.SetVisible(True)

def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS, thick=0.15, mirror=False, bold=False):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(thick)); t.SetMirrored(mirror)
    b.Add(t); return t

def seg(pts, n, w=0.25, layer=pcbnew.F_Cu):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2))
        t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net(n)); b.Add(t)

def via(x, y, n="GND"):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetDrill(mm(0.3)); v.SetWidth(mm(0.6))
    v.SetNet(net(n)); b.Add(v)

def line(x1, y1, x2, y2, layer=pcbnew.F_SilkS, w=0.15):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)

# ---- board outline ----
for (x1, y1, x2, y2) in [(X0, 0, X1, 0), (X1, 0, X1, H), (X1, H, X0, H), (X0, H, X0, 0)]:
    line(x1, y1, x2, y2, pcbnew.Edge_Cuts, 0.1)

# ---- Pico W / Pico 2 W on two 1x20 female sockets ----
ROW1_Y, ROW2_Y = 22.0, 22.0 + 17.78
PIN1_X = 54.63                       # pin 1 at the USB end (USB points to the right edge)
def pico_x(pin):                    # board x of a Pico pin
    return PIN1_X - (pin - 1) * 2.54 if pin <= 20 else PIN1_X - (40 - pin) * 2.54
CX = (pico_x(1) + pico_x(20)) / 2
J1 = place(LIB, "HDR-TH_20P-P2.54-V-F", "J1", CX, ROW1_Y, 180, "Socket 1x20 (Pico pins 1-20)")
J2 = place(LIB, "HDR-TH_20P-P2.54-V-F", "J2", CX, ROW2_Y, 0, "Socket 1x20 (Pico pins 21-40)")
GND_PINS = {3, 8, 13, 18, 23, 28, 33, 38}
PICO_NET = {4: "GP2_PWRBTN", 5: "GP3_PSON", 6: "GP4_SENSE", 7: "GP5_SW", 39: "VSYS"}
for pin in range(1, 41):
    fp, num = (J1, pin) if pin <= 20 else (J2, pin - 20)
    n = "GND" if pin in GND_PINS else PICO_NET.get(pin)
    if n: setnet(fp, num, n)
    x, y = pxy(fp, num)
    assert abs(x - pico_x(pin)) < 0.01, (pin, x, pico_x(pin))
ref_at(J1, 2.2, ROW1_Y, 0.8, 90)
ref_at(J2, 2.2, ROW2_Y, 0.8, 90)

# ---- wire pads (outside wires) ----
PAD_Y = 4.8
WIRE = [("J3", "GND", 8.0, "GND"), ("J4", "PC_ON", 16.2, "PC ON"), ("J5", "PS_ON", 24.4, "PS_ON"),
        ("J6", "PWR_BTN", 32.6, "PWR BTN"), ("J7", "GND", 40.8, "GND"), ("J8", "+5VSB", 49.0, "+5VSB")]
WP = {}
for ref, n, x, label in WIRE:
    fp = pcbnew.FootprintLoad(LIB, "WirePad_D2.2_Drill1.1"); fp.SetReference(ref); fp.SetValue("Wire pad " + label)
    fp.SetFPID(pcbnew.LIB_ID("GMX_BC250", "WirePad_D2.2_Drill1.1")); p = pad(fp, 1)
    fp.SetPosition(P(x, PAD_Y)); b.Add(fp); p.SetNet(net(n)); fp.Value().SetVisible(False)
    ref_at(fp, x - 2.3, PAD_Y, 0.8, 90)
    text(label, x, 2.0, 1.0)
    WP[ref] = fp

# ---- M3 mounting holes (Rev 1.1) ----
HOLES = [("H1", -2.5, 3.5), ("H2", 61.0, 3.5), ("H3", -2.5, 39.5), ("H4", 61.0, 39.5)]
for ref, x, y in HOLES:
    h = place(LIB, "MountingHole_3.2mm_M3", ref, x, y, 0, "M3 mounting hole")
    ref_at(h, x, y + (4.3 if y < 20 else -4.3))

# ---- parts ----
Q1 = place(LIB, "SOT-23-3_L2.9-W1.6-P1.90-LS2.8-BR", "Q1", 32.6, 13.5, 270, "BSS138LT1G")
Q2 = place(LIB, "SOT-23-3_L2.9-W1.6-P1.90-LS2.8-BR", "Q2", 24.4, 13.5, 270, "BSS138LT1G")
R1 = place(LIB, "R0603", "R1", 29.9, 14.0, 90, "10k")
R2 = place(LIB, "R0603", "R2", 21.7, 14.0, 90, "10k")
R3 = place(LIB, "R0603", "R3", 16.2, 13.0, 90, "1k")
D1 = place(LIB, "SOD-323_L1.8-W1.3-LS2.5-RD", "D1", 54.0, PAD_Y, 180, "1N5819WS")
SW1 = place(LIB, "SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL_H1.5", "SW1", 8.5, 14.0, 0, "TS-1187A-B-A-B")

# nets on parts. BSS138: 1=G 2=S 3=D. 1N5819WS: 1=K 2=A.
for q, g, d in [(Q1, "GP2_PWRBTN", "PWR_BTN"), (Q2, "GP3_PSON", "PS_ON")]:
    setnet(q, 1, g); setnet(q, 2, "GND"); setnet(q, 3, d)
setnet(R1, 1, "GP2_PWRBTN"); setnet(R1, 2, "GND")
setnet(R2, 1, "GP3_PSON");   setnet(R2, 2, "GND")
setnet(R3, 1, "GP4_SENSE");  setnet(R3, 2, "PC_ON")
setnet(D1, 1, "VSYS"); setnet(D1, 2, "+5VSB")
# SW1: use diagonal pads 1 and 4 - always on opposite sides of the switch contact,
# whichever pad pairs are joined inside. Pads 2 and 3 are left without a net (mechanical only).
setnet(SW1, 1, "GND"); setnet(SW1, 4, "GP5_SW")

print("pads:", {r: [(pad(f, n).GetNumber(), pxy(f, n)) for n in (1, 2, 3)]
                for r, f in [("Q1", Q1), ("Q2", Q2)]})
print("R1", pxy(R1, 1), pxy(R1, 2), "R3", pxy(R3, 1), pxy(R3, 2), "D1", pxy(D1, 1), pxy(D1, 2),
      "SW1", [pxy(SW1, n) for n in (1, 2, 3, 4)])

LCSC = {"Q1": "C82045", "Q2": "C82045", "R1": "C98220", "R2": "C98220", "R3": "C22548",
        "D1": "C191023", "SW1": "C318884", "J1": "C5224030", "J2": "C5224030"}
for f in (Q1, Q2, R1, R2, R3, D1, SW1, J1, J2):
    f.SetProperty("LCSC", LCSC[f.GetReference()])

# ---- routing (top copper) ----
q1g, q1s, q1d = pxy(Q1, 1), pxy(Q1, 2), pxy(Q1, 3)
q2g, q2s, q2d = pxy(Q2, 1), pxy(Q2, 2), pxy(Q2, 3)
# Pico GPIO lanes: the pin closest to the left uses the lane nearest the Pico, so nothing crosses.
gp2, gp3, gp4, gp5 = (pico_x(p) for p in (4, 5, 6, 7))
seg([(gp2, ROW1_Y), (gp2, 17.2), (q1g[0], 17.2), q1g], "GP2_PWRBTN")
seg([(gp3, ROW1_Y), (gp3, 18.2), (q2g[0], 18.2), q2g], "GP3_PSON")
seg([(gp4, ROW1_Y), (gp4, 19.2), (pxy(R3, 1)[0], 19.2), pxy(R3, 1)], "GP4_SENSE")
sw4 = pxy(SW1, 4)
seg([(gp5, ROW1_Y), (gp5, 20.2), (sw4[0], 20.2), sw4], "GP5_SW")
# gate pull-downs
seg([q1g, (pxy(R1, 1)[0], q1g[1]), pxy(R1, 1)], "GP2_PWRBTN")
seg([q2g, (pxy(R2, 1)[0], q2g[1]), pxy(R2, 1)], "GP3_PSON")
# outputs straight up to their wire pads
seg([q1d, (32.6, PAD_Y)], "PWR_BTN", 0.4)
seg([q2d, (24.4, PAD_Y)], "PS_ON", 0.4)
seg([pxy(R3, 2), (16.2, PAD_Y)], "PC_ON")
# +5VSB -> D1 -> VSYS (Pico pin 39), down the right edge and under the bottom row
seg([(49.0, PAD_Y), pxy(D1, 2)], "+5VSB", 0.5)
d1k = pxy(D1, 1)
p39 = pico_x(39)
seg([d1k, (57.0, PAD_Y), (57.0, 42.1), (p39, 42.1), (p39, ROW2_Y)], "VSYS", 0.5)
# GND stitching next to each ground pad
for (x, y) in [(q1s[0], 16.1), (q2s[0], 16.1)]:
    via(x, y)
seg([q1s, (q1s[0], 16.1)], "GND", 0.4); seg([q2s, (q2s[0], 16.1)], "GND", 0.4)
for r in (R1, R2):
    x, y = pxy(r, 2); via(x, y - 1.3); seg([(x, y), (x, y - 1.3)], "GND", 0.4)
x, y = pxy(SW1, 1); via(x, y - 1.8); seg([(x, y), (x, y - 1.8)], "GND", 0.4)

# ---- ground pours, both layers ----
def zone(layer):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net("GND"))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
    ol = z.Outline(); ol.NewOutline()
    for (x, y) in [(X0 + 0.5, 0.5), (X1 - 0.5, 0.5), (X1 - 0.5, H - 0.5), (X0 + 0.5, H - 0.5)]:
        ol.Append(mm(OX + x), mm(OY + y))
    b.Add(z); return z
zone(pcbnew.F_Cu); zone(pcbnew.B_Cu)
for (x, y) in [(3.0, 25.8), (12, 25.8), (22, 25.8), (32, 25.8), (42, 25.8), (3.0, 37.8), (12, 37.8), (22, 37.8),
               (32, 37.8), (42, 37.8), (52, 37.8), (2.0, 10), (45.0, 10.5), (52.0, 15)]:
    via(x, y)

# pin-1 (gate) marks for the MOSFETs, printable size
dot(q1g[0], 15.85); dot(q2g[0], 15.85)

# ---- reference designators ----
ref_at(Q1, 34.8, 11.4, 0.8, 270); ref_at(Q2, 26.6, 11.4, 0.8, 270)
ref_at(R1, 28.25, 14.0, 0.8, 90); ref_at(R2, 19.95, 14.0, 0.8, 90); ref_at(R3, 14.45, 13.0, 0.8, 90)
ref_at(D1, 54.0, 7.2); ref_at(SW1, 8.5, 18.0)

# ---- front silkscreen: Pico outline and orientation ----
PX0, PX1 = pico_x(20) - 1.37, pico_x(1) + 1.37
PY0, PY1 = ROW1_Y - 1.61, ROW2_Y + 1.61
for (x1, y1, x2, y2) in [(PX0, PY0 - 0.15, PX1, PY0 - 0.15)]:
    pass
text("Pico W / Pico 2 W", 28.0, 28.8, 1.2)
text("USB end this side  >>>", 28.0, 31.2, 1.0)
text("Pin 1", pico_x(1) - 0.4, 25.0, 0.8)
text("Pico parts side facing up", 28.0, 33.6, 0.8)
text("Option B only: Q2, R2, J5", 28.0, 36.3, 0.8)

# ---- back silkscreen: GMX logo + project name ----
logo = pcbnew.FootprintLoad(LOGO_LIB, "GMX_Mods_Logo_Silk_22mm")
logo.SetFPID(pcbnew.LIB_ID("GMX_Logo", "GMX_Mods_Logo_Silk_22mm")); logo.SetPosition(P((X0 + X1) / 2, 31.0)); logo.SetReference("LOGO1"); logo.Reference().SetVisible(False)
b.Add(logo); logo.Flip(P((X0 + X1) / 2, 31.0), False)
text("GMX BC-250 Wake Board", (X0 + X1) / 2, 8.5, 1.5, pcbnew.B_SilkS, 0.25, True)
text("Rev " + REV + "   Pico W / Pico 2 W", (X0 + X1) / 2, 18.3, 1.0, pcbnew.B_SilkS, 0.15, True)

tb = b.GetTitleBlock(); tb.SetTitle("GMX BC-250 Wake Board"); tb.SetRevision(REV); tb.SetCompany("GMX Mods")

# ---- fill + save ----
path = os.path.join(OUT, f"{NAME}_Rev{REV}.kicad_pcb")
b.Save(path)
b2 = pcbnew.LoadBoard(path)
pcbnew.ZONE_FILLER(b2).Fill(b2.Zones())
b2.Save(path)
print("saved", path)
