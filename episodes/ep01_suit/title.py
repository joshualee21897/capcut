"""Opening title frame (also the TikTok cover), in the style of the absolutlee abroad posts."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from style import *

S = Path(sys.argv[1])
OUT = Path(__file__).parent
TAG_BG, TAG_FG = (200, 228, 252, 225), (35, 60, 110)


def tag(img, center, s, size=46, angle=0):
    """[ bracket label ] on a light-blue box, slightly rotated."""
    f = font('caption_reg', size)
    w = int(f.getlength(s)) + 44
    h = size + 30
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.rectangle((0, 0, w, h), fill=TAG_BG)
    d.text((w / 2, h / 2), s, font=f, fill=TAG_FG, anchor='mm')
    t = t.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(t, (int(center[0] - t.width / 2), int(center[1] - t.height / 2)))


im = Image.open(S / 'f_title.png').convert('RGBA').resize((W, H))
# soft top gradient so the title pops off the bright ceiling
g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(g)
for y in range(800):
    gd.line((0, y, W, y), fill=(0, 0, 0, int(80 * (1 - y / 800))))
im.alpha_composite(g)

tag(im, (700, 140), '[ wedding series ]', 48, angle=-5)
text(im, (W // 2, 265), 'absolutlee', font('bootzy', 170), BUTTER, shadow=12)
text(im, (W // 2 - 30, 440), 'i do', font('bootzy', 260), 'white', shadow=16)
paste_emoji(im, '💍', (815, 355), 140, -18)
tag(im, (770, 700), '[ ep 1: custom suits ]', 46, angle=3)

paste_emoji(im, '🇹🇭', (120, 175), 110, 8)
paste_emoji(im, '✈️', (235, 100), 100, -15)
paste_emoji(im, '🤵', (175, 450), 105, -10)
paste_emoji(im, '✂️', (120, 760), 90, 15)
paste_emoji(im, '❤️', (985, 240), 80, 12)
im.convert('RGB').save(OUT / 'still_title.jpg', quality=92)
print('ok')
