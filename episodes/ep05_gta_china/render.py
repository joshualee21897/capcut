"""'how was your trip to china?' -> 'me in china:' game-style trend (TikTok).

Timing copied from the reference (same trending sound): hook dips to black at 4.5s, then 8 scenes cut on the
beat, ending at 13.0s. Exported silent; the trending sound is added in TikTok.
usage: EDIT_SCALE=1 python3 episodes/ep05_gta_china/render.py <hook_video> [out.mp4] [hook_in_point]
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
os.environ.setdefault('EDIT_LOOK', 'mid_warm')
from editor import *          # noqa
from PIL import ImageFont

G = '/home/user/footage_gta/'
HOOK = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else 'renders/ep05_gta_china_preview.mp4'
HOOK_SS = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

# scene files (as uploaded): 1 taobao, 2 crayfish, 3 hanfu, 4 zootopia, 5 bathhouse, 6 bund, 7 toilet, 8 alipay
ORDER = [1, 8, 2, 6, 3, 4, 5, 7]                       # squat toilet last
CUTS = [4.5, 5.667, 6.967, 8.0, 8.933, 9.9, 11.033, 12.0, 13.0]

shots = [Shot(HOOK, CUTS[0], HOOK_SS, zoom=(1.0, 1.0))]
for n, (a, b) in zip(ORDER, zip(CUTS, CUTS[1:])):
    shots.append(Shot(G + f'scene_{n}.png', b - a, zoom=(1.0, 1.0)))


class Dip(Overlay):
    """Dip to black around the hook -> scenes cut (reference: 4.2 -> 4.5 down, 4.5 -> 4.8 up)."""
    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        mid = (self.t0 + self.t1) / 2
        a = 1 - abs(t - mid) / (mid - self.t0)
        canvas.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * max(0, min(a, 1))))))


f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 58)


def label(s):
    """Plain TikTok-style white text with a thin dark outline + soft shadow so it reads on busy images."""
    l, t_, r, b_ = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), s, font=f, anchor='lt', stroke_width=3)
    im = Image.new('RGBA', (r - l + 40, b_ - t_ + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((20 - l, 20 - t_), s, font=f, fill=(0, 0, 0, 150), anchor='lt', stroke_width=3, stroke_fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((20 - l, 20 - t_), s, font=f, fill=(255, 255, 255), anchor='lt',
                            stroke_width=3, stroke_fill=(20, 20, 20, 200))
    return im


hook_txt = label('how was your trip to china?')
me_txt = label('me in china:')
ov = [Dip(4.2, 4.8, hook_txt, (0, 0), 'none', full=True),
      Overlay(0.0, CUTS[0], hook_txt, (W / 2, 330), 'none', fade_out=False),
      Overlay(CUTS[0], CUTS[-1], me_txt, (W / 2, 330), 'none', fade_out=False)]

render(shots, ov, [], [], OUT, total=CUTS[-1])         # silent: trending sound goes on in TikTok
print('wrote', OUT)
