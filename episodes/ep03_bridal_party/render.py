"""AbsolutLEE I DO ep 2: the bridal party (her side vs his side). DRAFT before the VO / filmed clips.

Structure: hook (best reaction) -> glitch rewind -> voiceover A (both explain, over placeholders for your own clips)
-> full reactions (her side, his side, real audio) -> voiceover B (Smiski, question) -> scorecard end card.

usage: EDIT_SCALE=1 python3 episodes/ep03_bridal_party/render.py <out.mp4>
"""
import sys, os, json
os.environ.setdefault('EDIT_LOOK', 'natural')        # neutral, saturated look matched to Rochelle's reference
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from editor import *

B, G = '/home/user/footage_ep3/bridesmaids/', '/home/user/footage_ep3/groomsmen/'
SFX = str(Path(__file__).resolve().parents[2] / 'assets' / 'sfx') + '/'
RW = json.load(open('/home/user/footage_ep3_log/words/reactions.json'))
BURGER_CLIP = B + '1172F250-E2E2-4936-816E-65F11C27E0F0.MOV'
hb = lambda n: B + f'IMG_{n}.HEIC'
hg = lambda n: G + f'IMG_{n}.HEIC'

SCRIPT_A = [   # Rochelle + Joshua's script (placeholder timing until the VO is recorded)
    "Welcome to episode two of AbsolutLEE I Do, where we propose to our bridal party, because we can't say I do without them.",
    "And you'll notice the difference right away. What do you mean one of us bought a {giant burger} and the other bought a gym bag?",
    "Every bridesmaid got a giant burger box. Inside, everyone got something similar but personalised, themed around their favourite characters and brands. For example travel bags, there were Pikachu packing cubes, an alien or Chupa Chups toiletries bag, and a 7-Eleven shopping bag. Tiny problem. I bought way too much, never measured anything, and half of it {didn't fit} inside the burger.",
    "Meanwhile, I got a gym bag you can carry three different ways. Inside, protein bars, a shaker bottle, lifting straps, a matching towel, and a massage gun. We're all {getting jacked} next year.",
    "Every single guy got {the exact same thing.}",
    "It's called efficiency. And I asked them all at once. {One table, one take.} Done.",
]
SCRIPT_B = [
    "And since it's a Smiski-coded wedding, we both snuck one in. A {Smiski} ring for my bridesmaids,",
    "and a Smiski luggage tag for my groomsmen.",
    "And they all said",
]
CALLOUTS_A = [
    ([('GIANT', 150, 'l'), ('BURGER', 210, 'r')], ['🍔', '😂']),
    ([("DIDN'T", 150, 'l'), ('FIT', 260, 'r')], ['😭', '📏']),
    ([('GETTING', 120, 'l'), ('JACKED', 210, 'r')], ['💪', '🏋️']),
    ([('SAME.', 140, 'l'), ('SAME.', 140, 'c'), ('SAME.', 140, 'r')], ['🏋️', '💪']),
    ([('ONE TABLE', 120, 'c'), ('ONE TAKE', 150, 'c')], ['🎬', '✅']),
]
CALLOUTS_B = [
    ([('SMISKI', 210, 'c'), ('coded wedding', 80, 'c')], ['💍', '🧳']),
]
CAP_Y, CALL_Y = 760, 1290

# ---------------------------------------------------------------- reactions (source clip, in, out)
HOOK = (BURGER_CLIP, 50.45, 58.45)   # she reads the card aloud: 'you know, I can't say I do without you… so… oh!' then the blooper cut
# many short reactions (2-4s), faces always in frame; optional 4th item = typed caption
M38, M41, M98 = B + 'IMG_8838.MOV', B + 'IMG_8841.MOV', B + 'IMG_8598.MOV'
HER = [(BURGER_CLIP, 39.6, 43.0, "i can't believe you customised this leh"),
       (M38, 4.4, 7.6),                                     # bridesman: 'a burger for me?'
       (M98, 35.5, 42.8),                                   # couple reading their cards, she gets excited
       (M38, 56.0, 58.4),                                   # 'is that a snorlax?'
       (M38, 84.4, 86.4),                                   # snorlax pillow 'oh my god'
       (M41, 0.5, 6.5, 'never been cooler'),                # donning every item
       (BURGER_CLIP, 77.0, 80.3, '', ('smiski ring', '💍'))]   # showing off her Smiski ring
HIS = [(G + 'IMG_1185.MOV', 39.6, 42.6), (G + 'IMG_1185.MOV', 64.0, 67.0),
       (G + 'IMG_1185.MOV', 73.6, 76.0),
       (G + 'IMG_1185.MOV', 77.6, 81.5)]                    # they pull Joshua in for a hug (ends before the date)

def react_words(path, a, b):
    key = path.replace('/home/user/footage_ep3/', '')
    ws = []
    for k, v in RW.items():
        if k.startswith(key + '@'):
            ws += [w for w in v if a <= w['s'] < b - 0.1]
    return ws


# ---------------------------------------------------------------- timeline
shots, ov, top, sfx, og = [], [], [], [], []
hit = lambda name, t, vol=0.45: sfx.append((SFX + name + '.wav', max(t, 0), vol))
now = lambda: sum(s.dur for s in shots)


def add_reaction(path, a, b, text=None, trans='cut', label=None, afilter=''):
    t0 = now()
    shots.append(Shot(path, b - a, ss=a, zoom=(1.0, 1.04), trans=trans))
    og.append((path, a, b - a, t0, 1.0, afilter))
    if text == '':                                           # no captions for this clip
        ws = []
    elif text:                                               # typed caption, spread over the clip
        tw = text.split()
        step = (b - a - 0.4) / len(tw)
        top.append(Karaoke([(w, t0 + 0.15 + i * step) for i, w in enumerate(tw)], t0 + (b - a), CAP_Y, 44, set()))
        ws = []
    else:
        ws = react_words(path, a, b)
    line = []
    for i, w in enumerate(ws):                             # reaction captions (karaoke, same style)
        cw = clean_caption_word(w['w'])
        for part in cw.split():
            line.append((part, t0 + w['s'] - a))
        if len(line) >= 5 or w['w'].endswith(('.', '?', '!', ',')) and len(line) >= 3 or i == len(ws) - 1:
            if line:
                end = min(t0 + ws[min(i + 1, len(ws) - 1)]['s'] - a, t0 + (b - a)) if i + 1 < len(ws) else t0 + (b - a)
                top.append(Karaoke(line, max(end, line[-1][1] + 0.4), CAP_Y, 44, set()))
                line = []
    if label:
        ov.append(Overlay(t0 + 0.15, t0 + min(2.5, b - a), sprite_tag(label[0], 42, label[1]), (W / 2, 300), 'bounce'))
        hit('click', t0 + 0.15, 0.5)
    return t0


def vo_block(script, callouts, plan, wps=3.5):
    """Lay out a voiceover block with placeholder timing; plan = per-paragraph list of (Shot, tag or None)."""
    words, length = synthetic_vo_words(script, wps=wps)
    t0 = now()
    for w in words:
        w['s'] += t0; w['e'] += t0
    toks = align_script(script, words)
    kar, phrases = build_captions(toks, set(), y_at=lambda t: CAP_Y)
    top.extend(kar)
    starts = [t0] + [min(t['s'] for t in toks if t['para'] == i) - 0.12 for i in range(1, len(script))]
    ends = starts[1:] + [t0 + length + 0.3]
    for pi, items in enumerate(plan):
        a, b = starts[pi], ends[pi]
        nom = sum(s.dur for s, _ in items)
        for s, tag in items:
            s.dur = (b - a) * s.dur / nom
            ts = now()
            shots.append(s)
            if tag:
                ov.append(Overlay(ts + 0.1, ts + s.dur, sprite_tag(tag, 34, '🎬'), (W / 2, 250), 'pop'))
    for (txt, p0, p1), co in zip(phrases, callouts):
        if co is None:
            continue
        lines, ch = co
        end = max(p1 + 0.7, p0 + 1.4)
        for i, (spr, (dx, dy)) in enumerate(callout_lines(lines, ch, emoji_size=150)):
            is_emoji = i >= len(lines)
            top.insert(0, Overlay(p0 + 0.12 * i + (0.05 if is_emoji else 0), end, spr, (W / 2 + dx, CALL_Y + dy),
                                  'bounce', (8 if i % 2 else -8) if is_emoji else 0))
        hit('thud', p0, 0.5)
        hit('pop', p0 + 0.12 * len(lines) + 0.05, 0.4)
    return starts, ends


S = Shot
# 1 hook: she reads the card (voice-focus filter to push down the background laughter); captions typed in
n_top = len(top)
add_reaction(*HOOK, afilter=VOICE_FOCUS + ',agate=threshold=0.08:ratio=8:attack=3:release=120')
del top[n_top:]
for words, t1 in [([('you', 50.5), ('know', 51.16), ("i can't", 51.8), ('say', 52.42)], 52.64),
                  ([('i', 52.64), ('do', 53.6), ('without', 53.88), ('you', 54.38)], 55.8),
                  ([('so', 55.9), ('oh', 56.64), ('i', 57.6), ("didn't", 57.8), ('know', 58.05)], 58.45)]:
    top.append(Karaoke([(w, t - HOOK[1]) for w, t in words], t1 - HOOK[1], CAP_Y, 44, set()))
ov.append(Overlay(0.2, HOOK[2] - HOOK[1], sprite_tag('proposing to our bridal party', 40, '💍'), (W / 2, 300), 'bounce'))
hit('click', 0.2, 0.5)

# 2 blooper 'no signal' glitch (colour bars + beep) straight after the hook
t_g = now()
shots.append(S(HOOK[0], 0.12, ss=HOOK[2] - 0.1, glitch=1.5, zoom=(1.0, 1.0)))      # frame tears first
shots.append(S(lambda t: no_signal_frame(t), 0.7, zoom=(1.0, 1.0)))
hit('glitch', t_g, 0.5)
hit('beep', t_g + 0.12, 0.55)

# 3 voiceover A over placeholders (your filmed clips go here)
PLAN_A = [
    [(S(B + 'IMG_0572.JPG', 4.0, zoom=(1.0, 1.06)), 'film: you two, welcome')],                         # title card on top
    [(S(B + 'IMG_0571.JPG', 2.0, zoom=(1.0, 1.06), trans='whip'), 'film: R holds burger, J holds gym bag'),
     (S(hg(6585), 2.0, zoom=(1.0, 1.06), trans='punch'), None)],
    [(S(hb(8395), 1.4, zoom=(1.0, 1.08), trans='whip'), 'film: R, items pop in as stickers'),
     (S(hb(8426), 1.4, zoom=(1.0, 1.08), trans='punch'), None), (S(hb(8414), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hb(8409), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(hb(8531), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hb(8405), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(hb(8418), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hb(8513), 1.4, zoom=(1.0, 1.06), trans='whip'), None), (S(hb(8505), 1.4, zoom=(1.0, 1.06), trans='punch'), None)],
    [(S(hg(6568), 1.3, zoom=(1.0, 1.08), trans='whip'), 'film: J, gym items pop in'), (S(hg(6556), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hg(6575), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(hg(6582), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hg(6560), 1.0, zoom=(1.0, 1.08), trans='punch'), None)],
    [(S(hg(6566), 0.8, zoom=(1.0, 1.08), trans='punch'), None), (S(hg(6578), 0.8, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hg(6562), 0.8, zoom=(1.0, 1.08), trans='punch'), None)],
    [(S(G + 'IMG_1185.MOV', 2.5, ss=40, trans='whip'), None)],
]
a_starts, a_ends = vo_block(SCRIPT_A, CALLOUTS_A, PLAN_A)
# title card over paragraph 2
t_title, t_title_end = a_starts[0], a_ends[0]
dim, parts = series_title_parts('[ ep 2: the bridal party ]', cy=H // 2 + 20)
ov.append(Overlay(t_title, t_title_end, dim, (0, 0), 'fade', full=True))
delays = {'tag1': 0.1, 'absolutlee': 0.35, 'i': 0.65, 'd': 0.8, 'ring': 1.0, 'tag2': 1.3,
          'emoji0': 1.5, 'emoji1': 1.6, 'emoji2': 1.7, 'emoji3': 1.8, 'emoji4': 1.9}
for name, spr, c in parts:
    t0 = t_title + delays[name]
    ov.append(Overlay(t0, t_title_end, spr, c, 'bounce' if name.startswith('emoji') or name == 'ring' else 'pop',
                      4 if name.startswith('emoji') else 0))
    snd = {'tag1': 'click', 'tag2': 'click', 'ring': 'sparkle', 'absolutlee': 'thud', 'i': 'thud', 'd': 'thud'}.get(name)
    if snd:
        hit(snd, t0, 0.5)
top[:] = [o for o in top if not (isinstance(o, Karaoke) and t_title <= o.t0 < t_title_end - 0.2)]
# "her side" / "his side" section tags
ov.append(Overlay(a_starts[2] + 0.1, a_ends[2], sprite_tag('her side', 44, '🍔'), (W / 2, 330), 'bounce'))
ov.append(Overlay(a_starts[3] + 0.1, a_ends[5], sprite_tag('his side', 44, '🏋️'), (W / 2, 330), 'bounce'))

# 4 full reactions
t_her = now()
for k, r in enumerate(HER):
    lab = r[4] if len(r) > 4 else (('her side', '🍔') if k == 0 else None)
    add_reaction(*r[:4], trans=('flash' if k == 0 else 'punch' if k % 2 else 'whip'), label=lab)
t_his = now()
for k, r in enumerate(HIS):
    add_reaction(*r, trans=('flash' if k == 0 else 'punch' if k % 2 else 'whip'), label=('his side', '🏋️') if k == 0 else None)

# 5 voiceover B: Smiski + the question
PLAN_B = [
    [(S(hb(8403), 2.0, zoom=(1.0, 1.1), trans='flash'), None)],
    [(S(hg(6585), 1.8, zoom=(1.0, 1.1), trans='whip'), None)],
    [(S(hb(8403), 1.2, zoom=(1.05, 1.12), trans='punch'), None)],
]
b_starts, b_ends = vo_block(SCRIPT_B, CALLOUTS_B, PLAN_B)


# 6 ending: 'they all said yes' collage, everyone's YES lined up to land at the same moment
YES = [(BURGER_CLIP, 80.35, 'bridesmaid'), (B + 'IMG_8838.MOV', 26.14, 'bridesman'),
       (B + 'IMG_8598.MOV', 51.64, 'bridesmaid'), (G + 'IMG_1185.MOV', 65.5, 'groomsmen')]
LEAD, CDUR = 0.12, 2.6                                      # every tile starts right on its yes
col = collage_clip([(src, t - LEAD) for src, t, _ in YES], CDUR, 'collage_yes.mp4')
t_col = now()
shots.append(Shot(str(col), CDUR, zoom=(1.0, 1.03), trans='flash'))
for src, t, lab in YES:
    og.append((src, t - LEAD, CDUR, t_col, 0.8))
for i, (src, t, lab) in enumerate(YES):                     # small labels on each tile
    x = W / 4 + (W / 2) * (i % 2)
    y = (H / 4 - 330) + (H / 2) * (i // 2) + 120
    ov.append(Overlay(t_col + 0.2, t_col + CDUR, sprite_tag(lab, 34), (x, max(y, 230)), 'pop', fade_out=False, safe=False))
t_yes = t_col + 0.15
for i, (spr, (dx, dy)) in enumerate(callout_lines([('they all said', 90, 'c'), ('YES!', 300, 'c')], ['💍', '🥹'], emoji_size=150)):
    top.append(Overlay(t_yes + 0.1 * i, t_col + CDUR, spr, (W / 2 + dx, H / 2 + dy), 'bounce',
                       (8 if i % 2 else -8) if i >= 2 else 0, fade_out=False))
hit('thud', t_yes, 0.6)
hit('sparkle', t_yes + 0.15, 0.5)
TOTAL = now()

if os.environ.get('PLAN_ONLY'):
    for i, s in enumerate(shots):
        print(f'{sum(x.dur for x in shots[:i]):6.2f} {Path(s.src).name:42s} {s.dur:.2f}s')
    print('total', round(TOTAL, 2))
    sys.exit()
out = sys.argv[1]
total = render(shots, ov + top, sfx, og, out, None, TOTAL)
print('rendered', out, f'{total:.1f}s')
