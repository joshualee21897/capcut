"""Ep 1 edit. Without a voiceover file, sections are timed to estimated VO length and the
script is shown as placeholder captions. Pass a VO path later to re-time to the real read.

usage: python3 episodes/ep01_suit/render.py <out.mp4>
"""
import sys, subprocess
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from editor import *
from receipt import receipt_sprite

F = '/home/user/footage/'
P = '/home/user/footage_proposal/'
SFX = str(Path(__file__).resolve().parents[2] / 'assets' / 'sfx') + '/'
v = lambda n: F + f'IMG_{n}.MOV'
ph = lambda n: F + f'IMG_{n}.JPG'

SCRIPT = [
    "Last time you saw me, I was on one knee at River Wonders. She said yes. And the first thing on my wedding to-do list? Figure out what I'm wearing.",
    "Welcome to episode one of AbsolutLEE I Do, where we take you through our wedding prep, one decision at a time. And for mine, I flew to Bangkok.",
    "We landed on Friday, and by 5pm I was at Ricky's Fashion House in Sukhumvit, recommended by a friend. I already knew what I wanted: a classic black single-breasted, and a burgundy double-breasted with four buttons. There are a lot of shades of burgundy, so I went with the boldest one.",
    "They took all my measurements, then came my favourite part, the lining. They suggested something fun for the burgundy, so I went with pink flamingos. Serious on the outside, party on the inside. For the black, I picked a white and red pattern.",
    "On Saturday, I came back for my first fitting in a skeleton suit. They also shortened the pants, took in the shirt and adjusted the black suit. I asked for a little extra room too, since I just had surgery and I'm back at the gym.",
    "By Monday, everything fit perfectly. They even handed me a beer while I tried everything on. Thai hospitality at its finest.",
    "Two suits, a shirt and two ties came up to twenty-six five hundred baht, alterations included. Would I recommend them? One hundred percent.",
    "If you're planning to get a custom suit, save this for later and follow us for more wedding prep shenanigans!",
]
DUR = [11.5, 10, 19, 16.5, 16, 8, 9, 7]          # estimated seconds per paragraph
T = [sum(DUR[:i]) for i in range(len(DUR) + 1)]  # paragraph start times

# end-card background: blurred reveal frame
bgp = CACHE / 'endcard_bg.png'
if not bgp.exists():
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '75', '-i', v(2336), '-frames:v', '1',
                    '-vf', f'scale={W}:{H}', str(bgp)], check=True)
    Image.open(bgp).filter(ImageFilter.GaussianBlur(14)).point(lambda x: int(x * 0.65)).save(bgp)
titlebg = CACHE / 'title_bg.png'
if not titlebg.exists():
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '8.5', '-i', v(2004), '-frames:v', '1',
                    '-vf', f'scale={W}:{H}', str(titlebg)], check=True)

S = Shot
shots = [
    # P1 proposal recap -> "what i'm wearing"
    S(P + 'IMG_1401.MOV', 2.5, ss=3), S(P + 'IMG_5387.MOV', 2.5, ss=125, trans='punch'),
    S(P + 'IMG_5387.MOV', 2.5, ss=196, trans='flash'), S(v(2121), 2.0, ss=3, trans='whip'),
    S(v(2336), 2.0, ss=50, trans='punch'),
    # P2 title + bangkok
    S(str(titlebg), 4.0, zoom=(1.0, 1.04), trans='flash'), S(v(1963), 3.0, ss=9, trans='whip'),
    S(v(1963), 3.0, ss=12.5, trans='punch'),
    # P3 ricky's, styles, burgundy shades
    S(v(1966), 2.5, ss=0, trans='whip'), S(ph(1965), 1.5, trans='punch'), S(v(1968), 2.5, ss=1),
    S(v(1976), 2.0, ss=1, trans='whip'), S(v(1975), 2.5, ss=1, trans='punch'), S(v(1971), 2.0, ss=4),
    S(v(1972), 2.0, ss=2, trans='punch'), S(v(1974), 2.0, ss=2), S(ph(1973), 2.0, trans='flash', photo_style='polaroid'),
    # P4 measurements + linings
    S(v(1977), 3.0, ss=3), S(v(1994), 2.0, ss=3, trans='punch'), S(v(1979), 1.5, ss=0),
    S(v(1983), 3.0, ss=8, trans='whip'), S(ph(1980), 1.5, trans='flash', photo_style='polaroid'),
    S(v(2340), 2.5, ss=6, trans='punch'), S(ph(1985), 1.5, trans='flash', photo_style='polaroid'),
    S(v(1988), 1.5, ss=1),
    # P5 fitting + alterations
    S(v(1999), 2.5, ss=0, trans='whip'), S(v(2004), 2.5, ss=1), S(v(2005), 2.5, ss=2, trans='punch'),
    S(v(2006), 2.5, ss=26), S(v(2121), 2.0, ss=6, trans='whip'), S(v(2335), 2.0, ss=2, trans='punch'),
    S(v(2006), 2.0, ss=8),
    # P6 monday reveal + beer
    S(v(2336), 3.0, ss=44, trans='flash'), S(v(2337), 2.5, ss=1, trans='punch'), S(v(2338), 2.5, ss=2),
    # P7 ties, collection, receipt
    S(v(2341), 1.2, ss=0, trans='punch'), S(v(2342), 1.8, ss=2), S(v(2352), 3.0, ss=1.5, trans='whip'),
    S(str(bgp), 3.0 + 7.0, zoom=(1.0, 1.05), trans='flash'),     # receipt runs through P8
]
assert abs(sum(s.dur for s in shots) - T[-1]) < 0.01, (sum(s.dur for s in shots), T[-1])
starts = [sum(s.dur for s in shots[:i]) for i in range(len(shots))]

ov, sfx = [], []
def pop(ch, t, pos, size=130, dur=1.6, wob=6):
    ov.append(Overlay(t, t + dur, sprite_emoji(ch, size), pos, 'pop', wob))
    sfx.append((SFX + 'pop.wav', t, 0.5))

# title card
title = Image.new('RGBA', (W, H), (0, 0, 0, 0))
series_title(title, '[ ep 1: custom suits ]', cy=H // 2 + 60)
ov.append(Overlay(T[1] + 0.15, T[1] + 4.0, title, (0, 0), 'pop', full=True))
sfx += [(SFX + 'sparkle.wav', T[1] + 0.15, 0.6)]

# captions (placeholder timing)
for t0, t1, c in captions_from_script(SCRIPT, T[:-1], T[1:]):
    if T[1] <= t0 < T[1] + 4.0:          # keep the title card clean
        continue
    ov.append(Overlay(t0, t1, sprite_text(c, font('caption', 54), 'white'), (W / 2, 1390), 'none'))

# emoji / tag beats
pop('💍', T[0] + 5.2, (760, 560), 150)
pop('👀', T[0] + 7.7, (780, 600))
pop('✈️', T[1] + 4.6, (760, 520))
ov.append(Overlay(T[2] + 0.2, T[2] + 4.0, sprite_tag("ricky's fashion house, sukhumvit", 44, '📍'), (W / 2, 560), 'pop'))
sfx.append((SFX + 'pop.wav', T[2] + 0.2, 0.5))
ov.append(Overlay(starts[12] + 0.1, starts[14] + 1.6, sprite_tag('black · single-breasted', 44, '🤵'), (W / 2, 520), 'pop'))
ov.append(Overlay(starts[12] + 0.7, starts[14] + 1.6, sprite_tag('burgundy · double-breasted, 4 buttons', 44, '👔'), (W / 2, 620), 'pop'))
sfx += [(SFX + 'pop.wav', starts[12] + 0.1, 0.5), (SFX + 'pop.wav', starts[12] + 0.7, 0.5)]
pop('🔥', starts[16] + 0.3, (800, 480))
pop('📏', starts[17] + 0.4, (760, 520))
pop('🦩', starts[20] + 0.3, (780, 540), 150, 2.6)
ov.append(Overlay(starts[22] + 0.1, starts[22] + 2.4, sprite_text('party on the inside', font('script', 110), BUTTER, 10),
                  (W / 2, 640), 'pop'))
pop('🥳', starts[22] + 0.4, (860, 520))
ov.append(Overlay(starts[25] + 0.1, starts[27], sprite_tag('fitting', 46, '🧵'), (W / 2, 560), 'pop'))
ov.append(Overlay(starts[29] + 0.1, starts[31], sprite_tag('alterations', 46, '✂️'), (W / 2, 560), 'pop'))
sfx += [(SFX + 'pop.wav', starts[25] + 0.1, 0.5), (SFX + 'pop.wav', starts[29] + 0.1, 0.5)]
pop('💪', starts[31] + 0.6, (780, 560))
ov.append(Overlay(starts[32] + 0.3, starts[32] + 3.0, sprite_text('so dapper', font('script', 130), BUTTER, 10),
                  (W / 2, 600), 'pop'))
pop('😍', starts[32] + 0.6, (840, 470))
pop('🍺', starts[33] + 0.3, (760, 560), 150, 2.2)
pop('🎉', starts[36] + 0.4, (780, 520), 140)

# receipt (prints up), then save sticker
rc = receipt_sprite("ricky's fashion house", 'sukhumvit soi 3, bangkok', 'fri 6 nov  –  mon 9 nov',
                    [('2x two-piece suit', ''), ('   black, single-breasted', ''), ('   burgundy, double-breasted', ''),
                     ('1x shirt', ''), ('2x tie', '')],
                    'THB 26,500', '≈ S$1,038.29',
                    ['* price includes 1 fitting', '  & all alterations', '* sgd based on exchange rate'])
ov.append(Overlay(starts[38] + 0.3, T[-1], rc, (W / 2, H / 2 - 40), 'slide_up'))
sfx.append((SFX + 'ding.wav', starts[38] + 1.0, 0.5))
ov.append(Overlay(T[7] + 1.5, T[-1], sprite_tag('save for later', 50, '🔖'), (W / 2, 1600), 'pop'))
sfx.append((SFX + 'pop.wav', T[7] + 1.5, 0.5))

# transition sfx
for s, t in zip(shots, starts):
    if s.trans == 'whip':
        sfx.append((SFX + 'whoosh.wav', max(t - 0.1, 0), 0.45))
    elif s.trans == 'flash':
        sfx.append((SFX + 'shutter.wav', t, 0.6))

out = sys.argv[1]
vo = sys.argv[2] if len(sys.argv) > 2 else None
total = render(shots, ov, sfx, [], out, vo)
print('rendered', out, f'{total:.1f}s')
