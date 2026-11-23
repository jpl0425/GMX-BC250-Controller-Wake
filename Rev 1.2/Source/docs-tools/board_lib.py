# Realistic top-view perfboard build renderer for the wake board
from render_lib import *

class Board:
    def __init__(self, ox, oy, cols, rows, P=32):
        self.ox, self.oy, self.cols, self.rows, self.P = ox, oy, cols, rows, P
    def xy(self, c, r):
        return self.ox + self.P * (c + 0.5), self.oy + self.P * (r + 0.5)
    def draw(self):
        P = self.P; w = self.cols * P; h = self.rows * P
        s = (f'<g filter="url(#shadow)"><rect x="{self.ox-14}" y="{self.oy-14}" width="{w+28}" height="{h+28}" rx="8" '
             f'fill="#c9a86a" filter="url(#noise)"/></g>')
        s += f'<rect x="{self.ox-14}" y="{self.oy-14}" width="{w+28}" height="{h+28}" rx="8" fill="none" stroke="#a8874e" stroke-width="2"/>'
        for c in range(self.cols):
            for r in range(self.rows):
                x, y = self.xy(c, r)
                s += f'<circle cx="{x}" cy="{y}" r="{P*0.30}" fill="#c98a4a" stroke="#9c6430" stroke-width="1"/><circle cx="{x}" cy="{y}" r="{P*0.12}" fill="#2a1d10"/>'
        return s
    def pad(self, c, r, big=False):
        x, y = self.xy(c, r)
        rr = self.P * (0.36 if big else 0.30)
        return f'<circle cx="{x}" cy="{y}" r="{rr}" fill="url(#solder)" filter="url(#softshadow)"/>'
    def wire(self, pts, color, w=None, bare=False):
        w = w or self.P * 0.30
        xy = [self.xy(c, r) for c, r in pts]
        d = "M " + " L ".join(f"{x},{y}" for x, y in xy)
        s = ""
        if bare:
            s += f'<path d="{d}" fill="none" stroke="#7d868b" stroke-width="{w*0.55+2}" stroke-linecap="round" stroke-linejoin="round"/>'
            s += f'<path d="{d}" fill="none" stroke="#d9dee1" stroke-width="{w*0.55}" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            s += f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="{w+4}" stroke-linecap="round" stroke-linejoin="round" transform="translate(2,3)"/>'
            s += f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
            s += f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity="0.22" stroke-width="{w*0.28}" stroke-linecap="round" stroke-linejoin="round" transform="translate(-1,-2)"/>'
        for c, r in (pts[0], pts[-1]):
            s += self.pad(c, r)
        return s

def pico_w(b, cl, rt, label="Pico W  /  Pico 2 W"):
    """Pico W top view. Left pin column at grid col cl, right at cl+7; pin 1 at row rt (USB at top)."""
    P = b.P
    x0, y0 = b.xy(cl, rt); x1, y1 = b.xy(cl + 7, rt + 19)
    L, R, T, B = x0 - P * 0.55, x1 + P * 0.55, y0 - P * 1.6, y1 + P * 0.75
    s = f'<g filter="url(#shadow)"><rect x="{L}" y="{T}" width="{R-L}" height="{B-T}" rx="6" fill="#1f7a3e" filter="url(#noise)"/></g>'
    # micro-USB
    cx = (L + R) / 2
    s += f'<rect x="{cx-P*1.2}" y="{T-P*0.35}" width="{P*2.4}" height="{P*1.25}" rx="4" fill="url(#nickel)" stroke="#666"/>'
    s += f'<rect x="{cx-P*0.8}" y="{T-P*0.15}" width="{P*1.6}" height="{P*0.35}" rx="2" fill="#333"/>'
    # castellated pins
    for i in range(20):
        for (c, n) in ((cl, i + 1), (cl + 7, 40 - i)):
            x, y = b.xy(c, rt + i)
            s += f'<rect x="{x-P*0.36}" y="{y-P*0.36}" width="{P*0.72}" height="{P*0.72}" rx="3" fill="url(#gold)"/>'
            s += f'<circle cx="{x}" cy="{y}" r="{P*0.16}" fill="url(#solder)"/>'
            tx = x + P * 0.55 if c == cl else x - P * 0.55
            s += text(tx, y + 4, str(n), 10, "bold", "start" if c == cl else "end", "#e8f5e9")
    # BOOTSEL
    s += f'<rect x="{cx-P*1.5}" y="{T+P*1.3}" width="{P*1.0}" height="{P*1.0}" rx="3" fill="#cfd4d6" filter="url(#softshadow)"/>'
    s += f'<circle cx="{cx-P*1.0}" cy="{T+P*1.8}" r="{P*0.3}" fill="#f5f5f5" stroke="#999"/>'
    s += text(cx - P * 1.0, T + P * 2.75, "BOOTSEL", 10, "bold", "middle", "#e8f5e9")
    # LED
    s += f'<rect x="{cx+P*0.8}" y="{T+P*1.5}" width="{P*0.35}" height="{P*0.22}" fill="#e0e0e0"/>' + text(cx + P * 0.98, T + P * 2.2, "LED", 9, "bold", "middle", "#e8f5e9")
    # RP2040/RP2350
    s += f'<rect x="{cx-P*1.15}" y="{T+P*5.2}" width="{P*2.3}" height="{P*2.3}" rx="3" fill="url(#plastic)" filter="url(#softshadow)"/>'
    s += text(cx, T + P * 6.45, "RP2040 /", 9, "bold", "middle", "#9e9e9e") + text(cx, T + P * 6.85, "RP2350", 9, "bold", "middle", "#9e9e9e")
    # flash
    s += f'<rect x="{cx-P*0.9}" y="{T+P*8.6}" width="{P*1.8}" height="{P*1.3}" rx="2" fill="url(#plastic)"/>'
    # wireless shield can
    s += f'<rect x="{cx-P*1.6}" y="{T+P*12.2}" width="{P*3.2}" height="{P*3.4}" rx="4" fill="url(#metal)" filter="url(#brushed)" stroke="#7d868b"/>'
    # antenna area
    s += f'<rect x="{cx-P*2.4}" y="{B-P*3.6}" width="{P*4.8}" height="{P*2.8}" rx="3" fill="#176332"/>'
    s += f'<path d="M {cx-P*2} {B-P*1.4} h {P*4} v -{P*0.4} h -{P*3.6} v -{P*0.4} h {P*3.6} v -{P*0.4} h -{P*3.6}" fill="none" stroke="#c98a4a" stroke-width="3"/>'
    s += text(cx, T + P * 18.0, label, 12, "bold", "middle", "#ffffff", rot=-90)
    return s

def sot23_adapter(b, c, rt, ref):
    """SOT-23-to-DIP adapter, pins vertical at col c rows rt..rt+2 (1,2,3), board body to the right."""
    P = b.P
    x, y = b.xy(c, rt)
    s = f'<g filter="url(#shadow)"><rect x="{x-P*0.5}" y="{y-P*0.5}" width="{P*2.6}" height="{P*3.0}" rx="4" fill="#1e4fa8"/></g>'
    for i in range(3):
        px, py = b.xy(c, rt + i)
        s += f'<circle cx="{px}" cy="{py}" r="{P*0.3}" fill="url(#solder)"/>'
        s += text(px + P * 0.45, py + 4, str(i + 1), 11, "bold", "start", "#ffffff")
    cx, cy = x + P * 1.45, y + P * 1.0
    s += f'<rect x="{cx-P*0.32}" y="{cy-P*0.45}" width="{P*0.64}" height="{P*0.9}" rx="2" fill="url(#plastic)"/>'
    for dy in (-0.25, 0.25):
        s += f'<rect x="{cx-P*0.55}" y="{cy+P*dy-3}" width="{P*0.25}" height="6" fill="url(#nickel)"/>'
    s += f'<rect x="{cx+P*0.3}" y="{cy-3}" width="{P*0.25}" height="6" fill="url(#nickel)"/>'
    s += text(x + P * 1.05, y + P * 2.35, ref, 13, "bold", "middle", "#ffffff")
    return s

def chip_adapter(b, c1, r1, c2, r2, ref, kind):
    """2-pin SMD-to-DIP adapter between holes (c1,r1)-(c2,r2). kind: 'res' or 'diode' (band at second pin)."""
    P = b.P
    x1, y1 = b.xy(c1, r1); x2, y2 = b.xy(c2, r2)
    vertical = c1 == c2
    if vertical:
        bx, by, bw, bh = x1 - P * 0.5, min(y1, y2) - P * 0.5, P * 1.6, abs(y2 - y1) + P
    else:
        bx, by, bw, bh = min(x1, x2) - P * 0.5, y1 - P * 0.5, abs(x2 - x1) + P, P * 1.6
    s = f'<g filter="url(#shadow)"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="#1e4fa8"/></g>'
    s += f'<circle cx="{x1}" cy="{y1}" r="{P*0.3}" fill="url(#solder)"/><circle cx="{x2}" cy="{y2}" r="{P*0.3}" fill="url(#solder)"/>'
    mx, my = (x1 + x2) / 2 + (P * 0.55 if vertical else 0), (y1 + y2) / 2 + (0 if vertical else P * 0.55)
    if kind == "res":
        if vertical:
            s += f'<rect x="{mx-P*0.2}" y="{my-P*0.38}" width="{P*0.4}" height="{P*0.76}" fill="#1c1c1c"/><rect x="{mx-P*0.2}" y="{my-P*0.38}" width="{P*0.4}" height="{P*0.16}" fill="url(#nickel)"/><rect x="{mx-P*0.2}" y="{my+P*0.22}" width="{P*0.4}" height="{P*0.16}" fill="url(#nickel)"/>'
        else:
            s += f'<rect x="{mx-P*0.38}" y="{my-P*0.2}" width="{P*0.76}" height="{P*0.4}" fill="#1c1c1c"/><rect x="{mx-P*0.38}" y="{my-P*0.2}" width="{P*0.16}" height="{P*0.4}" fill="url(#nickel)"/><rect x="{mx+P*0.22}" y="{my-P*0.2}" width="{P*0.16}" height="{P*0.4}" fill="url(#nickel)"/>'
    else:
        if vertical:
            s += f'<rect x="{mx-P*0.25}" y="{my-P*0.4}" width="{P*0.5}" height="{P*0.8}" rx="2" fill="#222"/><rect x="{mx-P*0.25}" y="{my+P*0.2}" width="{P*0.5}" height="{P*0.12}" fill="#e0e0e0"/>'
        else:
            s += f'<rect x="{mx-P*0.4}" y="{my-P*0.25}" width="{P*0.8}" height="{P*0.5}" rx="2" fill="#222"/><rect x="{mx+P*0.2}" y="{my-P*0.25}" width="{P*0.12}" height="{P*0.5}" fill="#e0e0e0"/>'
    tx = bx + bw / 2 if not vertical else bx + bw + 4
    ty = by + bh + 16 if not vertical else (y1 + y2) / 2 + 5
    s += text(tx, ty, ref, 13, "bold", "middle" if not vertical else "start", "#1a237e")
    return s

def header(b, pins, labels=None, vertical=False):
    """male pin header at list of (c,r) holes"""
    P = b.P
    xs = [b.xy(c, r) for c, r in pins]
    minx = min(x for x, y in xs) - P * 0.5; maxx = max(x for x, y in xs) + P * 0.5
    miny = min(y for x, y in xs) - P * 0.5; maxy = max(y for x, y in xs) + P * 0.5
    s = f'<g filter="url(#shadow)"><rect x="{minx}" y="{miny}" width="{maxx-minx}" height="{maxy-miny}" rx="3" fill="url(#plastic)"/></g>'
    for x, y in xs:
        s += f'<rect x="{x-P*0.17}" y="{y-P*0.17}" width="{P*0.34}" height="{P*0.34}" fill="url(#gold)" stroke="#7a5a14"/>'
    return s

def tact(b, c, r1, r2, ref):
    P = b.P
    x, y1 = b.xy(c, r1); _, y2 = b.xy(c, r2)
    s = f'<g filter="url(#shadow)"><rect x="{x-P*0.2}" y="{y1-P*0.2}" width="{P*1.6}" height="{y2-y1+P*0.4}" rx="3" fill="#1b1b1b"/></g>'
    s += f'<circle cx="{x+P*0.6}" cy="{(y1+y2)/2}" r="{P*0.45}" fill="#3a3a3a" stroke="#555"/>'
    s += f'<circle cx="{x}" cy="{y1}" r="{P*0.25}" fill="url(#solder)"/><circle cx="{x}" cy="{y2}" r="{P*0.25}" fill="url(#solder)"/>'
    s += text(x - P * 0.45, (y1 + y2) / 2 + 5, ref, 13, "bold", "end", "#1a237e")
    return s

def lead(b, c, r, d, color, w=10):
    """off-board flying lead from header pin (c,r) along SVG path d (starting at that pin)"""
    x, y = b.xy(c, r)
    return wire_path(f"M {x} {y} " + d, color, w)
