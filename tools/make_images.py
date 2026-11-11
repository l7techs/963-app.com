"""Renders the PNG icons and the link-preview image into assets/.

    python tools/make_images.py

Placeholder art drawn from the brand colours until the final 963 artwork exists.
Replace assets/og-image.png (1200x630) and the icons when it does.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'assets')
FONTS = 'C:/Windows/Fonts/'
F_BOLD = FONTS + 'segoeuib.ttf'
F_SEMI = FONTS + 'seguisb.ttf'
F_AR = FONTS + 'segoeuib.ttf'

FOREST = [(11, 90, 77), (5, 66, 57), (0, 38, 35)]
GOLD_TOP, GOLD_BOT = (228, 214, 174), (185, 167, 121)


def gradient(w, h, stops, diagonal=True):
    img = Image.new('RGB', (w, h))
    px = img.load()
    n = len(stops) - 1
    for y in range(h):
        for x in range(w):
            t = ((x / w) + (y / h)) / 2 if diagonal else y / h
            i = min(int(t * n), n - 1)
            f = t * n - i
            a, b = stops[i], stops[i + 1]
            px[x, y] = tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))
    return img


def pattern(draw, w, h, step, color, width=1):
    for cy in range(step // 2, h + step, step):
        for cx in range(step // 2, w + step, step):
            r = step * 0.19
            draw.rectangle([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
            d = r * 1.41
            draw.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)], outline=color, width=width)


def gold_text(base, xy, text, font, anchor='mm'):
    mask = Image.new('L', base.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    bbox = mask.getbbox()
    grad = gradient(base.size[0], base.size[1], [GOLD_TOP, GOLD_BOT], diagonal=False)
    if bbox:
        h = bbox[3] - bbox[1]
        g = Image.new('RGB', base.size)
        for y in range(base.size[1]):
            t = min(1, max(0, (y - bbox[1]) / max(h, 1)))
            c = tuple(int(GOLD_TOP[k] + (GOLD_BOT[k] - GOLD_TOP[k]) * t) for k in range(3))
            ImageDraw.Draw(g).line([(0, y), (base.size[0], y)], fill=c)
        grad = g
    base.paste(grad, (0, 0), mask)


def icon(size, rounded=True):
    s = size * 4
    img = gradient(s, s, FOREST)
    d = ImageDraw.Draw(img, 'RGBA')
    c, r = s / 2, s * 0.25
    d.rectangle([c - r, c - r, c + r, c + r], outline=(185, 167, 121, 56), width=max(2, s // 60))
    dd = r * 1.41
    d.polygon([(c, c - dd), (c + dd, c), (c, c + dd), (c - dd, c)], outline=(185, 167, 121, 56), width=max(2, s // 60))
    gold_text(img, (c, c + s * 0.02), '963', ImageFont.truetype(F_BOLD, int(s * 0.34)))
    img = img.resize((size, size), Image.LANCZOS)
    if rounded:
        m = Image.new('L', (size * 4, size * 4), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size * 4 - 1, size * 4 - 1], radius=size * 4 * 0.23, fill=255)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0), m.resize((size, size), Image.LANCZOS))
        return out
    return img


def og():
    W, H = 1200, 630
    img = gradient(W, H, [(11, 90, 77), (5, 66, 57), (0, 32, 29)])
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([700, -250, 1350, 400], fill=(125, 184, 173, 70))
    ImageDraw.Draw(glow).ellipse([-200, 380, 400, 900], fill=(217, 201, 156, 40))
    img = Image.alpha_composite(img.convert('RGBA'), glow.filter(ImageFilter.GaussianBlur(90)))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pattern(ImageDraw.Draw(lay), W, H, 64, (185, 167, 121, 30))
    img = Image.alpha_composite(img, lay)
    ic = icon(260)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([96, 205, 356, 465], radius=60, fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(28)))
    img.paste(ic, (90, 180), ic)
    d = ImageDraw.Draw(img)
    d.text((420, 190), '963', font=ImageFont.truetype(F_BOLD, 120), fill=(244, 241, 230))
    d.text((424, 335), 'Cars · Homes · Goods · Equipment · Services', font=ImageFont.truetype(F_SEMI, 34), fill=(217, 201, 156))
    if features.check('raqm'):
        d.text((424, 392), 'سيارات · عقارات · أغراض · معدات · خدمات', font=ImageFont.truetype(F_AR, 34),
               fill=(196, 207, 201), direction='rtl', language='ar')
        y = 455
    else:
        y = 395
    d.text((424, y), 'One free app for all of Syria  ·  963-app.com', font=ImageFont.truetype(F_SEMI, 26), fill=(160, 180, 172))
    img.convert('RGB').save(os.path.join(A, 'og-image.png'), optimize=True)


if __name__ == '__main__':
    icon(180, rounded=False).save(os.path.join(A, 'apple-touch-icon.png'), optimize=True)
    icon(192).save(os.path.join(A, 'icon-192.png'), optimize=True)
    icon(512).save(os.path.join(A, 'icon-512.png'), optimize=True)
    og()
    print('images written; raqm:', features.check('raqm'))
