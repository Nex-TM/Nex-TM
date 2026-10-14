import math, sys

W, H = 1000, 1200
CX, CY = 500, 620
PINK = "#E9A6BA"; DARK = "#B96B88"; LIGHT = "#F6CAD7"; BG = "#0A0A0A"

def P(x, y): return f"{x:.1f},{y:.1f}"

def catmull(points, n=16):
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i-1], pts[i], pts[i+1], pts[i+2]
        for s in range(n):
            t = s / n; t2 = t*t; t3 = t2*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    out.append(points[-1])
    return out

def tapered(points, wfunc, n=16, fill=PINK, extra=""):
    c = catmull(points, n); m = len(c)
    L = []; R = []
    for i, (x, y) in enumerate(c):
        if i == 0: dx, dy = c[1][0]-x, c[1][1]-y
        elif i == m-1: dx, dy = x-c[i-1][0], y-c[i-1][1]
        else: dx, dy = c[i+1][0]-c[i-1][0], c[i+1][1]-c[i-1][1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy/l, dx/l
        w = wfunc(i/(m-1))
        L.append((x+nx*w/2, y+ny*w/2)); R.append((x-nx*w/2, y-ny*w/2))
    poly = L + R[::-1]
    d = "M " + " L ".join(P(x, y) for x, y in poly) + " Z"
    return f'<path d="{d}" fill="{fill}" {extra}/>'

def spiral(cx, cy, r0, r1, a0, a1, n=40):
    return [(cx + (r0+(r1-r0)*i/n)*math.cos(a0+(a1-a0)*i/n), cy + (r0+(r1-r0)*i/n)*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]

def leaf(w): return lambda t: w*math.sin(math.pi*t)**0.7
def taper(w0, w1, p=1.0): return lambda t: w0 + (w1-w0)*(t**p)

def star_points(R, k):
    # square k (0: vertices on axes, 1: rotated 45)
    return [(CX + R*math.cos(math.radians(90*i + 45*k)), CY + R*math.sin(math.radians(90*i + 45*k))) for i in range(4)]

def seg_intersect(a, b, c, d):
    (x1,y1),(x2,y2),(x3,y3),(x4,y4) = a,b,c,d
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(den) < 1e-9: return None
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4))/den
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3))/den
    if 0 <= t <= 1 and 0 <= u <= 1: return (x1+t*(x2-x1), y1+t*(y2-y1))
    return None

def khatam(R, band=20, line=3):
    """Interlaced 8-point star made of two squares (Moroccan strapwork)."""
    A, B = star_points(R, 0), star_points(R, 1)
    out = []
    def poly(pts): return " ".join(P(x, y) for x, y in pts)
    for S in (A, B):
        out.append(f'<polygon points="{poly(S)}" fill="none" stroke="{PINK}" stroke-width="{band}" stroke-linejoin="miter" stroke-miterlimit="12"/>')
        out.append(f'<polygon points="{poly(S)}" fill="none" stroke="{BG}" stroke-width="{line}" stroke-linejoin="miter" stroke-miterlimit="12"/>')
    # interlace: at each crossing, redraw a short piece of the "over" square
    crossings = []
    for i in range(4):
        a1, a2 = A[i], A[(i+1) % 4]
        for j in range(4):
            b1, b2 = B[j], B[(j+1) % 4]
            p = seg_intersect(a1, a2, b1, b2)
            if p: crossings.append((p, (a1, a2), (b1, b2)))
    crossings.sort(key=lambda c: math.atan2(c[0][1]-CY, c[0][0]-CX))
    for k, (p, ea, eb) in enumerate(crossings):
        e = ea if k % 2 == 0 else eb
        dx, dy = e[1][0]-e[0][0], e[1][1]-e[0][1]
        l = math.hypot(dx, dy); ux, uy = dx/l, dy/l
        h = band*1.6
        q1 = (p[0]-ux*h, p[1]-uy*h); q2 = (p[0]+ux*h, p[1]+uy*h)
        out.append(f'<line x1="{q1[0]:.1f}" y1="{q1[1]:.1f}" x2="{q2[0]:.1f}" y2="{q2[1]:.1f}" stroke="{BG}" stroke-width="{band+2*line+2}"/>')
        q1p = (p[0]-ux*(h+1.5), p[1]-uy*(h+1.5)); q2p = (p[0]+ux*(h+1.5), p[1]+uy*(h+1.5))
        out.append(f'<line x1="{q1p[0]:.1f}" y1="{q1p[1]:.1f}" x2="{q2p[0]:.1f}" y2="{q2p[1]:.1f}" stroke="{PINK}" stroke-width="{band}"/>')
        out.append(f'<line x1="{q1[0]:.1f}" y1="{q1[1]:.1f}" x2="{q2[0]:.1f}" y2="{q2[1]:.1f}" stroke="{BG}" stroke-width="{line}"/>')
    return "\n".join(out)

def star_union_path(R):
    # union outline of the two squares as 16-vertex polygon (8 tips + 8 inner crossings)
    tips = [(CX + R*math.cos(math.radians(45*i)), CY + R*math.sin(math.radians(45*i))) for i in range(8)]
    ri = R*math.cos(math.radians(45))/math.cos(math.radians(22.5))
    inner = [(CX + ri*math.cos(math.radians(45*i+22.5)), CY + ri*math.sin(math.radians(45*i+22.5))) for i in range(8)]
    pts = []
    for i in range(8): pts += [tips[i], inner[i]]
    return "M " + " L ".join(P(x, y) for x, y in pts) + " Z"

def sun_rays(r_in, r_out, R):
    out = []
    for i in range(8):
        a = math.radians(45*i)
        ca, sa = math.cos(a), math.sin(a)
        base = (CX + r_in*ca, CY + r_in*sa); tip = (CX + r_out*ca, CY + r_out*sa)
        out.append(tapered([base, tip], taper(40, 0, 0.75), n=4))
        for s in (-1, 1):
            b = math.radians(45*i + s*6.5)
            base2 = (CX + (r_in+10)*math.cos(b), CY + (r_in+10)*math.sin(b))
            tip2 = (CX + (r_out-30)*math.cos(b), CY + (r_out-30)*math.sin(b))
            out.append(tapered([base2, tip2], taper(20, 0, 0.75), n=4))
    return "\n".join(out)

def seigaiha(x0, y0, x1, y1, r=40, rings=4, stroke=3.2):
    out = []
    dy = r*0.5; dx = r*2
    row = 0; y = y0 - r
    while y < y1 + r:
        off = dx/2 if row % 2 else 0
        x = x0 - dx + off
        while x < x1 + dx:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BG}"/>')
            for k in range(rings):
                rr = r - k*(r/(rings+0.5))
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="none" stroke="{PINK}" stroke-width="{stroke}"/>')
            x += dx
        y += dy; row += 1
    return "\n".join(out)

def sakura(cx, cy, r, fill=PINK):
    out = []
    petal = (f'M 0,0 C {-r*0.55:.1f},{-r*0.25:.1f} {-r*0.62:.1f},{-r*0.82:.1f} {-r*0.2:.1f},{-r*0.98:.1f} '
             f'L 0,{-r*0.8:.1f} L {r*0.2:.1f},{-r*0.98:.1f} C {r*0.62:.1f},{-r*0.82:.1f} {r*0.55:.1f},{-r*0.25:.1f} 0,0 Z')
    for i in range(5):
        out.append(f'<path transform="translate({cx},{cy}) rotate({72*i})" d="{petal}" fill="{fill}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.2:.1f}" fill="{BG}"/>')
    for i in range(5):
        a = math.radians(-90 + 72*i)
        out.append(f'<line x1="{cx+math.cos(a)*r*0.2:.1f}" y1="{cy+math.sin(a)*r*0.2:.1f}" x2="{cx+math.cos(a)*r*0.5:.1f}" y2="{cy+math.sin(a)*r*0.5:.1f}" stroke="{fill}" stroke-width="2.4" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx+math.cos(a)*r*0.52:.1f}" cy="{cy+math.sin(a)*r*0.52:.1f}" r="2.6" fill="{fill}"/>')
    return "\n".join(out)

def flourish_pair(cx, cy, scale=1.0, flip=False):
    """Moroccan arabesque scroll, mirrored."""
    s = scale
    pts = [(0, 0), (40*s, -6*s), (80*s, -2*s), (110*s, 12*s)] + spiral(130*s, 2*s, 22*s, 3*s, math.radians(150), math.radians(150+300), 24)
    one = tapered(pts, leaf(9*s), n=10)
    g = f'<g transform="translate({cx},{cy})">{one}</g><g transform="translate({cx},{cy}) scale(-1,1)">{one}</g>'
    return g

def arc_text(text, r, top, size, font="Cinzel", spacing=7, weight=600, fill=PINK):
    if top:
        d = f"M {CX-r},{CY} A {r},{r} 0 0 1 {CX+r},{CY}"
    else:
        d = f"M {CX-r},{CY} A {r},{r} 0 0 0 {CX+r},{CY}"
    pid = f"arc{'t' if top else 'b'}{int(r)}"
    return (f'<path id="{pid}" d="{d}" fill="none"/>'
            f'<text font-family="{font}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" fill="{fill}">'
            f'<textPath href="#{pid}" startOffset="50%" text-anchor="middle">{text}</textPath></text>')

def dragon():
    """Twin filigree dragons (left half, mirrored) circling the medallion."""
    out = []
    Rb = 452
    body = []
    for deg in range(250, 99, -6):
        a = math.radians(deg); r = Rb + 9*math.sin(math.radians(deg*3))
        body.append((CX + r*math.cos(a), CY + r*math.sin(a)))
    body += [(CX-60, CY+462), (CX-18, CY+478)]
    c = catmull(body, 8)
    # dorsal spikes (outward)
    for i in range(14, len(c)-30, 11):
        x, y = c[i]; dx, dy = c[i+1][0]-c[i-1][0], c[i+1][1]-c[i-1][1]
        l = math.hypot(dx, dy); tx_, ty_ = dx/l, dy/l; nx, ny = -ty_, tx_
        if (x-CX)*nx + (y-CY)*ny < 0: nx, ny = -nx, -ny
        t = i/len(c); ln = 30*(1-t)+10
        out.append(tapered([(x, y), (x+nx*ln*0.55 - tx_*ln*0.45, y+ny*ln*0.55 - ty_*ln*0.45), (x+nx*ln - tx_*ln*1.0, y+ny*ln - ty_*ln*1.0)], taper(13, 0, 0.8), n=6))
    out.append(tapered(body, lambda t: 40*(1-t)**0.8 + 5, n=8))
    out.append(tapered(body, lambda t: 1.8*(1-t)+0.6, n=8, fill=DARK))
    # tail tufts
    tx, ty = CX-18, CY+478
    out.append(tapered([(tx, ty), (tx+22, ty-18), (tx+40, ty-50)] + spiral(tx+30, ty-78, 22, 3, math.radians(60), math.radians(60-290), 20), leaf(10), n=10))
    out.append(tapered([(tx, ty), (tx+40, ty+8), (tx+74, ty-4)] + spiral(tx+88, ty-26, 18, 3, math.radians(120), math.radians(120+290), 20), leaf(9), n=10))
    # head (back of head at hx,hy; faces right / inward)
    hx, hy = CX-152, CY-438
    out.append(tapered([(hx-34, hy+8), (hx+30, hy-4), (hx+78, hy-2), (hx+116, hy+12)], taper(40, 5), n=10))
    out.append(tapered([(hx-12, hy+24), (hx+40, hy+28), (hx+94, hy+34)], taper(24, 3), n=10))
    out.append(tapered([(hx+66, hy+8), (hx+70, hy+26)], taper(7, 0), n=4))
    out.append(f'<ellipse cx="{hx+34}" cy="{hy+2}" rx="10" ry="6.5" fill="{BG}"/><circle cx="{hx+37}" cy="{hy+2}" r="2.8" fill="{PINK}"/>')
    for ox, oy in ((0, 0), (24, -3)):
        out.append(tapered([(hx+6+ox, hy-8+oy), (hx-8+ox, hy-52+oy), (hx-44+ox, hy-84+oy)], taper(14, 0, 0.8), n=10))
    for k in range(4):
        a0 = math.radians(140 + k*25)
        pts = [(hx-24, hy+10), (hx-56-8*k, hy-14+24*k)] + spiral(hx-84-6*k, hy-16+30*k, 20, 3, a0, a0+math.radians(300), 20)
        out.append(tapered(pts, leaf(11), n=10))
    out.append(tapered([(hx+110, hy+6), (hx+128, hy-24), (hx+118, hy-56)] + spiral(hx+100, hy-70, 14, 2, math.radians(20), math.radians(20-290), 20), lambda t: 4.5*(1-t)**0.3+0.5, n=10))
    out.append(tapered([(hx+96, hy+34), (hx+124, hy+54), (hx+112, hy+84)] + spiral(hx+92, hy+94, 14, 2, math.radians(-20), math.radians(-20+290), 20), lambda t: 4*(1-t)**0.3+0.5, n=10))
    g = "\n".join(out)
    return f'<g id="dragon">{g}</g><use href="#dragon" transform="translate({W},0) scale(-1,1)"/>'

def build(with_dragon):
    R = 320
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="{BG}"/>',
             '<defs>', f'<clipPath id="waves"><path d="{star_union_path(R-16)}"/></clipPath>', f'<clipPath id="lower"><rect x="0" y="{CY+104}" width="{W}" height="400"/></clipPath>', '</defs>']
    if with_dragon:
        parts.append(f'<g transform="translate({CX},{CY}) scale(0.86) translate({-CX},{-CY})">')
    # rings (kamon)
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="432" fill="none" stroke="{PINK}" stroke-width="5"/>')
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="419" fill="none" stroke="{PINK}" stroke-width="1.8"/>')
    # sun rays behind star
    parts.append(sun_rays(R-40, 396, R))
    # waves inside star, lower part
    # star
    parts.append(f'<path d="{star_union_path(R)}" fill="{BG}"/>')
    parts.append(f'<g clip-path="url(#waves)"><g clip-path="url(#lower)">{seigaiha(CX-330, CY+96, CX+330, CY+330, r=42, rings=4, stroke=3.4)}</g></g>')
    parts.append(khatam(R, band=20, line=3))
    # inner small star outline (rosette)
    # divider under monogram with diamond
    y_div = CY + 92
    parts.append(f'<line x1="{CX-200}" y1="{y_div}" x2="{CX-26}" y2="{y_div}" stroke="{PINK}" stroke-width="3"/>')
    parts.append(f'<line x1="{CX+26}" y1="{y_div}" x2="{CX+200}" y2="{y_div}" stroke="{PINK}" stroke-width="3"/>')
    parts.append(f'<polygon points="{P(CX,y_div-13)} {P(CX+13,y_div)} {P(CX,y_div+13)} {P(CX-13,y_div)}" fill="{PINK}"/>')
    parts.append(f'<polygon points="{P(CX,y_div-6)} {P(CX+6,y_div)} {P(CX,y_div+6)} {P(CX-6,y_div)}" fill="{BG}"/>')
    # sakura top
    parts.append(sakura(CX, CY-172, 40))
    parts.append(flourish_pair(CX, CY-112, 0.85))
    # monogram
    parts.append(f'<text x="{CX}" y="{CY+48}" font-family="Pirata One" font-size="168" letter-spacing="10" text-anchor="middle" fill="{PINK}">TALA</text>')
    # trilingual star row at the bottom of the star (over waves, boxed)
    y_tri = CY + 215
    parts.append(f'<rect x="{CX-190}" y="{y_tri-34}" width="380" height="60" fill="{BG}"/>')
    parts.append(f'<text x="{CX-132}" y="{y_tri+10}" font-family="IPAGothic" font-size="40" text-anchor="middle" fill="{PINK}">星</text>')
    parts.append(f'<text x="{CX}" y="{y_tri+6}" font-family="Cinzel" font-weight="600" font-size="28" letter-spacing="5" text-anchor="middle" fill="{PINK}">BITUIN</text>')
    parts.append(f'<text x="{CX+132}" y="{y_tri+9}" font-family="Noto Naskh Arabic" font-size="36" text-anchor="middle" fill="{PINK}">نجمة</text>')
    parts.append(f'<circle cx="{CX-92}" cy="{y_tri-4}" r="3" fill="{PINK}"/><circle cx="{CX+92}" cy="{y_tri-4}" r="3" fill="{PINK}"/>')
    # arc texts outside ring
    if not with_dragon:
        parts.append(arc_text("HOSHI  ·  NAJMA  ·  TALA", 468, True, 30))
        parts.append(arc_text("MAROC  ·  PILIPINAS  ·  NIPPON", 468, False, 26))
    if with_dragon:
        parts.append('</g>')
        parts.append(dragon())
    parts.append('</svg>')
    return "\n".join(parts)

for name, flag in (("tala_back_A", False), ("tala_back_B_dragon", True)):
    open(f"out/{name}.svg", "w").write(build(flag))
print("ok")
