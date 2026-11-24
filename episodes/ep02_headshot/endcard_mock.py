"""Mock-up: LinkedIn-style 'I'm happy to share' post as the end card (replaces the receipt for this episode)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from style import *

F = '/home/user/footage_ep2/'
OUT = Path(__file__).parent
bg = Image.open(sys.argv[1]).convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(16))
im = ImageEnhance.Brightness(bg).enhance(0.55).convert('RGBA')
photo = ImageOps.exif_transpose(Image.open(F + 'IMG_8002.JPG')).convert('RGB')

cw, x0, y0 = 900, 90, 360
ui, uib = font('info', 30), font('info_bold', 32)
small = font('info', 24)
card = Image.new('RGBA', (cw, 1400), (0, 0, 0, 0))
d = ImageDraw.Draw(card)
d.rounded_rectangle((0, 0, cw, 1400), 28, fill=(255, 255, 255, 250))
# header: avatar + generic name
av = ImageOps.fit(photo, (96, 96), centering=(0.5, 0.25))
m = Image.new('L', (96, 96), 0); ImageDraw.Draw(m).ellipse((0, 0, 96, 96), fill=255)
card.paste(av, (32, 30), m)
d.text((146, 40), 'Your Name', font=uib, fill=(20, 20, 20))
d.text((146, 80), 'Professional holiday-goer · open to new photos', font=small, fill=(100, 100, 100))
d.text((146, 108), 'now', font=small, fill=(140, 140, 140))
# post body
d.text((32, 160), "I'm happy to share that I have a", font=ui, fill=(20, 20, 20))
d.text((32, 200), 'new profile photo', font=uib, fill=(20, 20, 20))
card.alpha_composite(sticker('🎉', 52, 4), (300, 186))
lines = [('📍', 'Holo Face, Bangkok'), ('📸', 'Professional Portrait · 3 retouched photos'),
         ('💸', 'THB 3,888'), ('💄', 'hair, makeup, styling + outfits included'), ('⚡', 'edits back the same day')]
y = 262
for e, t in lines:
    card.alpha_composite(emoji(e, 34) if e in EMOJI_CODES else emoji('✨', 34), (32, y))
    d.text((80, y + 17), t, font=small, fill=(40, 40, 40), anchor='lm')
    y += 46
# post image
ph = ImageOps.fit(photo, (cw - 64, 560), centering=(0.5, 0.3))
card.paste(ph, (32, y + 14))
y += 590
# reactions row
for i, e in enumerate(['👍', '❤️', '👏']):
    card.alpha_composite(emoji(e, 34), (32 + i * 26, y + 4))
d.text((124, y + 21), 'Josh and 1,024 others', font=small, fill=(100, 100, 100), anchor='lm')
d.line((32, y + 54, cw - 32, y + 54), fill=(225, 225, 225), width=2)
for i, t in enumerate(['Like', 'Comment', 'Repost', 'Send']):
    d.text((90 + i * 215, y + 90), t, font=uib, fill=(100, 100, 100), anchor='mm')
card = card.crop((0, 0, cw, y + 140))
sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); sh.putalpha(card.split()[3].point(lambda v: v // 3))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), (x0 + 8, y0 + 16))
im.alpha_composite(card, (x0, y0))
text(im, (W // 2 - 60, 140), 'NEW PFP', font('bootzy', 120), 'white', shadow=12)
text(im, (W // 2 + 40, 250), 'UNLOCKED', font('bootzy', 130), BUTTER, shadow=12)
im.alpha_composite(sticker('🔓', 110), (790, 50))
im.alpha_composite(sticker('💼', 100), (70, 200))
im.convert('RGB').save(OUT / 'endcard_mock.jpg', quality=90)
print('ok')
