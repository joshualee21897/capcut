"""AbsolutLEE brand style helpers (fonts, colours, text with soft shadow, emoji stickers)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
FONTS, EMOJI = ROOT / 'fonts', ROOT / 'assets' / 'emoji_ios'   # Apple (iOS) emoji, 64px source
BUTTER = (255, 236, 150)          # #FFEC96 lighter butter yellow
CREAM = (255, 250, 235)
INK = (40, 36, 30)
W, H = 1080, 1920

EMOJI_CODES = {'📍': '1f4cd', '💸': '1f4b8', '🧵': '1f9f5', '🗓': '1f5d3', '✅': '2705', '✨': '2728',
               '🤵': '1f935', '💍': '1f48d', '🦩': '1f9a9', '🍺': '1f37a', '😍': '1f60d', '🎉': '1f389',
               '👀': '1f440', '📏': '1f4cf', '🇹🇭': '1f1f9-1f1ed', '💛': '1f49b', '✈️': '2708', '👔': '1f454',
               '✂️': '2702', '🥰': '1f970', '❤️': '2764', '📸': '1f4f8', '🤍': '1f90d',
               '👰': '1f470', '💐': '1f490', '🥂': '1f942', '💒': '1f492', '💌': '1f48c', '💕': '1f495',
               '💪': '1f4aa', '🔖': '1f516', '🥳': '1f973', '🔥': '1f525', '🤔': '1f914', '💀': '1f480', '🥹': '1f979', '💗': '1f497', '💃': '1f483', '🧾': '1f9fe', '💯': '1f4af',
               '🍻': '1f37b', '🏋️': '1f3cb', '🔓': '1f513', '💼': '1f4bc', '👍': '1f44d', '👏': '1f44f',
               '💄': '1f484', '⚡': '26a1'}


def font(kind, size):
    f = {
        'bootzy': ('BootzyTM.ttf', None),
        'script': ('GreatVibes-Regular.ttf', None),
        'caption': ('PublicSans-Italic%5Bwght%5D.ttf', 'SemiBold Italic'),
        'caption_reg': ('PublicSans-Italic%5Bwght%5D.ttf', 'Italic'),
        'info': ('BeVietnamPro-Italic.ttf', None),
        'info_bold': ('BeVietnamPro-BoldItalic.ttf', None),
    }[kind]
    ft = ImageFont.truetype(str(FONTS / f[0]), size)
    if f[1]:
        ft.set_variation_by_name(f[1])
    return ft


def text(img, xy, s, f, fill, anchor='mm', shadow=10, shadow_alpha=170):
    """Draw text with a soft dark shadow so it reads on any footage."""
    if shadow:
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text(xy, s, font=f, fill=(0, 0, 0, shadow_alpha), anchor=anchor)
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)))
    ImageDraw.Draw(img).text(xy, s, font=f, fill=fill, anchor=anchor)


def emoji(ch, size):
    e = Image.open(EMOJI / f'{EMOJI_CODES[ch]}.png').convert('RGBA').resize((size, size), Image.LANCZOS)
    return e.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)) if size > 64 else e


def paste_emoji(img, ch, center, size, angle=0):
    e = emoji(ch, size)
    if angle:
        e = e.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(e, (int(center[0] - e.width / 2), int(center[1] - e.height / 2)))


def backdrop(frame, blur=18, dim=0.55):
    """Blurred, dimmed frame for title / info card backgrounds."""
    b = frame.convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), b, dim).convert('RGBA')


# ---------------------------------------------------------------------------
# Series title card: same layout + same wedding emojis for every episode
TAG_BG, TAG_FG = (200, 228, 252, 225), (35, 60, 110)
SERIES_EMOJIS = [('🤵', -0.36, -0.02, 105, -10), ('👰', 0.36, -0.02, 105, 10),   # (emoji, dx, dy, size, angle)
                 ('💐', -0.40, 0.16, 95, 12), ('🥂', 0.40, 0.17, 95, -12),     # dx/dy as fraction of W around centre
                 ('🤍', 0.38, -0.17, 70, 10)]


def tag(img, center, s, size=46, angle=0):
    """[ bracket label ] on a light-blue box."""
    f = font('caption_reg', size)
    w, h = int(f.getlength(s)) + 44, size + 30
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.rectangle((0, 0, w, h), fill=TAG_BG)
    d.text((w / 2, h / 2), s, font=f, fill=TAG_FG, anchor='mm')
    if angle:
        t = t.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(t, (int(center[0] - t.width / 2), int(center[1] - t.height / 2)))


def series_title(im, ep_line, cy=H // 2, series='[ wedding series ]', parts=None):
    """Centred block: tag / absolutlee / i d(ring) / ep tag, plus the fixed wedding emojis.
    parts: optional set of names to draw only some pieces (for animation):
    dim, tag1, absolutlee, i, d, ring, tag2, emoji0..emoji4"""
    on = lambda n: parts is None or n in parts
    if on('dim'):
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        for y in range(H):
            gd.line((0, y, W, y), fill=(0, 0, 0, int(80 * max(0, 1 - abs(y - cy) / 520))))
        im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    f1, f2 = font('bootzy', 170), font('bootzy', 290)
    y1 = cy - 140
    if on('absolutlee'):
        text(im, (W // 2, y1), 'absolutlee', f1, BUTTER, shadow=12)
    a_t, a_b = d.textbbox((W // 2, y1), 'absolutlee', font=f1, anchor='mm')[1::2]
    d_top = d.textbbox((0, 0), 'd', font=f2, anchor='ls')[1]   # negative: ascender height above baseline
    y2 = a_b - d_top + 8                        # baseline of "i do", almost touching "absolutlee"
    o_l, o_t, o_r, o_b = d.textbbox((0, 0), 'o', font=f2, anchor='ls')
    o_w, o_h = o_r - o_l, o_b - o_t
    w_i, w_d = f2.getlength('i'), f2.getlength('d')
    word_gap, o_gap = int(o_w * 0.35), int(o_w * 0.04)
    x = (W - (w_i + word_gap + w_d + o_gap + o_w)) / 2
    if on('i'):
        text(im, (x, y2), 'i', f2, 'white', anchor='ls', shadow=16)
    if on('d'):
        text(im, (x + w_i + word_gap, y2), 'd', f2, 'white', anchor='ls', shadow=16)
    ring = int(o_h * 1.3)
    if on('ring'):
        paste_emoji(im, '💍', (x + w_i + word_gap + w_d + o_gap + o_w / 2, y2 - o_h / 2 - ring * 0.12), ring, -6)
    if on('tag1'):
        tag(im, (W // 2, a_t - 60), series, 46)
    if on('tag2'):
        tag(im, (W // 2, y2 + 80), ep_line, 46)
    for i, (e, dx, dy, size, ang) in enumerate(SERIES_EMOJIS):
        if on(f'emoji{i}'):
            paste_emoji(im, e, (W // 2 + dx * W, cy + dy * W), size, ang)
    return im


TITLE_ORDER = ['tag1', 'absolutlee', 'i', 'd', 'ring', 'tag2', 'emoji0', 'emoji1', 'emoji2', 'emoji3', 'emoji4']


def series_title_parts(ep_line, cy=H // 2, series='[ wedding series ]'):
    """Return (dim_layer, [(name, sprite, centre), ...]) for line-by-line animation."""
    dim = series_title(Image.new('RGBA', (W, H), (0, 0, 0, 0)), ep_line, cy, series, {'dim'})
    out = []
    for n in TITLE_ORDER:
        layer = series_title(Image.new('RGBA', (W, H), (0, 0, 0, 0)), ep_line, cy, series, {n})
        bb = layer.getbbox()
        out.append((n, layer.crop(bb), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)))
    return dim, out


def sticker(ch, size, outline=7):
    """Emoji with a white sticker outline + soft shadow so it pops on any footage."""
    e = emoji(ch, size)
    pad = outline + 16
    c = Image.new('RGBA', (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    c.paste(e, (pad, pad), e)
    a = c.split()[3].point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(outline * 2 + 1))
    out = Image.new('RGBA', c.size, (0, 0, 0, 0))
    sh = Image.new('RGBA', c.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * 0.45))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (0, 0))
    white = Image.new('RGBA', c.size, (255, 255, 255, 0))
    white.putalpha(a.filter(ImageFilter.GaussianBlur(1)))
    out.alpha_composite(white)
    out.alpha_composite(c)
    return out
