"""Ep 2 (Bangkok headshots, Rochelle). Timed to the voiceover if /home/user/vo_ep2/words_clean.json exists,
otherwise to placeholder timings from the script (draft before the VO is recorded).

usage: EDIT_SCALE=1 python3 episodes/ep02_headshot/render.py <out.mp4>      (1080p draft)
"""
import sys, os, json
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from editor import *
from linkedin import linkedin_post, lanyard_badge

F = '/home/user/footage_ep2/'
VO_DIR = '/home/user/vo_ep2/'
SFX = str(Path(__file__).resolve().parents[2] / 'assets' / 'sfx') + '/'
norm_w = lambda w: ''.join(c for c in w.lower() if c.isalnum())


def v(n):
    for ext in ('.MOV', '.mov', '.HEIC', '.JPG', '.jpg'):
        if os.path.exists(F + f'IMG_{n}{ext}'):
            return F + f'IMG_{n}{ext}'
    raise FileNotFoundError(n)


SCRIPT = [
    "{POV: this is your sign to update your LinkedIn photo while you're on holiday.}",
    "If you're in Bangkok, book a headshot at {Holo Face.} Here's exactly how it works.",
    "You check in, and a stylist asks what you're going for: {soft or bold makeup,} your outfit, even your backdrop, so it all comes together.",
    "Then it's {an hour of hair and makeup,} while you pick from a huge wardrobe of styles and outfits. Basically, {playing dress-up as an adult,} but make it professional.",
    "Before you lock in your look, you do {test shots} on camera. I started in pants, but it wasn't flattering, so I decided to change into a skirt.",
    "And if you're awkward in front of the camera like me, they literally {teach you how to pose.} Chin down, shoulders back, and somehow I look like I know what I'm doing.",
    "After about fifteen minutes of shooting, you pick your photos. {The hardest part.} I booked {one…} and walked out with {three.} Self-control was not part of the package.",
    "The edits came back {the same day.} In their app, you see the before and after, and message the editor exactly what to change.",
    "The next day we picked up our prints, and I gave Josh my photo card. Because I'm {the only idol} he has, obviously.",
    "{New LinkedIn photo, unlocked.} Would you do this on your next holiday?",
]
CAP_Y, CAP_Y_END = 760, 230
LOW, HIGH, BEHIND_Y = 1330, 430, 470
# per {phrase}: (lines, emojis, y, behind_person)   None = no callout (handled elsewhere)
CALLOUTS = [
    ([('POV:', 110, 'c'), ('this is your sign to', 66, 'c'), ('UPDATE YOUR', 120, 'c'),
      ('LINKEDIN PHOTO', 150, 'c', (255, 255, 255)), ("while you're on holiday", 70, 'c')], ['💼', '📸'], 1230, False),
    ([('HOLO FACE', 190, 'c')], ['📍', '✨'], LOW, False),
    ([('SOFT', 170, 'l'), ('or', 80, 'c'), ('BOLD?', 200, 'r')], ['💄', '🎨'], LOW, False),
    ([('1 HOUR', 210, 'c'), ('hair + makeup', 80, 'c')], ['💇', '💄'], LOW, False),
    ([('PLAYING', 110, 'l'), ('DRESS UP', 190, 'c'), ('as an adult', 80, 'r')], ['👗', '👠'], LOW, False),
    ([('TEST', 260, 'c'), ('SHOTS', 260, 'c')], ['📸', '🎬'], 650, True),        # she stands in front of it
    ([('POSE', 340, 'c')], ['🙈', '📸'], BEHIND_Y, True),
    ([('THE HARDEST', 130, 'c'), ('PART', 220, 'c')], ['😩', '😭'], LOW, False),
    ([('ONE', 300, 'c')], ['☝️'], LOW, False),
    ([('THREE', 300, 'c')], ['🤭', '💸'], LOW, False),
    ([('SAME', 170, 'l'), ('DAY', 240, 'r')], ['⚡', '📱'], LOW, False),
    ([('THE ONLY', 120, 'c'), ('IDOL', 260, 'c')], ['🥹', '💛'], 1400, False),
    None,                                                     # end card heading instead
]
HIGHLIGHT = {'awkward', 'skirt', 'obviously', 'professional'}

if os.path.exists(VO_DIR + 'words_clean.json'):
    vo = json.load(open(VO_DIR + 'words_clean.json'))['words']
    vo_path = VO_DIR + 'vo_clean.wav'
    vo_len = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vo_path],
                                  capture_output=True, text=True).stdout)
else:                                                         # draft: placeholder timing, no audio
    vo, vo_len = synthetic_vo_words(SCRIPT, wps=3.3)
    vo_path = None
TAIL = 2.0 if vo_path is None else 0.8                        # end card readable before the cut
toks = align_script(SCRIPT, vo)
_, phrases = build_captions(toks, HIGHLIGHT)
TOTAL = vo_len + TAIL
para_start = [0.0] + [max(min(t['s'] for t in toks if t['para'] == i) - 0.15, 0) for i in range(1, len(SCRIPT))]
para_end = para_start[1:] + [TOTAL]
ph_t = lambda i: phrases[i][1]


def word_t(para, word, nth=0):
    return [t for t in toks if t['para'] == para and norm_w(t['w']) == word][nth]['s']


S = Shot
PLAN = [
    # 1 hook: hero photo + quick cuts under the POV text
    [(S(v(8002), 1.6, zoom=(1.0, 1.08), trans='flash'), None), (S(v(7621), 0.8, ss=3, trans='punch'), None),
     (S(v(7634), 0.8, ss=20, trans='zoomblur'), None), (S(v(7635), 0.8, ss=3, trans='punch'), None),
     (S(v(8001), 1.2, zoom=(1.0, 1.06), trans='flash'), None)],
    # 2 holo face
    [(S(v(7669), 1.5, ss=0, trans='whip'), None), (S(v(7600), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(v(7602), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(v(7603), 2.0, ss=0, trans='whip'), ('w', 'heres'))],
    # 3 check-in, style chat, backdrop
    [(S(v(7668), 1.3, ss=1, trans='zoomblur'), None), (S(v(7668), 1.2, ss=6, trans='punch'), None),
     (S(v(7614), 1.5, ss=1, trans='punch'), ('ph', 2)),
     (S(v(7665), 1.5, ss=0.5, trans='whip'), ('w', 'outfit')), (S(v(7634), 1.5, ss=0, trans='punch'), ('w', 'backdrop'))],
    # 4 hair + makeup, wardrobe, friend's outfit, fitting room
    [(S(v(7616), 2.0, ss=1, trans='zoomblur'), None), (S(v(7621), 2.0, ss=6, trans='punch'), None),
     (S(v(7622), 1.5, ss=1, trans='whip'), ('w', 'while')), (S(v(7666), 1.2, ss=0, trans='punch'), ('w', 'huge')),
     (S(v(7612), 2.0, ss=6, trans='whip'), ('w', 'styles')), (S(v(7609), 1.2, ss=0.5, trans='punch'), ('ph', 4)),
     (S(v(7610), 1.2, ss=1, trans='punch'), None), (S(v(7613), 1.5, ss=2, trans='zoomblur'), ('w', 'professional'))],
    # 5 test shots (text behind her), pants -> skirt
    [(S(v(7632), 2.5, ss=6.0, zoom=(1.35, 1.42), pan=(0.62, 0.62), trans='punch'), None),  # pants test shot on set, text behind her
     (S(v(7625), 1.5, ss=7.5, trans='whip'), ('w', 'pants')), (S(v(7625), 1.2, ss=10, trans='punch'), ('w', 'flattering')),
     (S(v(7634), 2.0, ss=9, trans='flash'), ('w', 'skirt'))],
    # 6 posing (POSE behind her), friend directed
    [(S(v(7634), 2.0, ss=5, zoom=(1.15, 1.2), trans='whip'), None),
     (S(v(7634), 2.5, ss=11, zoom=(1.38, 1.46), pan=(0.5, 0.6), trans='punch'), ('ph', 6)),
     (S(v(7634), 1.8, ss=21, zoom=(1.2, 1.28), trans='zoomblur'), ('w', 'chin')),
     (S(v(7634), 2.0, ss=26, zoom=(1.15, 1.2), trans='punch'), ('w', 'somehow')),
     (S(v(7635), 1.5, ss=1, trans='whip'), None)],
    # 7 picking photos, one -> three
    [(S(v(7635), 1.5, ss=3, trans='zoomblur'), None), (S(v(7635), 1.5, ss=10, trans='punch'), ('w', 'shooting')),
     (S(F + 'camphoto_1594243340.jpg', 1.5, zoom=(1.0, 1.08), trans='punch'), ('w', 'pick')),
     (S(v(7664), 2.0, ss=8, trans='whip'), ('ph', 7)), (S(v(7664), 1.5, ss=15, trans='punch'), ('ph', 8)),
     (S(v(7635), 1.5, ss=15, trans='flash'), ('ph', 9)), (S(v(7671), 1.5, ss=3.5, trans='whip'), ('w', 'selfcontrol')),
     (S(v(7671), 1.2, ss=13.5, trans='punch'), ('w', 'package'))],
    # 8 same-day edits in the app, then the reveal of the three finals
    [(S(v(7996), 1.3, zoom=(1.0, 1.06), trans='slide'), None), (S(v(7998), 1.2, zoom=(1.0, 1.06), trans='punch'), ('w', 'in')),
     (S(v(7997), 1.2, zoom=(1.0, 1.06), trans='punch'), ('w', 'before')),
     (S(v(7634), 3.9, ss=1, soft=0.4, zoom=(1.0, 1.05), trans='flash'), ('w', 'message'))],     # badges on top
    # 9 prints + photo card for Josh
    [(S(v(8395), 2.0, ss=5.3, trans='whip'), None),                                 # Josh already picking a card
     (S(v(8396), 3.0, ss=5.0, trans='punch'), ('w', 'gave')),                       # the phone kiss, held longer
     (S(v(8396), 2.2, ss=11.4, trans='zoomblur'), ('ph', 11))],             # second kiss
    # 10 LinkedIn end card over the wardrobe
    [(S(v(7665), 4.0, ss=0, speed=0.38, soft=0.45, zoom=(1.0, 1.06), trans='flash'), None)],
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
    sc = (b - a) / sum(s.dur for s, _ in plan)
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
    if pair:
        p2 = (pos[0] + (-150 if pos[0] > W / 2 else 150), pos[1] + 110)
        ov.append(Overlay(t + 0.15, t + dur, sticker(pair, int(size * 0.8)), p2, 'bounce', -wob))


def tag_in(label, t0, t1, pos, ch=None, size=44):
    ov.append(Overlay(t0, t1, sprite_tag(label, size, ch), pos, 'bounce'))
    hit('click', t0, 0.6)


# --- captions + callouts ---------------------------------------------------------
t_finale = idx[(9, 0)]
behind_win = [(p[1] - 0.1, max(p[2] + 1.6, p[1] + 2.2)) for p, co in zip(phrases, CALLOUTS) if co and co[3]]
cap_y = lambda t: CAP_Y_END if t >= t_finale - 0.05 else 1420 if any(a <= t < b for a, b in behind_win) else CAP_Y
kar, _ = build_captions(toks, HIGHLIGHT, y_at=cap_y)
top += kar
for (txt, p0, p1), co in zip(phrases, CALLOUTS):
    if co is None:
        continue
    lines, ch, y, behind = co
    end = max(p1 + 0.7, p0 + 1.4) if not behind else max(p1 + 1.6, p0 + 2.2)
    if txt.startswith('POV'):
        end = para_end[0] - 0.05
    parts = callout_lines(lines, ch, emoji_size=150 if not behind else 170)
    for i, (spr, (dx, dy)) in enumerate(parts):
        is_emoji = i >= len(lines)
        t0 = p0 + 0.12 * i + (0.05 if is_emoji else 0)
        o = Overlay(t0, end, spr, (W / 2 + dx, y + dy), 'bounce', (8 if i % 2 else -8) if is_emoji else 0)
        o.behind = behind and not is_emoji                    # words behind her, emojis in front
        (ov if o.behind else top).insert(0, o)
    hit('thud', p0, 0.5)
    hit('pop', p0 + 0.12 * len(lines) + 0.05, 0.4)

# --- beats --------------------------------------------------------------------------
pop('✅', word_t(4, 'skirt') + 0.2, (800, 1150), 190, sound='sparkle', pair='👗')
pop('❌', word_t(4, 'pants') + 0.2, (800, 1150), 170)
t_badges = idx[(7, 3)]                                        # three finals as corporate lanyard badges
for k, (n, ang, x) in enumerate([(8001, 4, 195), (8002, 0, 540), (8003, -4, 885)]):
    b = lanyard_badge(v(n), w=318, angle=ang)
    t0 = t_badges + 0.15 + 0.45 * k
    ov.append(Overlay(t0, idx[(8, 0)], b, (x, 1340 - b.height / 2), 'drop', 3 * (1 if k % 2 else -1)))   # cards end above the bottom UI
    hit('shutter', t0 + 0.3, 0.55)
pop('😍', t_badges + 1.6, (870, 1480), 170, sound='sparkle', pair='✨')
for k, (ch, pos, dt) in enumerate([('😘', (820, 560), 0.6), ('💋', (250, 640), 0.9), ('😘', (300, 520), 0.2), ('💋', (830, 640), 0.5)]):
    base_t = idx[(8, 1)] if k < 2 else idx[(8, 2)]
    pop(ch, base_t + dt, pos, 170, dur=1.6, sound='pop')
tag_in('emsphere, bangkok', idx[(1, 0)] + 0.3, idx[(1, 3)], (W / 2, 560), '📍')
tag_in('1 photo booked', ph_t(8) + 0.2, ph_t(9) - 0.05, (W / 2, 560), '📸')
tag_in('3 photos taken home', ph_t(9) + 0.2, ph_t(9) + 2.0, (W / 2, 560), '📸')

# --- end card: LinkedIn post ---------------------------------------------------------
t_end = idx[(9, 0)]
card = linkedin_post(v(8002), [('📍', 'Holo Face, Emsphere, Bangkok'), ('📸', 'Professional Portrait · 3 retouched photos'),
                               ('💸', 'THB 3,888'), ('💄', 'hair, makeup, styling + outfits included'),
                               ('⚡', 'edits back the same day')])
card = card.resize((int(card.width * 0.97), int(card.height * 0.97)), Image.LANCZOS)
ov.append(Overlay(t_end + 0.3, TOTAL, card, (W / 2, 470 + card.height / 2), 'slide_up', fade_out=False))
hit('ding', t_end + 0.9, 0.5)
h1 = sprite_text('NEW PFP', font('bootzy', 110), 'white', 12)
h2 = sprite_text('UNLOCKED', font('bootzy', 125), BUTTER, 12)
ov.append(Overlay(t_end + 0.1, TOTAL, h1, (W / 2 - 70, 330), 'bounce', fade_out=False))
ov.append(Overlay(t_end + 0.25, TOTAL, h2, (W / 2 + 50, 425), 'bounce', fade_out=False))
ov.append(Overlay(t_end + 0.45, TOTAL, sticker('🔓', 110), (870, 300), 'bounce', 8, fade_out=False))
ov.append(Overlay(t_end + 0.55, TOTAL, sticker('💼', 100), (130, 440), 'bounce', -8, fade_out=False))
hit('thud', t_end + 0.1, 0.5)
hit('pop', t_end + 0.45, 0.4)

if os.environ.get('PLAN_ONLY'):
    for (pi, j), t in sorted(idx.items(), key=lambda x: x[1]):
        print(f'{t:6.2f}  p{pi + 1}.{j}  {Path(PLAN[pi][j][0].src).name}  {PLAN[pi][j][0].dur:.2f}s')
    print('phrases', [(p[0], round(p[1], 2)) for p in phrases], 'total', round(TOTAL, 2))
    sys.exit()
out = sys.argv[1]
total = render(shots, ov + top, sfx, [], out, vo_path, TOTAL)
print('rendered', out, f'{total:.1f}s')
