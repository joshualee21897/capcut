"""Ep 1 edit, timed to Joshua's cleaned voiceover.

usage: python3 episodes/ep01_suit/render.py <out.mp4>
needs: /home/user/vo/vo_clean.wav + words_clean.json (tools/vo_clean.py), cutouts in /home/user/edit_cache/cutouts
"""
import sys, os, json
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from editor import *
from receipt import receipt_sprite

F, P = '/home/user/footage/', '/home/user/footage_proposal/'
VO_DIR, CUT = '/home/user/vo/', '/home/user/edit_cache/cutouts/'
SFX = str(Path(__file__).resolve().parents[2] / 'assets' / 'sfx') + '/'


def v(n):
    for ext in ('.MOV', '.mov'):
        if os.path.exists(F + f'IMG_{n}{ext}'):
            return F + f'IMG_{n}{ext}'
    raise FileNotFoundError(n)


ph = lambda n: F + f'IMG_{n}.JPG'
norm_w = lambda w: ''.join(c for c in w.lower() if c.isalnum())

SCRIPT = [
    "Last time you saw me, I was on one knee at River Wonders. {She said yes.} And the first thing on my wedding to-do list? Figure out what I'm wearing.",
    "Welcome to episode one of AbsolutLEE I Do, where we take you through our wedding prep, one decision at a time. And for mine, I flew to {Bangkok.}",
    "We landed on Friday, and by 5pm I was at {Ricky's Fashion House} in Sukhumvit, recommended by a friend. I already knew what I wanted: a classic black single-breasted, and a burgundy double-breasted with four buttons. There are a lot of shades of burgundy, so I went with {the boldest one.}",
    "They took all my measurements, then came my favourite part, the lining. They suggested something fun for the burgundy, so I went with {pink flamingos.} {Serious on the outside, party on the inside.} For the black, I picked a white and red pattern.",
    "On Saturday, I came back for my first fitting in a {skeleton suit.} They also shortened the pants, took in the shirt and adjusted the black suit. I asked for a little extra room too, since I just had surgery and I'm back at the gym.",
    "By Monday, everything fit perfectly. They even handed me {a beer} while I tried everything on. Thai hospitality at its finest.",
    "Two suits, a shirt and two ties came up to {twenty-six five hundred baht.} Alterations included. Would I recommend them? {One hundred percent.}",
    "If you're planning to get a custom suit, save this for later and follow us for more wedding prep shenanigans!",
]
CAP_Y, CAP_Y_END = 760, 230          # captions at eye level; moved to the top for the cutout/receipt finale
LOW, HIGH = 1180, 430               # callout bands below / above the caption line
CALLOUTS = [   # (lines, emojis, y) per {phrase}, in order
    ([('SHE SAID', 100, 'l'), ('YES!', 280, 'r')], ['💍', '🥹'], LOW),
    ([('BANGKOK', 200, 'c')], ['✈️', '🇹🇭'], LOW),
    ([("RICKY'S", 210, 'c'), ('FASHION HOUSE', 86, 'c')], ['📍', '🧵'], LOW),
    ([('THE', 100, 'l'), ('BOLDEST', 220, 'c'), ('ONE', 100, 'r')], ['🔥', '👔'], HIGH),   # polaroid sits low
    ([('PINK', 130, 'l'), ('FLAMINGOS', 175, 'c')], ['🦩', '💗'], HIGH),                 # polaroid sits low
    ([('SERIOUS', 130, 'c'), ('on the outside', 66, 'c'), ('PARTY', 230, 'c'), ('on the inside', 66, 'c')], ['🥳', '💃'], LOW),
    ([('SKELETON', 175, 'c'), ('SUIT', 130, 'r')], ['💀', '🧵'], LOW),
    ([('A', 110, 'l'), ('BEER?!', 240, 'c')], ['🍺', '🍻'], LOW),
    ([('26,500', 200, 'c'), ('BAHT', 105, 'r')], ['💸', '🧾'], 400),
    ([('100%', 250, 'c')], ['✅', '💯'], 400),
]
HIGHLIGHT = {'perfectly', 'save'}
TAIL = 0.5                                                    # end card: short hold, then a clean cut

vo = json.load(open(VO_DIR + 'words_clean.json'))['words']
toks = align_script(SCRIPT, vo)

vo_len = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                               VO_DIR + 'vo_clean.wav'], capture_output=True, text=True).stdout)
TOTAL = vo_len + TAIL
para_start = [0.0] + [max(min(t['s'] for t in toks if t['para'] == i) - 0.15, 0) for i in range(1, len(SCRIPT))]
para_end = para_start[1:] + [TOTAL]
_, phrases = build_captions(toks, HIGHLIGHT)
ph_t = lambda i: phrases[i][1]


def word_t(para, word, nth=0):
    return [t for t in toks if t['para'] == para and norm_w(t['w']) == word][nth]['s']


# --- shots: per paragraph; optional anchor = the word/phrase the shot must start on ----
S = Shot
PLAN = [
    [(S(P + 'IMG_1401.MOV', 2.5, ss=3), None), (S(P + 'IMG_5387.MOV', 2.5, ss=125, trans='zoomblur'), None),
     (S(P + 'IMG_5387.MOV', 2.5, ss=196, trans='flash'), ('ph', 0)),
     (S(v(2121), 2.0, ss=3, trans='whip'), ('w', 'first')), (S(v(2005), 2.0, ss=18, trans='punch'), ('w', 'figure'))],
    [(S(v(2004), 4.0, ss=1.0, zoom=(1.0, 1.06), trans='zoomblur'), None),
     (S(v(2336), 2.0, ss=75, trans='slide'), ('w', 'through')), (S(v(2005), 2.0, ss=15, trans='punch'), ('w', 'decision')),
     (S(v(1963), 3.0, ss=6.5, trans='whip'), ('w', 'mine'))],
    [(S(v(1966), 1.5, ss=0, trans='whip'), None), (S(v(1995), 2.0, ss=0.0, trans='punch'), ('ph', 2)),
     (S(v(1999), 2.0, ss=15.0, trans='zoomblur'), ('w', 'recommended')),
     (S(v(1968), 2.0, ss=1, trans='whip'), ('w', 'already')), (S(v(1976), 1.5, ss=1, trans='punch'), None),
     (S(v(1975), 2.5, ss=1, trans='slide'), ('w', 'classic')), (S(v(1971), 1.5, ss=4, trans='punch'), None),
     (S(v(1972), 2.0, ss=2, trans='whip'), ('w', 'shades')), (S(v(1974), 1.5, ss=2, trans='punch'), None),
     (S(v(1972), 2.0, ss=6, soft=0.35, trans='flash'), ('ph', 3))],
    [(S(v(1977), 3.0, ss=3, trans='zoomblur'), None), (S(v(1994), 2.0, ss=3, trans='punch'), None),
     (S(v(1979), 1.5, ss=0, trans='whip'), ('w', 'then')), (S(v(1983), 3.0, ss=8, trans='slide'), ('w', 'lining')),
     (S(v(1984), 1.5, ss=40, soft=0.35, trans='flash'), ('ph', 4)),
     (S(v(2340), 2.5, ss=6, trans='zoomblur'), ('ph', 5)),
     (S(v(1986), 1.5, ss=0.5, soft=0.35, trans='flash'), ('w', 'black')), (S(v(1989), 1.5, ss=2, trans='punch'), ('w', 'white'))],
    [(S(v(1999), 2.0, ss=4, trans='whip'), None), (S(v(2004), 2.5, ss=1, trans='punch'), ('ph', 6)),
     (S(v(2005), 2.0, ss=2, trans='zoomblur'), None), (S(v(2006), 2.0, ss=26, trans='slide'), ('w', 'shortened')),
     (S(v(2121), 2.0, ss=6, trans='whip'), ('w', 'took')), (S(v(2333), 2.0, ss=12, trans='punch'), ('w', 'adjusted')),
     (S(v(2333), 2.0, ss=22, trans='punch'), ('w', 'asked')), (S(v(2335), 1.5, ss=2, trans='zoomblur'), ('w', 'surgery'))],
    [(S(v(2336), 3.0, ss=74, trans='flash'), None), (S(v(2337), 2.0, ss=1, trans='punch'), ('ph', 7)),
     (S(v(2353), 3.0, ss=2.5, trans='whip'), ('w', 'thai'))],
    [(S(v(1968), 4.5, ss=2.5, soft=0.35, zoom=(1.0, 1.05), trans='flash'), None),          # suit cutouts on top
     (S(v(1976), 4.5, ss=0, soft=0.35, zoom=(1.0, 1.05)), None)],                        # (people-free parts only)
    [(S(v(2345), 7.0, ss=0.5, soft=0.45, zoom=(1.0, 1.06), trans='flash'), None)],       # receipt over the tie wall
]
shots, idx = [], {}
for pi, plan in enumerate(PLAN):
    a, b = para_start[pi], para_end[pi]
    anchors = []
    for k, (shot, anc) in enumerate(plan):
        if anc is not None and k != 0:
            t = ph_t(anc[1]) if anc[0] == 'ph' else word_t(pi, anc[1])
            anchors.append((k, min(max(t - 0.1, a), b)))
    bounds = [(0, a)] + anchors + [(len(plan), b)]
    for (k0, t0), (k1, t1) in zip(bounds, bounds[1:]):
        group = plan[k0:k1]
        nom = sum(s.dur for s, _ in group)
        for s, _ in group:
            s.dur = max((t1 - t0) * s.dur / nom, 0.35)
    sc = (b - a) / sum(s.dur for s, _ in plan)                # fill [a, b] exactly
    for j, (s, _) in enumerate(plan):
        s.dur *= sc
        idx[(pi, j)] = sum(x.dur for x in shots)
        shots.append(s)
TOTAL = sum(s.dur for s in shots)

ov, top, sfx = [], [], []
hit = lambda name, t, vol=0.45: sfx.append((SFX + name + '.wav', max(t, 0), vol))


def pop(ch, t, pos, size=180, dur=1.8, wob=8, sound='pop', pair=None):
    ov.append(Overlay(t, t + dur, sticker(ch, size), pos, 'bounce', wob))
    hit(sound, t)
    if pair:                                              # a second emoji so it never looks lonely
        p2 = (pos[0] + (-150 if pos[0] > W / 2 else 150), pos[1] + 110)
        ov.append(Overlay(t + 0.15, t + dur, sticker(pair, int(size * 0.8)), p2, 'bounce', -wob))


def tag_in(label, t0, t1, pos, ch=None, size=44):
    ov.append(Overlay(t0, t1, sprite_tag(label, size, ch), pos, 'bounce'))
    hit('click', t0, 0.6)


def photo_in(path, t0, t1, angle=-4):
    ov.append(Overlay(t0, t1, polaroid(path, width=420, angle=angle), (W / 2, 1230), 'drop'))   # below captions
    hit('shutter', t0 + 0.35, 0.5)


# --- title: builds line by line over the playing clip (paragraph 2 opening) ------
t_title, t_title_end = idx[(1, 0)], idx[(1, 1)]
dim, parts = series_title_parts('[ ep 1: custom suits ]', cy=H // 2 + 60)
ov.append(Overlay(t_title, t_title_end, dim, (0, 0), 'fade', full=True))
delays = {'tag1': 0.15, 'absolutlee': 0.45, 'i': 0.8, 'd': 0.95, 'ring': 1.2, 'tag2': 1.55,
          'emoji0': 1.8, 'emoji1': 1.9, 'emoji2': 2.0, 'emoji3': 2.1, 'emoji4': 2.2}
for name, spr, c in parts:
    t0 = t_title + delays[name]
    anim = 'bounce' if name.startswith('emoji') or name == 'ring' else 'pop'
    ov.append(Overlay(t0, t_title_end, spr, c, anim, 4 if name.startswith('emoji') else 0))
    snd = {'tag1': 'click', 'tag2': 'click', 'ring': 'sparkle', 'absolutlee': 'thud', 'i': 'thud', 'd': 'thud'}.get(name)
    if snd:
        hit(snd, t0, 0.5)
hit('pop', t_title + 1.8, 0.4)

# --- captions + emphasis callouts (drawn last = always on top) -------------------
t_finale = idx[(6, 0)]
kar, _ = build_captions(toks, HIGHLIGHT, y_at=lambda t: CAP_Y_END if t >= t_finale - 0.05 else CAP_Y)
top += [k for k in kar if not (t_title <= k.t0 < t_title_end - 0.3)]
for (txt, p0, p1), (lines, ch, y) in zip(phrases, CALLOUTS):
    end = max(p1 + 0.7, p0 + 1.4)
    for i, (spr, (dx, dy)) in enumerate(callout_lines(lines, ch)):
        is_emoji = i >= len(lines)
        t0 = p0 + 0.12 * i + (0.05 if is_emoji else 0)
        top.insert(0, Overlay(t0, end, spr, (W / 2 + dx, y + dy), 'bounce', (8 if i % 2 else -8) if is_emoji else 0))
    hit('thud', p0, 0.5)
    hit('pop', p0 + 0.12 * len(lines) + 0.05, 0.4)

# --- beats linked to what's on screen -------------------------------------------
pop('👀', word_t(0, 'figure') + 0.2, (240, 480), pair='🤔')
tag_in('black · single-breasted', idx[(2, 5)] + 0.1, idx[(2, 7)], (W / 2, 520), '🤵')
tag_in('burgundy · double-breasted, 4 buttons', word_t(2, 'burgundy'), idx[(2, 7)], (W / 2, 620), '👔')
photo_in(ph(1973), idx[(2, 9)], para_end[2])
hit('zip', idx[(3, 0)] + 0.3, 0.5)
pop('📏', idx[(3, 0)] + 0.6, (860, 1120), pair='✂️')
hit('scribble', idx[(3, 2)], 0.45)
photo_in(ph(1980), idx[(3, 4)], idx[(3, 5)], 4)
photo_in(ph(1991), idx[(3, 6)], idx[(3, 7)] + 1.0, -3)
tag_in('fitting', idx[(4, 0)] + 0.1, idx[(4, 3)], (W / 2, 520), '🧵', 48)
tag_in('alterations', idx[(4, 3)] + 0.1, idx[(4, 6)], (W / 2, 520), '✂️', 48)
hit('snip', idx[(4, 3)] + 0.3, 0.6)
pop('💪', word_t(4, 'gym'), (800, 480), 190, sound='thud', pair='🏋️')
hit('riser', idx[(5, 0)] - 1.0, 0.35)
pop('😍', word_t(5, 'perfectly'), (850, 1060), 190, sound='sparkle', pair='✨')
hit('clink', idx[(5, 1)] + 0.2, 0.5)
pop('🎉', word_t(5, 'thai') + 0.3, (800, 480), 200, pair='🇹🇭')

# --- two suits: big turning cutouts over fabric rolls ---------------------------
t_suits = idx[(6, 0)]
black, burg = cutout_sprite(CUT + 'black.png', 880), cutout_sprite(CUT + 'burgundy.png', 880)
ov.append(Overlay(t_suits + 0.1, para_end[6], black, (290, 1530 - black.height / 2), 'bounce', 6))
ov.append(Overlay(t_suits + 0.35, para_end[6], burg, (790, 1530 - burg.height / 2), 'bounce', -6))
hit('pop', t_suits + 0.1, 0.5)
hit('pop', t_suits + 0.35, 0.5)

# --- end card: big receipt (bottom stays above captions) + small turning cutouts --
rc = receipt_sprite("ricky's fashion house", 'sukhumvit soi 3, bangkok', 'fri 6 nov  –  mon 9 nov',
                    [('2x two-piece suit', ''), ('   black, single-breasted', ''), ('   burgundy, double-breasted', ''),
                     ('1x shirt', ''), ('2x tie', '')],
                    'THB 26,500', '≈ S$1,038.29',
                    ['* price includes 1 fitting', '  & all alterations', '* sgd based on exchange rate'])
s_rc = min(1.05, (1500 - 320) / rc.height, 690 / rc.width)    # top below the captions; leave room for side cutouts
rc = rc.resize((int(rc.width * s_rc), int(rc.height * s_rc)), Image.LANCZOS)
t_end = idx[(7, 0)]
ov.append(Overlay(t_end + 0.2, TOTAL, rc, (W / 2, 320 + rc.height / 2), 'slide_up', fade_out=False))
hit('printer', t_end + 0.2, 0.5)
hit('chaching', t_end + 0.9, 0.5)
small_b, small_r = cutout_sprite(CUT + 'black.png', 560), cutout_sprite(CUT + 'burgundy.png', 560)
ov.append(Overlay(t_end + 0.8, TOTAL, small_b, (115, 1530 - small_b.height / 2), 'bounce', 6, fade_out=False))
ov.append(Overlay(t_end + 1.0, TOTAL, small_r, (965, 1530 - small_r.height / 2), 'bounce', -6, fade_out=False))
hit('pop', t_end + 0.8, 0.4)
hit('pop', t_end + 1.0, 0.4)

if os.environ.get('PLAN_ONLY'):
    for (pi, j), t in sorted(idx.items(), key=lambda x: x[1]):
        print(f'{t:6.2f}  p{pi + 1}.{j}  {Path(PLAN[pi][j][0].src).name}  {PLAN[pi][j][0].dur:.2f}s')
    print('phrases', [(p[0], round(p[1], 2)) for p in phrases], 'total', round(TOTAL, 2))
    sys.exit()
out = sys.argv[1]
total = render(shots, ov + top, sfx, [], out, VO_DIR + 'vo_clean.wav', TOTAL)
print('rendered', out, f'{total:.1f}s')
