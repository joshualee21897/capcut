"""LinkedIn-style 'I'm happy to share' post card (end card for career / LinkedIn themed videos)."""
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from style import font, emoji, sticker, EMOJI_CODES


def linkedin_post(photo_path, details, name='Your Name', headline='Professional holiday-goer · open to new photos',
                  lead="I'm happy to share that I have a", bold='new profile photo', likes='Josh and 1,024 others',
                  cw=900, photo_h=560):
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    photo = ImageOps.exif_transpose(Image.open(photo_path)).convert('RGB')
    ui, uib, small = font('info', 30), font('info_bold', 32), font('info', 24)
    card = Image.new('RGBA', (cw, 1600), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw, 1600), 28, fill=(255, 255, 255, 250))
    av = ImageOps.fit(photo, (96, 96), centering=(0.5, 0.25))
    m = Image.new('L', (96, 96), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 96, 96), fill=255)
    card.paste(av, (32, 30), m)
    d.text((146, 40), name, font=uib, fill=(20, 20, 20))
    d.text((146, 80), headline, font=small, fill=(100, 100, 100))
    d.text((146, 108), 'now', font=small, fill=(140, 140, 140))
    d.text((32, 160), lead, font=ui, fill=(20, 20, 20))
    d.text((32, 200), bold, font=uib, fill=(20, 20, 20))
    card.alpha_composite(sticker('🎉', 52, 4), (int(32 + uib.getlength(bold) + 6), 186))
    y = 262
    for e, t in details:
        card.alpha_composite(emoji(e if e in EMOJI_CODES else '✨', 34), (32, y))
        d.text((80, y + 17), t, font=small, fill=(40, 40, 40), anchor='lm')
        y += 46
    card.paste(ImageOps.fit(photo, (cw - 64, photo_h), centering=(0.5, 0.3)), (32, y + 14))
    y += photo_h + 30
    for i, e in enumerate(['👍', '❤️', '👏']):
        card.alpha_composite(emoji(e, 34), (32 + i * 26, y + 4))
    d.text((124, y + 21), likes, font=small, fill=(100, 100, 100), anchor='lm')
    d.line((32, y + 54, cw - 32, y + 54), fill=(225, 225, 225), width=2)
    for i, t in enumerate(['Like', 'Comment', 'Repost', 'Send']):
        d.text((90 + i * 215, y + 90), t, font=uib, fill=(100, 100, 100), anchor='mm')
    card = card.crop((0, 0, cw, y + 140))
    out = Image.new('RGBA', (card.width + 40, card.height + 50), (0, 0, 0, 0))
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    sh.putalpha(card.split()[3].point(lambda v: v // 3))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), (28, 36))
    out.alpha_composite(card, (20, 20))
    return out
