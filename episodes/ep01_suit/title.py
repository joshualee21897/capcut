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
# gentle dim behind the centred title block
g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(g)
for y in range(H):
    gd.line((0, y, W, y), fill=(0, 0, 0, int(70 * max(0, 1 - abs(y - 960) / 520))))
im.alpha_composite(g)

cy = H // 2 + 70          # centred, nudged below his face
# line 1: "absolutlee", centred
f1 = font('bootzy', 170)
y1 = cy - 160
text(im, (W // 2, y1), 'absolutlee', f1, BUTTER, shadow=12)
a_l, a_t, a_r, a_b = ImageDraw.Draw(im).textbbox((W // 2, y1), 'absolutlee', font=f1, anchor='mm')

# line 2: "i" + "d" + ring-as-o, centred as one unit (custom word gap, Bootzy's space is wide)
f2 = font('bootzy', 290)
y2 = cy + 150                                # baseline
d = ImageDraw.Draw(im)
o_l, o_t, o_r, o_b = d.textbbox((0, 0), 'o', font=f2, anchor='ls')
o_w, o_h = o_r - o_l, o_b - o_t
w_i, w_d = f2.getlength('i'), f2.getlength('d')
word_gap, o_gap = int(o_w * 0.35), int(o_w * 0.04)
total = w_i + word_gap + w_d + o_gap + o_w
x = (W - total) / 2
text(im, (x, y2), 'i', f2, 'white', anchor='ls', shadow=16)
text(im, (x + w_i + word_gap, y2), 'd', f2, 'white', anchor='ls', shadow=16)
ring = int(o_h * 1.3)
ring_cx = x + w_i + word_gap + w_d + o_gap + o_w / 2
paste_emoji(im, '💍', (ring_cx, y2 - o_h / 2 - ring * 0.12), ring, -6)
i_r = x + total

tag(im, (a_l + 150, a_t - 55), '[ wedding series ]', 46, angle=-5)
tag(im, (i_r - 150, y2 + 75), '[ ep 1: custom suits ]', 46, angle=3)

paste_emoji(im, '🇹🇭', (950, a_t - 40), 105, 10)
paste_emoji(im, '✈️', (840, a_t - 95), 95, -15)
paste_emoji(im, '🤵', (130, y2 - 60), 105, -10)
paste_emoji(im, '✂️', (120, y2 + 150), 85, 15)
paste_emoji(im, '❤️', (985, y1 + 30), 75, 12)
im.convert('RGB').save(OUT / 'still_title.jpg', quality=92)
print('ok')
