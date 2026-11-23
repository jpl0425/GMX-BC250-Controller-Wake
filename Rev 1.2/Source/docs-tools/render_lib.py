# Shared drawing helpers for the "realistic" board renders (SVG -> PNG via rsvg-convert)
import subprocess, os, random
F = "DejaVu Sans"

DEFS = """
<defs>
  <filter id="noise" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/>
    <feColorMatrix type="saturate" values="0" in="n" result="g"/>
    <feComponentTransfer in="g" result="a"><feFuncA type="linear" slope="0.10"/></feComponentTransfer>
    <feComposite in="a" in2="SourceGraphic" operator="in" result="na"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="na"/></feMerge>
  </filter>
  <filter id="brushed" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.002 0.6" numOctaves="2" seed="7" result="n"/>
    <feColorMatrix type="saturate" values="0" in="n" result="g"/>
    <feComponentTransfer in="g" result="a"><feFuncA type="linear" slope="0.22"/></feComponentTransfer>
    <feComposite in="a" in2="SourceGraphic" operator="in" result="na"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="na"/></feMerge>
  </filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="5"/><feOffset dx="6" dy="8" result="o"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.45"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softshadow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3"/><feOffset dx="3" dy="4" result="o"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.5"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="pcblight" cx="35%" cy="30%" r="85%">
    <stop offset="0" stop-color="#2a8a4c"/><stop offset="0.6" stop-color="#1d6c3b"/><stop offset="1" stop-color="#13502a"/>
  </radialGradient>
  <radialGradient id="solder" cx="38%" cy="35%" r="65%">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.25" stop-color="#d9dde0"/><stop offset="0.7" stop-color="#8d969c"/><stop offset="1" stop-color="#5b6368"/>
  </radialGradient>
  <radialGradient id="copper" cx="40%" cy="35%" r="70%">
    <stop offset="0" stop-color="#f6c48a"/><stop offset="0.6" stop-color="#d9894a"/><stop offset="1" stop-color="#a85f2a"/>
  </radialGradient>
  <radialGradient id="hole" cx="50%" cy="55%" r="60%">
    <stop offset="0" stop-color="#3b2a20"/><stop offset="0.8" stop-color="#140e0a"/><stop offset="1" stop-color="#000"/>
  </radialGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff4b8"/><stop offset="0.45" stop-color="#e2b84a"/><stop offset="1" stop-color="#9c7420"/>
  </linearGradient>
  <linearGradient id="plastic" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a3a3a"/><stop offset="0.15" stop-color="#1e1e1e"/><stop offset="1" stop-color="#0b0b0b"/>
  </linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#e9ecee"/><stop offset="0.5" stop-color="#bfc5c9"/><stop offset="1" stop-color="#8e969b"/>
  </linearGradient>
  <linearGradient id="nickel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f3f4f5"/><stop offset="0.5" stop-color="#b9bec2"/><stop offset="1" stop-color="#7d858a"/>
  </linearGradient>
  <radialGradient id="lightpipe" cx="40%" cy="35%" r="70%">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/><stop offset="0.5" stop-color="#dfe9ee" stop-opacity="0.75"/><stop offset="1" stop-color="#9fb3bd" stop-opacity="0.8"/>
  </radialGradient>
  <linearGradient id="nylon" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f4f1e8"/><stop offset="0.5" stop-color="#e2ddcf"/><stop offset="1" stop-color="#c5bfae"/>
  </linearGradient>
  <linearGradient id="nylonblack" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3b3b3b"/><stop offset="0.5" stop-color="#232323"/><stop offset="1" stop-color="#121212"/>
  </linearGradient>
  <linearGradient id="table" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#e3c39a"/><stop offset="1" stop-color="#caa273"/>
  </linearGradient>
</defs>
"""

def svg(w, h, body, bg="url(#table)"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS}<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size=18, weight="normal", anchor="start", fill="#111", rot=0, family=None, spacing=0):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{family or F}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}"{tr}{ls}>{esc(s)}</text>')

def silk(x, y, s, size=20, anchor="start", rot=0):
    return text(x, y, s, size, "bold", anchor, "#eef3ee", rot, "DejaVu Sans Mono", 1)

def pcb(x, y, w, h, rx=18, seed=1, via_step=26):
    r = random.Random(seed)
    s = f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#pcblight)" filter="url(#noise)"/></g>'
    # board edge highlight
    s += f'<rect x="{x+2}" y="{y+2}" width="{w-4}" height="{h-4}" rx="{rx}" fill="none" stroke="#5fae7a" stroke-opacity="0.35" stroke-width="2"/>'
    # stitching vias
    for vx in range(int(x + 20), int(x + w - 10), via_step):
        for vy in range(int(y + 20), int(y + h - 10), via_step):
            if r.random() < 0.55:
                jx, jy = vx + r.uniform(-3, 3), vy + r.uniform(-3, 3)
                s += f'<circle cx="{jx:.1f}" cy="{jy:.1f}" r="2.6" fill="#145a2e"/><circle cx="{jx-0.6:.1f}" cy="{jy-0.6:.1f}" r="1.1" fill="#3f9a60" opacity="0.7"/>'
    return s

def trace(points, w=4):
    d = " ".join(f"{a},{b}" for a, b in points)
    return f'<polyline points="{d}" fill="none" stroke="#2a8a50" stroke-width="{w}" stroke-linejoin="round" opacity="0.65"/>'

def solder_joint(x, y, r=13, pin=True):
    s = f'<circle cx="{x}" cy="{y}" r="{r+5}" fill="#c9d1c9" opacity="0.35"/>'
    s += f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#solder)" filter="url(#softshadow)"/>'
    if pin:
        s += f'<circle cx="{x-1}" cy="{y-1}" r="{max(2.5, r*0.28)}" fill="#e8ecee" stroke="#7a8287" stroke-width="1"/>'
    return s

def square_joint(x, y, r=13):
    s = f'<rect x="{x-r-5}" y="{y-r-5}" width="{2*r+10}" height="{2*r+10}" fill="#c9d1c9" opacity="0.35"/>'
    s += f'<rect x="{x-r}" y="{y-r}" width="{2*r}" height="{2*r}" rx="3" fill="url(#solder)" filter="url(#softshadow)"/>'
    s += f'<circle cx="{x-1}" cy="{y-1}" r="{max(2.5, r*0.28)}" fill="#e8ecee" stroke="#7a8287" stroke-width="1"/>'
    return s

def mount_hole(x, y, r=44):
    s = f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#copper)"/>'
    for i in range(8):
        import math
        a = i * math.pi / 4
        s += f'<circle cx="{x + math.cos(a)*r*0.72:.1f}" cy="{y + math.sin(a)*r*0.72:.1f}" r="2.6" fill="#5a2f12"/>'
    s += f'<circle cx="{x}" cy="{y}" r="{r*0.48}" fill="url(#hole)" stroke="#8a5a30" stroke-width="2"/>'
    return s

def smd(x, y, w=22, h=12, color="#7a5c3a", rot=0):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    return (f'<g{tr} filter="url(#softshadow)"><rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="1.5" fill="{color}"/>'
            f'<rect x="{x-w/2}" y="{y-h/2}" width="{w*0.22}" height="{h}" fill="url(#nickel)"/>'
            f'<rect x="{x+w/2-w*0.22}" y="{y-h/2}" width="{w*0.22}" height="{h}" fill="url(#nickel)"/></g>')

def ic(x, y, w, h, label="", pins_side=8, rot=0):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    s = f'<g{tr}>'
    step = w / (pins_side + 1)
    for i in range(pins_side):
        px = x - w/2 + step * (i + 1)
        s += f'<rect x="{px-3}" y="{y-h/2-9}" width="6" height="10" fill="url(#nickel)"/><rect x="{px-3}" y="{y+h/2-1}" width="6" height="10" fill="url(#nickel)"/>'
    s += f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="3" fill="url(#plastic)" filter="url(#softshadow)"/>'
    s += f'<circle cx="{x-w/2+9}" cy="{y+h/2-9}" r="3" fill="#444"/>'
    if label: s += text(x, y + 5, label, 12, "bold", "middle", "#9a9a9a")
    return s + "</g>"

def callout_ring(x, y, r=26, color="#FFE000"):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#000" stroke-opacity="0.55" stroke-width="9"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{color}" stroke-width="5" filter="url(#glow)"/>')

def label(x, y, lines, color="#FFE000", w=None, anchor_pt=None, title_size=22, size=17):
    """dark label box at x,y (top-left); optional leader line to anchor_pt"""
    lw = w or max(len(l) for l in lines) * size * 0.62 + 30
    lh = 16 + title_size + 8 + (len(lines) - 1) * (size + 7)
    s = ""
    if anchor_pt:
        ax, ay = anchor_pt
        cx = x + lw / 2
        cy = y + lh / 2
        # connect from nearest box edge midpoint
        ex = x if ax < x else (x + lw if ax > x + lw else cx)
        ey = y if ay < y else (y + lh if ay > y + lh else cy)
        s += f'<line x1="{ex}" y1="{ey}" x2="{ax}" y2="{ay}" stroke="#000" stroke-opacity="0.55" stroke-width="8" stroke-linecap="round"/>'
        s += f'<line x1="{ex}" y1="{ey}" x2="{ax}" y2="{ay}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
    s += f'<rect x="{x}" y="{y}" width="{lw}" height="{lh}" rx="10" fill="#101418" fill-opacity="0.92" stroke="{color}" stroke-width="3"/>'
    s += text(x + 14, y + 12 + title_size, lines[0], title_size, "bold", "start", color)
    for i, l in enumerate(lines[1:]):
        s += text(x + 14, y + 12 + title_size + 10 + (i + 1) * (size + 7) - 4, l, size, "normal", "start", "#ffffff")
    return s

def probe(tipx, tipy, color, angle=-35, length=260, lab=None):
    """multimeter probe whose tip touches tipx,tipy, coming in at angle (degrees, 0 = from right)"""
    g = f'<g transform="rotate({angle} {tipx} {tipy})" filter="url(#shadow)">'
    g += f'<polygon points="{tipx},{tipy} {tipx+26},{tipy-4} {tipx+26},{tipy+4}" fill="url(#nickel)"/>'
    g += f'<rect x="{tipx+26}" y="{tipy-9}" width="{length*0.55}" height="18" rx="6" fill="{color}"/>'
    g += f'<rect x="{tipx+26+length*0.55}" y="{tipy-14}" width="14" height="28" rx="4" fill="{color}"/>'
    g += f'<rect x="{tipx+40+length*0.55}" y="{tipy-11}" width="{length*0.4}" height="22" rx="8" fill="{color}"/>'
    g += f'<rect x="{tipx+30}" y="{tipy-7}" width="{length*0.5}" height="4" rx="2" fill="#fff" opacity="0.25"/>'
    g += "</g>"
    return g

def wire_path(d, color, w=10):
    return (f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="{w+4}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity="0.25" stroke-width="{w*0.3}" stroke-linecap="round" transform="translate(-1,-2)"/>')

def title_bar(w, title, subtitle):
    return (f'<rect x="0" y="0" width="{w}" height="86" fill="#0f1a14" fill-opacity="0.93"/>'
            + text(28, 40, title, 30, "bold", "start", "#ffffff")
            + text(28, 72, subtitle, 18, "normal", "start", "#c8e6c9"))

def footer(w, h, s):
    return (f'<rect x="0" y="{h-44}" width="{w}" height="44" fill="#0f1a14" fill-opacity="0.9"/>'
            + text(w/2, h - 15, s, 16, "normal", "middle", "#ffe082"))

def save(outdir, name, content, scale=1.0):
    p = os.path.join(outdir, name + ".svg")
    open(p, "w").write(content)
    subprocess.run(["rsvg-convert", "-z", str(scale), "-o", os.path.join(outdir, name + ".png"), p], check=True)
