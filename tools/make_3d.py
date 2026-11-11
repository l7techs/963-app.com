"""Makes the web versions of the 3D renders in assets/3d/ (sources: 2048px PNGs).

    python tools/make_3d.py

- cars/homes/goods/equipment/services.png  -> assets/3d/web/<name>.webp (900px), shown in the marketplace panels
- hero.png -> assets/3d/web/hero.webp with the 963 app icon (assets/app-icon.png) placed on the phone screen
The 3D app-icon.png render is not used: the site uses the real app icon instead.
"""
import os
from collections import deque

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', '3d')
OUT = os.path.join(SRC, 'web')


def webp(im, name, size):
    im = im.copy()
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=86, method=6)


def _lsq(pairs):
    n = len(pairs)
    st = sum(t for t, _ in pairs); sv = sum(v for _, v in pairs)
    stt = sum(t * t for t, _ in pairs); stv = sum(t * v for t, v in pairs)
    a = (n * stv - st * sv) / (n * stt - st * st)
    return a, (sv - a * st) / n


def fit_line(pairs):
    """Robust a*t + b through (t, value) pairs: refits after dropping outliers such as the camera notch,
    the orbit ring and the wrench that cover parts of the screen edge. Returns (a, b)."""
    pts = list(pairs)
    for _ in range(6):
        a, b = _lsq(pts)
        res = sorted(abs(v - (a * t + b)) for t, v in pts)
        cut = max(4, 2.5 * res[len(res) // 2])
        kept = [(t, v) for t, v in pts if abs(v - (a * t + b)) <= cut]
        if len(kept) == len(pts) or len(kept) < 10:
            break
        pts = kept
    return _lsq(pts)


def screen_quad(im, seeds):
    """Flood-fills the phone's green screen from `seeds` (the orbit ring splits it in two) and fits its
    four straight edges. Returns the mask and the corners (tl, tr, br, bl)."""
    px = im.load()
    W, H = im.size

    def ok(c):
        r, g, b, a = c
        return a > 200 and r < 60 and 45 < g < 125 and 35 < b < 105 and g > r + 25

    seen = bytearray(W * H)
    q = deque()
    for s in seeds:
        q.append(s)
        seen[s[1] * W + s[0]] = 1
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and ok(px[nx, ny]):
                seen[ny * W + nx] = 1
                q.append((nx, ny))
    mask = Image.frombytes('L', (W, H), bytes(seen)).point(lambda v: 255 if v else 0)
    x0, y0, x1, y1 = mask.getbbox()
    rows = {y: [x for x in range(x0, x1 + 1) if seen[y * W + x]] for y in range(y0, y1 + 1, 4)}
    cols = {x: [y for y in range(y0, y1 + 1) if seen[y * W + x]] for x in range(x0, x1 + 1, 4)}
    # Use the middle 70% of each side, away from the rounded corners and the ring.
    ys = [y for y, xs in rows.items() if xs]
    lo, hi = ys[int(len(ys) * .15)], ys[int(len(ys) * .85)]
    left = fit_line([(y, min(rows[y])) for y in ys if lo <= y <= hi])
    right = fit_line([(y, max(rows[y])) for y in ys if lo <= y <= hi])
    xs_ = [x for x, v in cols.items() if v]
    lo, hi = xs_[int(len(xs_) * .2)], xs_[int(len(xs_) * .8)]
    top = fit_line([(x, min(cols[x])) for x in xs_ if lo <= x <= hi])
    bottom = fit_line([(x, max(cols[x])) for x in xs_ if lo <= x <= hi])

    def meet(vert, horiz):  # x = a*y + b and y = c*x + d
        a, b = vert; c, d = horiz
        y = (c * b + d) / (1 - c * a)
        return (a * y + b, y)
    return mask, (meet(left, top), meet(right, top), meet(right, bottom), meet(left, bottom))


def lerp_quad(q, u, v):
    (tl, tr, br, bl) = q
    top = (tl[0] + (tr[0] - tl[0]) * u, tl[1] + (tr[1] - tl[1]) * u)
    bot = (bl[0] + (br[0] - bl[0]) * u, bl[1] + (br[1] - bl[1]) * u)
    return (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)


def perspective_coeffs(dst, src):
    """Coefficients for Image.transform(PERSPECTIVE) mapping output points `dst` back to input points `src`."""
    rows = []
    for (x, y), (X, Y) in zip(dst, src):
        rows.append([x, y, 1, 0, 0, 0, -X * x, -X * y, X])
        rows.append([0, 0, 0, x, y, 1, -Y * x, -Y * y, Y])
    n = 8  # Gauss-Jordan elimination with partial pivoting (no numpy needed)
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(rows[r][c]))
        rows[c], rows[p] = rows[p], rows[c]
        piv = rows[c][c]
        rows[c] = [v / piv for v in rows[c]]
        for r in range(n):
            if r != c and rows[r][c]:
                f = rows[r][c]
                rows[r] = [a - f * b for a, b in zip(rows[r], rows[c])]
    return [rows[r][n] for r in range(n)]


def rounded(icon, radius_frac=.2237):
    s = icon.size[0]
    m = Image.new('L', (s * 4, s * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, s * 4 - 1, s * 4 - 1], radius=s * 4 * radius_frac, fill=255)
    out = icon.convert('RGBA')
    out.putalpha(m.resize((s, s), Image.LANCZOS))
    return out


def hero():
    im = Image.open(os.path.join(SRC, 'hero.png')).convert('RGBA')
    mask, quad = screen_quad(im, [(950, 1000), (1117, 1452)])
    print('screen corners', [tuple(round(v) for v in p) for p in quad])
    icon = rounded(Image.open(os.path.join(ROOT, 'assets', 'app-icon.png')).resize((1024, 1024), Image.LANCZOS))
    # Icon square in screen space: 62% of the screen width, centred, a little above the middle.
    (tl, tr, br, bl) = quad
    width = ((tr[0] - tl[0]) ** 2 + (tr[1] - tl[1]) ** 2) ** .5
    height = ((bl[0] - tl[0]) ** 2 + (bl[1] - tl[1]) ** 2) ** .5
    du = .58
    dv = du * width / height
    u0, v0 = .5 - du / 2, .36 - dv / 2
    dst = [lerp_quad(quad, u0, v0), lerp_quad(quad, u0 + du, v0), lerp_quad(quad, u0 + du, v0 + dv), lerp_quad(quad, u0, v0 + dv)]
    src = [(0, 0), (1024, 0), (1024, 1024), (0, 1024)]
    warped = icon.transform(im.size, Image.PERSPECTIVE, perspective_coeffs(dst, src), Image.BICUBIC)
    # soft shadow under the icon
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shadow.putalpha(warped.getchannel('A').point(lambda a: a * .45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18)).transform(im.size, Image.AFFINE, (1, 0, -6, 0, 1, -16))
    layer = Image.alpha_composite(shadow, warped)
    layer.putalpha(Image.composite(layer.getchannel('A'), Image.new('L', im.size, 0), mask.filter(ImageFilter.MaxFilter(9))))
    out = Image.alpha_composite(im, layer)
    webp(out, 'hero', 1100)
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n in ('cars', 'homes', 'goods', 'equipment', 'services'):
        webp(Image.open(os.path.join(SRC, n + '.png')).convert('RGBA'), n, 900)
    hero()
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
