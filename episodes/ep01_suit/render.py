"""Ep 1 edit. Without a voiceover file, sections are timed to estimated VO length and the
script runs as placeholder karaoke captions. {Braced phrases} become big Bootzy callouts.

usage: python3 episodes/ep01_suit/render.py <out.mp4> [vo.wav]
"""
import sys, os
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from editor import *
from receipt import receipt_sprite

F = '/home/user/footage/'
P = '/home/user/footage_proposal/'
SFX = str(Path(__file__).resolve().parents[2] / 'assets' / 'sfx') + '/'


def v(n):
    for ext in ('.MOV', '.mov'):
        if os.path.exists(F + f'IMG_{n}{ext}'):
            return F + f'IMG_{n}{ext}'
    raise FileNotFoundError(n)


ph = lambda n: F + f'IMG_{n}.JPG'

SCRIPT = [
    "Last time you saw me, I was on one knee at River Wonders. {She said yes.} And the first thing on my wedding to-do list? Figure out what I'm wearing.",
    "Welcome to episode one of AbsolutLEE I Do, where we take you through our wedding prep, one decision at a time. And for mine, I flew to {Bangkok.}",
    "We landed on Friday, and by 5pm I was at {Ricky's Fashion House} in Sukhumvit, recommended by a friend. I already knew what I wanted: a classic black single-breasted, and a burgundy double-breasted with four buttons. There are a lot of shades of burgundy, so I went with {the boldest one.}",
    "They took all my measurements, then came my favourite part, the lining. They suggested something fun for the burgundy, so I went with {pink flamingos.} {Serious on the outside, party on the inside.} For the black, I picked a white and red pattern.",
    "On Saturday, I came back for my first fitting in a {skeleton suit.} They also shortened the pants, took in the shirt and adjusted the black suit. I asked for a little extra room too, since I just had surgery and I'm back at the gym.",
    "By Monday, everything fit perfectly. They even handed me {a beer} while I tried everything on. Thai hospitality at its finest.",
    "Two suits, a shirt and two ties came up to {twenty-six five hundred baht,} alterations included. Would I recommend them? {One hundred percent.}",
    "If you're planning to get a custom suit, save this for later and follow us for more wedding prep shenanigans!",
]
# callout design per emphasised phrase (same order as the braces above)
CALLOUTS = [
    ([('SHE SAID', 100, 'l'), ('YES!', 280, 'r')], '💍'),
    ([('BANGKOK', 210, 'c')], '✈️'),
    ([("RICKY'S", 210, 'c'), ('FASHION HOUSE', 86, 'c')], '📍'),
    ([('THE', 100, 'l'), ('BOLDEST', 220, 'c'), ('ONE', 100, 'r')], '🔥'),
    ([('PINK', 130, 'l'), ('FLAMINGOS', 175, 'c')], '🦩'),
    ([('SERIOUS', 130, 'c'), ('on the outside', 66, 'c'), ('PARTY', 230, 'c'), ('on the inside', 66, 'c')], '🥳'),
    ([('SKELETON', 175, 'c'), ('SUIT', 130, 'r')], '💀'),
    ([('A', 110, 'l'), ('BEER?!', 240, 'c')], '🍺'),
    ([('26,500', 230, 'c'), ('BAHT', 120, 'r')], '💸'),
    ([('100%', 300, 'c')], '✅'),
]
HIGHLIGHT = {'perfectly', 'save'}
DUR = [11.5, 10, 19, 16.5, 16, 8, 9, 7]          # estimated seconds per paragraph
T = [sum(DUR[:i]) for i in range(len(DUR) + 1)]
TITLE_LEN = 4.0

# --- shots (named markers so overlays never drift when the list changes) --------
shots, mark = [], {}


def add(shot, name=None):
    if name:
        mark[name] = sum(s.dur for s in shots)
    shots.append(shot)


S = Shot
# P1 proposal recap -> "what i'm wearing"
add(S(P + 'IMG_1401.MOV', 2.5, ss=3))
add(S(P + 'IMG_5387.MOV', 2.5, ss=125, trans='zoomblur'))
add(S(P + 'IMG_5387.MOV', 2.5, ss=196, trans='flash'), 'yes')
add(S(v(2121), 2.0, ss=3, trans='whip'))
add(S(v(2336), 2.0, ss=50, trans='punch'))
# P2 title over moving footage, then joshua's own selfie in bangkok
add(S(v(2004), TITLE_LEN, ss=6.0, zoom=(1.0, 1.06), trans='zoomblur'), 'title')
add(S(v(1963), 3.0, ss=2.0, trans='slide'))
add(S(v(1963), 3.0, ss=5.0, trans='punch'))
# P3 ricky's, waiting, styles, burgundy shades
add(S(v(1966), 1.5, ss=0, trans='whip'))
add(S(v(1995), 2.0, ss=0.3, trans='punch'), 'sign')
add(S(v(1999), 2.0, ss=15.0, trans='zoomblur'))
add(S(v(1968), 2.0, ss=1, trans='whip'), 'fabric')
add(S(v(1976), 2.0, ss=1, trans='punch'))
add(S(v(1975), 2.5, ss=1, trans='slide'), 'styles')
add(S(v(1971), 1.5, ss=4, trans='punch'))
add(S(v(1972), 2.0, ss=2, trans='whip'))
add(S(v(1974), 1.5, ss=2, trans='punch'))
add(S(v(1972), 2.0, ss=6, soft=0.35, trans='flash'), 'shades')
# P4 measurements + linings
add(S(v(1977), 3.0, ss=3, trans='zoomblur'), 'measure')
add(S(v(1994), 2.0, ss=3, trans='punch'))
add(S(v(1979), 1.5, ss=0, trans='whip'), 'book')
add(S(v(1983), 3.0, ss=8, trans='slide'), 'flamingo')
add(S(v(1984), 1.5, ss=40, soft=0.35, trans='flash'), 'flamingo_photo')
add(S(v(2340), 2.5, ss=6, trans='zoomblur'), 'party')
add(S(v(1989), 1.5, ss=2, soft=0.35, trans='flash'), 'red_photo')
add(S(v(1988), 1.5, ss=1, trans='punch'))
# P5 fitting + alterations (joshua on camera)
add(S(v(1999), 2.0, ss=4, trans='whip'), 'fitting')
add(S(v(2004), 2.5, ss=1, trans='punch'))
add(S(v(2005), 2.5, ss=2, trans='zoomblur'))
add(S(v(2006), 2.0, ss=26, trans='slide'))
add(S(v(2121), 2.0, ss=6, trans='whip'), 'alter')
add(S(v(2333), 2.0, ss=12, trans='punch'))
add(S(v(2335), 1.5, ss=2, trans='zoomblur'))
add(S(v(2011), 1.5, ss=1, trans='punch'), 'gym')
# P6 monday reveal + beer
add(S(v(2336), 3.0, ss=74, trans='flash'), 'reveal')
add(S(v(2337), 2.0, ss=1, trans='punch'), 'beer')
add(S(v(2338), 3.0, ss=2, trans='whip'))
# P7 ties, collection selfies
add(S(v(2341), 1.0, ss=0, trans='zoomblur'), 'ties')
add(S(v(2342), 1.5, ss=2, trans='punch'))
add(S(v(2353), 3.5, ss=2.5, trans='whip'), 'collect')
add(S(v(2352), 3.0, ss=4.0, trans='punch'))
# P8 receipt over moving footage
add(S(v(2336), 7.0, ss=58, soft=0.45, zoom=(1.0, 1.04), trans='flash'), 'receipt')
assert abs(sum(s.dur for s in shots) - T[-1]) < 0.01, (sum(s.dur for s in shots), T[-1])
st = [sum(s.dur for s in shots[:i]) for i in range(len(shots))]

ov, caps, sfx = [], [], []
hit = lambda name, t, vol=0.5: sfx.append((SFX + name + '.wav', max(t, 0), vol))


def pop(ch, t, pos, size=180, dur=1.8, wob=8, sound='pop'):
    ov.append(Overlay(t, t + dur, sticker(ch, size), pos, 'bounce', wob))
    hit(sound, t, 0.55)


def tag_in(label, t0, t1, pos, ch=None, size=44):
    ov.append(Overlay(t0, t1, sprite_tag(label, size, ch), pos, 'bounce'))
    hit('click', t0, 0.7)


def photo_in(path, t0, t1, angle=-4):                   # smaller + higher: never covers captions
    ov.append(Overlay(t0, t1, polaroid(path, width=500, angle=angle), (W / 2, 600), 'drop'))
    hit('shutter', t0 + 0.35, 0.6)


# --- title: animates in line by line over the playing clip ------------------------
t_title = mark['title']
dim, parts = series_title_parts('[ ep 1: custom suits ]', cy=H // 2 + 60)
ov.append(Overlay(t_title, t_title + TITLE_LEN, dim, (0, 0), 'fade', full=True))
hit('swoosh_up', t_title - 0.35, 0.6)
delays = {'tag1': 0.15, 'absolutlee': 0.45, 'i': 0.8, 'd': 0.95, 'ring': 1.2, 'tag2': 1.55,
          'emoji0': 1.8, 'emoji1': 1.9, 'emoji2': 2.0, 'emoji3': 2.1, 'emoji4': 2.2}
for name, spr, c in parts:
    t0 = t_title + delays[name]
    anim = 'bounce' if name.startswith('emoji') or name == 'ring' else 'pop'
    ov.append(Overlay(t0, t_title + TITLE_LEN, spr, c, anim, 4 if name.startswith('emoji') else 0))
    hit({'tag1': 'click', 'tag2': 'click', 'ring': 'sparkle'}.get(name, 'thud' if name in ('absolutlee', 'i', 'd') else 'tick'),
        t0, 0.7 if not name.startswith('emoji') else 0.5)

# --- captions + emphasis callouts -------------------------------------------------
kar, phrases = parse_emphasis(SCRIPT, T[:-1], T[1:], highlight=HIGHLIGHT)
caps += [k for k in kar if not (t_title <= k.t0 < t_title + TITLE_LEN - 0.5)]
CALLOUT_Y = 1060                       # lower-middle: clear of faces/polaroids, above captions
for (txt, p0, p1), (lines, ch) in zip(phrases, CALLOUTS):
    end = max(p1 + 0.7, p0 + 1.4)
    for i, (spr, (dx, dy)) in enumerate(callout_lines(lines, ch)):
        is_emoji = i == len(lines)
        t0 = p0 + (0.12 * i if not is_emoji else 0.12 * len(lines) + 0.05)
        caps.insert(0, Overlay(t0, end, spr, (W / 2 + dx, CALLOUT_Y + dy), 'bounce', 8 if is_emoji else 0))
    hit('thud', p0, 0.7)
    hit('pop', p0 + 0.12 * len(lines) + 0.05, 0.5)

# --- beats linked to what's on screen -------------------------------------------
pop('👀', T[0] + 7.7, (790, 620))
tag_in('black · single-breasted', mark['styles'] + 0.1, mark['styles'] + 5.5, (W / 2, 520), '🤵')
tag_in('burgundy · double-breasted, 4 buttons', mark['styles'] + 0.7, mark['styles'] + 5.5, (W / 2, 620), '👔')
for t in st[st.index(mark['fabric']):st.index(mark['shades'])]:
    hit('tick', t, 0.35)                                       # montage ticks on fabric cuts
photo_in(ph(1973), mark['shades'], mark['measure'])
hit('zip', mark['measure'] + 0.2, 0.6)
pop('📏', mark['measure'] + 0.6, (880, 760))
hit('scribble', mark['book'], 0.5)
photo_in(ph(1980), mark['flamingo_photo'], mark['party'], 4)
photo_in(ph(1985), mark['red_photo'], mark['red_photo'] + 1.5, -3)
tag_in('fitting', mark['fitting'] + 0.1, mark['fitting'] + 4.4, (W / 2, 520), '🧵', 48)
tag_in('alterations', mark['alter'] + 0.1, mark['gym'], (W / 2, 520), '✂️', 48)
hit('snip', mark['alter'] + 0.3, 0.7)
pop('💪', mark['gym'] + 0.4, (790, 560), 190, sound='thud')
hit('riser', mark['reveal'] - 1.2, 0.5)
pop('😍', mark['reveal'] + 0.6, (850, 1060), 190, sound='sparkle')
hit('clink', mark['beer'] + 0.2, 0.6)
hit('whoosh', mark['ties'], 0.4)
pop('🎉', mark['collect'] + 0.4, (790, 520), 200)

# receipt prints up over moving footage (kept above the caption band), then save sticker
rc = receipt_sprite("ricky's fashion house", 'sukhumvit soi 3, bangkok', 'fri 6 nov  –  mon 9 nov',
                    [('2x two-piece suit', ''), ('   black, single-breasted', ''), ('   burgundy, double-breasted', ''),
                     ('1x shirt', ''), ('2x tie', '')],
                    'THB 26,500', '≈ S$1,038.29',
                    ['* price includes 1 fitting', '  & all alterations', '* sgd based on exchange rate'])
rc = rc.resize((int(rc.width * 0.8), int(rc.height * 0.8)), Image.LANCZOS)
ov.append(Overlay(mark['receipt'] + 0.2, T[-1], rc, (W / 2, 120 + rc.height / 2), 'slide_up'))
hit('printer', mark['receipt'] + 0.2, 0.6)
hit('chaching', mark['receipt'] + 0.9, 0.6)
tag_in('save for later', T[7] + 2.0, T[-1], (W / 2, 1580), '🔖', 50)

# transition sounds
for s, t in zip(shots, st):
    sound = {'whip': ('whoosh', -0.1, 0.45), 'zoomblur': ('swoosh_up', -0.25, 0.35),
             'slide': ('whoosh', -0.05, 0.35), 'flash': ('shutter', 0, 0.55)}.get(s.trans)
    if sound:
        hit(sound[0], t + sound[1], sound[2])

out = sys.argv[1]
vo = sys.argv[2] if len(sys.argv) > 2 else None
total = render(shots, ov + caps, sfx, [], out, vo)        # captions drawn last = always on top
print('rendered', out, f'{total:.1f}s')
