"""AbsolutLEE brand style helpers (fonts, colours, text with soft shadow, emoji stickers)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
FONTS, EMOJI = ROOT / 'fonts', ROOT / 'assets' / 'emoji_ios'   # Apple (iOS) emoji, 64px source
BUTTER = (255, 226, 122)          # #FFE27A
CREAM = (255, 250, 235)
INK = (40, 36, 30)
W, H = 1080, 1920

EMOJI_CODES = {'📍': '1f4cd', '💸': '1f4b8', '🧵': '1f9f5', '🗓': '1f5d3', '✅': '2705', '✨': '2728',
               '🤵': '1f935', '💍': '1f48d', '🦩': '1f9a9', '🍺': '1f37a', '😍': '1f60d', '🎉': '1f389',
               '👀': '1f440', '📏': '1f4cf', '🇹🇭': '1f1f9-1f1ed', '💛': '1f49b', '✈️': '2708', '👔': '1f454',
               '✂️': '2702', '🥰': '1f970', '❤️': '2764', '📸': '1f4f8', '🤍': '1f90d'}


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
