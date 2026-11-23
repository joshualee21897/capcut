"""Receipt end card (series standard). Returns an RGBA sprite incl. drop shadow."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from style import FONTS, font, emoji

PAPER, INK, SOFT = (253, 251, 245), (45, 42, 38), (120, 112, 104)


def mono(n):
    return ImageFont.truetype(str(FONTS / 'CourierPrime-Regular.ttf'), n)


def receipt_sprite(header, address, dates, items, total, total_alt=None, fineprint=(),
                   rec='would recommend', rw=700, angle=-3):
    # measure height first
    rh = 255 + 55 + sum(48 if a.startswith('   ') else 58 for a, _ in items) + 70 + (45 if total_alt else 0) \
         + 125 + 32 * len(fineprint) + 110
    r = Image.new('RGBA', (rw, rh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(r)
    d.rectangle((0, 0, rw, rh), fill=PAPER)
    for x in range(0, rw, 30):                                       # torn zig-zag edge
        d.polygon([(x, rh), (x + 15, rh + 22), (x + 30, rh)], fill=PAPER)
    hs = 90
    while font('bootzy', hs).getlength(header) > rw - 90:
        hs -= 2
    d.text((rw / 2, 95), header, font=font('bootzy', hs), fill=INK, anchor='mm')
    d.text((rw / 2, 160), address, font=mono(30), fill=SOFT, anchor='mm')
    d.text((rw / 2, 205), dates, font=mono(30), fill=SOFT, anchor='mm')
    dash = lambda y: [d.line((x, y, x + 14, y), fill=SOFT, width=3) for x in range(50, rw - 50, 26)]
    dash(255)
    y = 310
    for a, b in items:
        small = a.startswith('   ')
        d.text((60, y), ('  ' + a.strip()) if small else a, font=mono(28 if small else 34),
               fill=SOFT if small else INK, anchor='lm')
        if b:
            d.text((rw - 60, y), b, font=mono(34), fill=INK, anchor='rm')
        y += 48 if small else 58
    dash(y + 5)
    d.text((60, y + 65), 'TOTAL', font=mono(44), fill=INK, anchor='lm')
    d.text((rw - 60, y + 65), total, font=mono(44), fill=INK, anchor='rm')
    if total_alt:
        d.text((rw - 60, y + 112), total_alt, font=mono(30), fill=SOFT, anchor='rm')
        y += 45
    dash(y + 125)
    for i, line in enumerate(fineprint):
        d.text((rw / 2, y + 160 + 32 * i), line, font=mono(24), fill=SOFT, anchor='mm')
    y += 32 * max(0, len(fineprint) - 2)
    ef, eg = mono(34), 48                                           # centre text + emoji together
    rx = (rw - (ef.getlength(rec) + 12 + eg)) / 2
    d.text((rx, y + 255), rec, font=ef, fill=INK, anchor='lm')
    r.alpha_composite(emoji('✅', eg), (int(rx + ef.getlength(rec) + 12), int(y + 255 - eg / 2)))
    r = r.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', r.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 110), mask=r.split()[3])
    out = Image.new('RGBA', (r.width + 40, r.height + 50), (0, 0, 0, 0))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (20, 30))
    out.alpha_composite(r, (10, 12))
    return out
