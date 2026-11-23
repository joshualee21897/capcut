"""Ep 1 edit. Without a voiceover file, sections are timed to estimated VO length and the
script runs as placeholder karaoke captions. Pass a VO path later to re-time to the real read.

usage: python3 episodes/ep01_suit/render.py <out.mp4> [vo.wav]
"""
import sys
from pathlib import Path
from PIL import Image
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
HIGHLIGHT = {'yes', 'bangkok', "ricky's", 'fashion', 'house', 'boldest', 'pink', 'flamingos', 'party', 'inside',
             'skeleton', 'perfectly', 'beer', 'twenty-six', 'five', 'baht', 'percent', 'save', 'absolutlee', 'do'}
DUR = [11.5, 10, 19, 16.5, 16, 8, 9, 7]          # estimated seconds per paragraph
T = [sum(DUR[:i]) for i in range(len(DUR) + 1)]
TITLE_LEN = 4.0

S = Shot
shots = [
    # P1 proposal recap -> "what i'm wearing"
    S(P + 'IMG_1401.MOV', 2.5, ss=3), S(P + 'IMG_5387.MOV', 2.5, ss=125, trans='zoomblur'),
    S(P + 'IMG_5387.MOV', 2.5, ss=196, trans='flash'), S(v(2121), 2.0, ss=3, trans='whip'),
    S(v(2336), 2.0, ss=50, trans='punch'),
    # P2 title over moving footage + bangkok
    S(v(2004), TITLE_LEN, ss=6.0, zoom=(1.0, 1.06), trans='zoomblur'), S(v(1963), 3.0, ss=9, trans='slide'),
    S(v(1963), 3.0, ss=12.5, trans='punch'),
    # P3 ricky's, styles, burgundy shades
    S(v(1966), 2.5, ss=0, trans='whip'), S(v(1967), 1.5, ss=3, trans='punch'), S(v(1968), 2.5, ss=1, trans='zoomblur'),
    S(v(1976), 2.0, ss=1, trans='whip'), S(v(1975), 2.5, ss=1, trans='slide'), S(v(1971), 2.0, ss=4, trans='punch'),
    S(v(1972), 2.0, ss=2, trans='whip'), S(v(1974), 2.0, ss=2, trans='punch'), S(v(1972), 2.0, ss=6, soft=0.35, trans='flash'),
    # P4 measurements + linings
    S(v(1977), 3.0, ss=3, trans='zoomblur'), S(v(1994), 2.0, ss=3, trans='punch'), S(v(1979), 1.5, ss=0, trans='whip'),
    S(v(1983), 3.0, ss=8, trans='slide'), S(v(1983), 1.5, ss=14, soft=0.35, trans='flash'),
    S(v(2340), 2.5, ss=6, trans='zoomblur'), S(v(1989), 1.5, ss=2, soft=0.35, trans='flash'),
    S(v(1988), 1.5, ss=1, trans='punch'),
    # P5 fitting + alterations
    S(v(1999), 2.5, ss=0, trans='whip'), S(v(2004), 2.5, ss=1, trans='punch'), S(v(2005), 2.5, ss=2, trans='zoomblur'),
    S(v(2006), 2.5, ss=26, trans='slide'), S(v(2121), 2.0, ss=6, trans='whip'), S(v(2335), 2.0, ss=2, trans='punch'),
    S(v(2006), 2.0, ss=8, trans='zoomblur'),
    # P6 monday reveal + beer
    S(v(2336), 3.0, ss=74, trans='flash'), S(v(2337), 2.5, ss=1, trans='punch'), S(v(2338), 2.5, ss=2, trans='whip'),
    # P7 ties, collection, receipt (over moving footage) through P8
    S(v(2341), 1.2, ss=0, trans='zoomblur'), S(v(2342), 1.8, ss=2, trans='punch'), S(v(2352), 3.0, ss=1.5, trans='whip'),
    S(v(2336), 10.0, ss=58, soft=0.45, zoom=(1.0, 1.04), trans='flash'),
]
assert abs(sum(s.dur for s in shots) - T[-1]) < 0.01, (sum(s.dur for s in shots), T[-1])
st = [sum(s.dur for s in shots[:i]) for i in range(len(shots))]

ov, sfx = [], []
hit = lambda name, t, vol=0.5: sfx.append((SFX + name + '.wav', max(t, 0), vol))


def pop(ch, t, pos, size=180, dur=1.8, wob=8, sound='pop'):
    ov.append(Overlay(t, t + dur, sticker(ch, size), pos, 'bounce', wob))
    hit(sound, t, 0.55)


def tag_in(label, t0, t1, pos, ch=None, size=44):
    ov.append(Overlay(t0, t1, sprite_tag(label, size, ch), pos, 'bounce'))
    hit('click', t0, 0.7)


def photo_in(path, t0, t1, angle=-4):
    ov.append(Overlay(t0, t1, polaroid(path, angle=angle), (W / 2, H / 2 - 80), 'drop'))
    hit('shutter', t0 + 0.35, 0.6)


# --- title: animates in line by line over the playing clip ------------------------
t_title = T[1]
dim, parts = series_title_parts('[ ep 1: custom suits ]', cy=H // 2 + 60)
ov.append(Overlay(t_title, t_title + TITLE_LEN, dim, (0, 0), 'fade', full=True))
hit('swoosh_up', t_title - 0.35, 0.6)
delays = {'tag1': 0.15, 'absolutlee': 0.45, 'i': 0.8, 'd': 0.95, 'ring': 1.2, 'tag2': 1.55,
          'emoji0': 1.8, 'emoji1': 1.9, 'emoji2': 2.0, 'emoji3': 2.1, 'emoji4': 2.2}
for name, spr, c in parts:
    t0 = t_title + delays[name]
    anim = 'bounce' if name.startswith('emoji') or name == 'ring' else 'pop'
    ov.append(Overlay(t0, t_title + TITLE_LEN, spr, c, anim, 4 if name.startswith('emoji') else 0))
    if name in ('tag1', 'tag2'):
        hit('click', t0, 0.7)
    elif name in ('absolutlee', 'i', 'd'):
        hit('thud', t0, 0.7)
    elif name == 'ring':
        hit('sparkle', t0, 0.7)
    elif name.startswith('emoji'):
        hit('tick', t0, 0.5)

# --- karaoke captions (placeholder timing until the VO exists) --------------------
for k in karaoke_from_script(SCRIPT, T[:-1], T[1:], highlight=HIGHLIGHT):
    if not (t_title <= k.t0 < t_title + TITLE_LEN - 0.5):          # keep the title card clean
        ov.append(k)

# --- beats linked to what's on screen -------------------------------------------
pop('💍', T[0] + 5.2, (770, 560), 200, sound='sparkle')
pop('👀', T[0] + 7.7, (790, 620))
pop('✈️', st[6] + 0.5, (760, 520), 190, sound='whoosh')
tag_in("ricky's fashion house, sukhumvit", st[8] + 0.2, st[8] + 4.0, (W / 2, 560), '📍')
tag_in('black · single-breasted', st[12] + 0.1, st[14] + 1.6, (W / 2, 520), '🤵')
tag_in('burgundy · double-breasted, 4 buttons', st[12] + 0.7, st[14] + 1.6, (W / 2, 620), '👔')
for i in range(10, 16):
    hit('tick', st[i], 0.35)                                       # montage ticks on fabric cuts
photo_in(ph(1973), st[16], st[17])
pop('🔥', st[16] + 0.9, (820, 430))
hit('zip', st[17] + 0.2, 0.6)
pop('📏', st[17] + 0.6, (780, 520))
hit('scribble', st[19], 0.5)
pop('🦩', st[20] + 0.3, (790, 540), 210, 2.6, sound='sparkle')
photo_in(ph(1980), st[21], st[22], 4)
pop('🥳', st[22] + 0.4, (820, 520), 190)
photo_in(ph(1985), st[23], st[24], -3)
tag_in('fitting', st[25] + 0.1, st[27], (W / 2, 560), '🧵', 48)
tag_in('alterations', st[29] + 0.1, st[31], (W / 2, 560), '✂️', 48)
hit('snip', st[29] + 0.3, 0.7)
pop('💪', st[31] + 0.6, (790, 560), 190, sound='thud')
hit('riser', st[32] - 1.2, 0.5)
pop('😍', st[32] + 0.6, (850, 1060), 190, sound='sparkle')
pop('🍺', st[33] + 0.3, (770, 560), 210, 2.2, sound='clink')
hit('whoosh', st[34], 0.4)
pop('🎉', st[36] + 0.4, (790, 520), 200)

# receipt prints up over moving footage, cha-ching on the total, then save sticker
rc = receipt_sprite("ricky's fashion house", 'sukhumvit soi 3, bangkok', 'fri 6 nov  –  mon 9 nov',
                    [('2x two-piece suit', ''), ('   black, single-breasted', ''), ('   burgundy, double-breasted', ''),
                     ('1x shirt', ''), ('2x tie', '')],
                    'THB 26,500', '≈ S$1,038.29',
                    ['* price includes 1 fitting', '  & all alterations', '* sgd based on exchange rate'])
rc = rc.resize((int(rc.width * 0.85), int(rc.height * 0.85)), Image.LANCZOS)   # leave room for captions
ov.append(Overlay(st[37] + 0.3, T[-1], rc, (W / 2, H / 2 - 150), 'slide_up'))
hit('printer', st[37] + 0.3, 0.6)
hit('chaching', st[37] + 1.0, 0.6)
tag_in('save for later', T[7] + 1.5, T[-1], (W / 2, 1590), '🔖', 50)

# transition sounds
for s, t in zip(shots, st):
    if s.trans == 'whip':
        hit('whoosh', t - 0.1, 0.45)
    elif s.trans == 'zoomblur':
        hit('swoosh_up', t - 0.25, 0.35)
    elif s.trans == 'slide':
        hit('whoosh', t - 0.05, 0.35)
    elif s.trans == 'flash':
        hit('shutter', t, 0.55)

out = sys.argv[1]
vo = sys.argv[2] if len(sys.argv) > 2 else None
total = render(shots, ov, sfx, [], out, vo)
print('rendered', out, f'{total:.1f}s')
