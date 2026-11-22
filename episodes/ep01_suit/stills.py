"""Render approval stills for ep 1: centred series intro + end info card."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from style import *

S = Path(sys.argv[1])          # dir holding extracted frames
OUT = Path(__file__).parent

# --- 1. Series intro, centred -------------------------------------------------
im = backdrop(Image.open(S / 'f_intro.png'), blur=14, dim=0.6)
cy = H // 2
text(im, (W // 2, cy - 90), 'AbsolutLEE I DO', font('bootzy', 150), BUTTER, shadow=14)
text(im, (W // 2, cy + 20), 'wedding diaries · ep 1', font('caption', 54), 'white', shadow=8)
text(im, (W // 2, cy + 140), "joshua's suit", font('script', 130), 'white', shadow=10)
paste_emoji(im, '✨', (150, cy - 210), 110, 12)
paste_emoji(im, '✨', (930, cy + 200), 90, -10)
paste_emoji(im, '🤵', (870, cy - 260), 120, -8)
paste_emoji(im, '🇹🇭', (170, cy + 270), 100, 10)
im.convert('RGB').save(OUT / 'still_intro.jpg', quality=90)

# --- 2. End info card ---------------------------------------------------------
im = backdrop(Image.open(S / 'f_reveal.png'), blur=20, dim=0.5)
text(im, (W // 2 - 20, 470), 'the details', font('bootzy', 110), BUTTER, shadow=12)
rows = [('📍', "ricky's fashion house, bangkok", None),
        ('💸', 'S$1,038.29', '2 suits, 2 ties, 1 shirt (incl. alterations)'),
        ('🧵', '2 fittings', '30–45 mins each'),
        ('🗓', 'friday visit, monday collect', None),
        ('✅', 'would recommend', 'friendly team, great advice')]
x0, x1, y = 70, 930, 570
row_h = [96 if sub is None else 130 for _, _, sub in rows]
d = ImageDraw.Draw(im)
d.rounded_rectangle((x0, y, x1, y + sum(row_h) + 50), 36, fill=CREAM + (240,))
y += 30
fb, fr = font('info_bold', 40), font('info', 32)
for (e, main, sub), h in zip(rows, row_h):
    paste_emoji(im, e, (x0 + 70, y + h // 2), 64)
    if sub:
        d.text((x0 + 130, y + h // 2 - 22), main, font=fb, fill=INK, anchor='lm')
        d.text((x0 + 130, y + h // 2 + 26), sub, font=fr, fill=(110, 100, 90), anchor='lm')
    else:
        d.text((x0 + 130, y + h // 2), main, font=fb, fill=INK, anchor='lm')
    y += h
text(im, (W // 2 - 50, y + 120), 'ep 2 coming soon', font('caption', 50), 'white', shadow=8)
paste_emoji(im, '✨', (W // 2 + 210, y + 116), 60)
im.convert('RGB').save(OUT / 'still_infocard.jpg', quality=90)
print('ok')
