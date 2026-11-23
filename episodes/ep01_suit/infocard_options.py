"""Three info-card style options (all centred) for the end of the episode."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from style import *

S = Path(sys.argv[1])
OUT = Path(__file__).parent
BG = Image.open(S / 'f_reveal.png').convert('RGB').resize((W, H))


def base(dim=0.7):
    return ImageEnhance.Brightness(BG).enhance(dim).convert('RGBA')


def emoji_tag(img, cy, ch, s, size=44):
    """Light-blue sticker tag with an emoji, centred horizontally."""
    f = font('caption_reg', size)
    e = size + 14
    w, h = int(f.getlength(s)) + e + 66, size + 34
    x = (W - w) // 2
    ImageDraw.Draw(img).rectangle((x, cy - h // 2, x + w, cy + h // 2), fill=TAG_BG)
    paste_emoji(img, ch, (x + 22 + e / 2, cy), e)
    ImageDraw.Draw(img).text((x + 34 + e, cy), s, font=f, fill=TAG_FG, anchor='lm')


# --- A: stacked sticker tags (matches the series title tags) -------------------
im = base(0.75)
rows = [('📍', "ricky's fashion house, bangkok"), ('💸', 'S$1,038.29 all in'),
        ('👔', '2 two-piece suits, 1 shirt, 2 ties'), ('🧵', '2 fittings, alterations incl.'),
        ('🗓', 'friday visit, monday collect'), ('✅', 'would recommend!')]
gap = 100
y0 = H // 2 - gap * (len(rows) - 1) // 2
for i, (e, s) in enumerate(rows):
    emoji_tag(im, y0 + i * gap, e, s)
im.convert('RGB').save(OUT / 'info_A_tags.jpg', quality=90)

# --- B: receipt -----------------------------------------------------------------
im = base(0.6)
mono = lambda n: ImageFont.truetype(str(FONTS / 'CourierPrime-Regular.ttf'), n)
rw, rh = 700, 985
r = Image.new('RGBA', (rw, rh + 30), (0, 0, 0, 0))
d = ImageDraw.Draw(r)
d.rectangle((0, 0, rw, rh), fill=(253, 251, 245))
for x in range(0, rw, 30):                                   # zig-zag torn edge
    d.polygon([(x, rh), (x + 15, rh + 22), (x + 30, rh)], fill=(253, 251, 245))
ink, soft = (45, 42, 38), (120, 112, 104)
hdr, hs = "ricky's fashion house", 90
while font('bootzy', hs).getlength(hdr) > rw - 90:      # shrink to fit on one line
    hs -= 2
d.text((rw / 2, 95), hdr, font=font('bootzy', hs), fill=ink, anchor='mm')
d.text((rw / 2, 160), 'sukhumvit soi 3, bangkok', font=mono(30), fill=soft, anchor='mm')
d.text((rw / 2, 205), 'fri 6 nov  –  mon 9 nov', font=mono(30), fill=soft, anchor='mm')
dash = lambda y: [d.line((x, y, x + 14, y), fill=soft, width=3) for x in range(50, rw - 50, 26)]
dash(255)
items = [('2x two-piece suit', ''), ('   black, single-breasted', ''), ('   burgundy, double-breasted', ''),
         ('1x shirt', ''), ('2x tie', '')]
y = 310
for a, b in items:
    small = a.startswith('   ')
    d.text((60, y), a.strip() if not small else '  ' + a.strip(), font=mono(28 if small else 34),
           fill=soft if small else ink, anchor='lm')
    if b:
        d.text((rw - 60, y), b, font=mono(34), fill=ink, anchor='rm')
    y += 48 if small else 58
dash(y + 5)
d.text((60, y + 65), 'TOTAL', font=mono(44), fill=ink, anchor='lm')
d.text((rw - 60, y + 65), 'THB 26,500', font=mono(44), fill=ink, anchor='rm')
d.text((rw - 60, y + 112), '≈ S$1,038.29', font=mono(30), fill=soft, anchor='rm')
y += 45
dash(y + 125)
d.text((rw / 2, y + 160), '* price includes 2 fittings', font=mono(24), fill=soft, anchor='mm')
d.text((rw / 2, y + 192), '  & all alterations', font=mono(24), fill=soft, anchor='mm')
d.text((rw / 2, y + 224), '* sgd based on exchange rate', font=mono(24), fill=soft, anchor='mm')
y += 32
rec, ef, eg = 'would recommend', mono(34), 48                # centre text + emoji as one unit
rx = (rw - (ef.getlength(rec) + 12 + eg)) / 2
d.text((rx, y + 255), rec, font=ef, fill=ink, anchor='lm')
r.alpha_composite(emoji('✅', eg), (int(rx + ef.getlength(rec) + 12), int(y + 255 - eg / 2)))
r = r.rotate(-3, resample=Image.BICUBIC, expand=True)
sh = Image.new('RGBA', r.size, (0, 0, 0, 0))
sh.paste((0, 0, 0, 110), mask=r.split()[3])
sh = sh.filter(ImageFilter.GaussianBlur(18))
x, y = (W - r.width) // 2, (H - r.height) // 2
im.alpha_composite(sh, (x + 10, y + 18))
im.alpha_composite(r, (x, y))
im.convert('RGB').save(OUT / 'info_B_receipt.jpg', quality=90)

# --- C: frosted glass panel -----------------------------------------------------
im = base(0.8)
pw, ph = 860, 760
px, py = (W - pw) // 2, (H - ph) // 2
glass = BG.crop((px, py, px + pw, py + ph)).filter(ImageFilter.GaussianBlur(30))
glass = Image.blend(glass, Image.new('RGB', glass.size, (255, 255, 255)), 0.28).convert('RGBA')
mask = Image.new('L', (pw, ph), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), 48, fill=255)
im.paste(glass, (px, py), mask)
ImageDraw.Draw(im).rounded_rectangle((px, py, px + pw, py + ph), 48, outline=(255, 255, 255, 140), width=3)
rows = [('📍', "ricky's fashion house", 'sukhumvit, bangkok'), ('💸', 'S$1,038.29', '2 two-piece suits, 1 shirt, 2 ties'),
        ('🧵', '2 fittings', 'alterations included'), ('🗓', 'friday → monday', '4 days start to finish'),
        ('✅', 'would recommend', 'friendly team, great advice')]
fb, fr = font('info_bold', 42), font('info', 32)
rh_ = ph // len(rows)
for i, (e, a, b) in enumerate(rows):
    cy = py + rh_ * i + rh_ // 2
    paste_emoji(im, e, (px + 85, cy), 66)
    text(im, (px + 150, cy - 22), a.replace('→', 'to'), fb, 'white', anchor='lm', shadow=6, shadow_alpha=120)
    text(im, (px + 150, cy + 26), b, fr, (255, 255, 255, 230), anchor='lm', shadow=6, shadow_alpha=120)
im.convert('RGB').save(OUT / 'info_C_glass.jpg', quality=90)

# side-by-side preview
prev = Image.new('RGB', (W * 3 + 80, H), (20, 20, 20))
for i, n in enumerate(['info_A_tags', 'info_B_receipt', 'info_C_glass']):
    prev.paste(Image.open(OUT / f'{n}.jpg'), (i * (W + 40), 0))
prev.resize((prev.width // 2, H // 2)).save(OUT / 'infocard_options.jpg', quality=88)
print('ok')
