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
    f_lead, f_bold = font('info', 27), font('info_bold', 28)
    lw = f_lead.getlength(lead + ' ')
    d.text((32, 178), lead + ' ', font=f_lead, fill=(20, 20, 20), anchor='lm')
    d.text((32 + lw, 178), bold, font=f_bold, fill=(20, 20, 20), anchor='lm')
    card.alpha_composite(sticker('🎉', 46, 4), (int(32 + lw + f_bold.getlength(bold) + 2), 150))
    y = 222
    for e, t in details:
        card.alpha_composite(emoji(e if e in EMOJI_CODES else '✨', 34), (32, y))
        d.text((80, y + 17), t, font=small, fill=(40, 40, 40), anchor='lm')
        y += 46
    box = (cw - 64, photo_h)
    fill = ImageOps.fit(photo, box).filter(ImageFilter.GaussianBlur(25))
    fit = photo.copy()
    fit.thumbnail(box, Image.LANCZOS)                                   # whole photo, never cropped
    fill.paste(fit, ((box[0] - fit.width) // 2, (box[1] - fit.height) // 2))
    card.paste(fill, (32, y + 14))
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


def lanyard_badge(photo_path, title='HEADSHOT', sub='2026 · bangkok', w=300, strap_len=900, angle=0):
    """Corporate ID badge on a lanyard (butter-yellow strap printed with 'absolutlee'), photo not cropped at the head."""
    from style import BUTTER, font, text
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    photo = ImageOps.exif_transpose(Image.open(photo_path)).convert('RGB')
    h = int(w * 1.48)
    card = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w, h), 22, fill=(252, 251, 247, 255))
    d.rounded_rectangle((w / 2 - 34, 16, w / 2 + 34, 30), 7, fill=(205, 205, 205, 255))      # slot
    pw, ph = w - 36, int((w - 36) * 1.2)
    card.paste(ImageOps.fit(photo, (pw, ph), centering=(0.5, 0.18)), (18, 46))               # keep the head in
    d.text((w / 2, 46 + ph + 34), title, font=font('bootzy', 44), fill=(40, 36, 30), anchor='mm')
    d.text((w / 2, 46 + ph + 72), sub, font=font('info', 20), fill=(120, 112, 104), anchor='mm')
    # strap: two ribbons from the clip up out of frame
    sw = 44
    strap = Image.new('RGBA', (w + 160, strap_len), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strap)
    cx = strap.width / 2
    for side in (-1, 1):
        top_x = cx + side * (w / 2 + 40)
        poly = [(cx + side * 6, strap_len), (cx + side * (6 + sw), strap_len), (top_x + side * sw / 2, 0), (top_x - side * sw / 2, 0)]
        sd.polygon(poly, fill=BUTTER + (255,))
    for yy in range(60, strap_len - 80, 150):                                                # printed brand text
        for side in (-1, 1):
            x = cx + side * (6 + sw / 2 + (w / 2 + 40 - 6 - sw / 2) * (1 - yy / strap_len))
            txt = Image.new('RGBA', (140, 34), (0, 0, 0, 0))
            ImageDraw.Draw(txt).text((70, 17), 'absolutlee', font=font('bootzy', 22), fill=(60, 50, 20), anchor='mm')
            txt = txt.rotate(90 if side < 0 else -90, expand=True)
            strap.alpha_composite(txt, (int(x - txt.width / 2), int(yy)))
    sd.rounded_rectangle((cx - 22, strap_len - 18, cx + 22, strap_len + 2), 6, fill=(170, 170, 175, 255))  # metal clip
    out = Image.new('RGBA', (strap.width, strap_len + h - 10), (0, 0, 0, 0))
    out.alpha_composite(strap, (0, 0))
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    sh.putalpha(card.split()[3].point(lambda v: v // 3))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (88, strap_len))
    out.alpha_composite(card, (80, strap_len - 10))
    if angle:
        out = out.rotate(angle, resample=Image.BICUBIC, expand=True, center=(out.width / 2, 0))
    return out
