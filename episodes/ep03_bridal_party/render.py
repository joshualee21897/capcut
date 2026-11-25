"""AbsolutLEE I DO ep 2: the bridal party (her side vs his side). DRAFT before the VO / filmed clips.

Structure: hook (best reaction) -> glitch rewind -> voiceover A (both explain, over placeholders for your own clips)
-> full reactions (her side, his side, real audio) -> voiceover B (Smiski, question) -> scorecard end card.

usage: EDIT_SCALE=1 python3 episodes/ep03_bridal_party/render.py <out.mp4>
"""
import sys, os, json
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

SCRIPT_A = [   # R = Rochelle, J = Joshua (draft: placeholder timing until the VO is recorded)
    "We asked our bridal party to stand beside us, and you can tell exactly who planned which side.",
    "Welcome to episode two of AbsolutLEE I Do.",
    "My side first. Every bridesmaid, and my two bridesmen, got a {giant burger.} Don't ask.",
    "Inside, {everyone got something different.} Their favourite characters, Pikachu, Snorlax, Sully, Patrick, plus stuff they'd actually use.",
    "Tiny problem. I bought way too much, never measured the burger, and half of it {didn't fit.}",
    "My side? A gym bag. Protein bars, a shaker, lifting straps, and a matching tee.",
    "Every single guy got {the exact same thing.}",
    "It's called efficiency. And I asked them all at once. {One table, one take.} Done.",
    "Here's how they reacted.",
]
SCRIPT_B = [
    "But we both snuck in one thing. {A Smiski.} A ring for my side,",
    "and a luggage tag for mine.",
    "So, {whose side would you rather be on?}",
]
CALLOUTS_A = [
    ([('GIANT', 150, 'l'), ('BURGER', 210, 'r')], ['🍔', '😂']),
    ([('EVERYONE', 140, 'c'), ('DIFFERENT', 170, 'c')], ['✨', '🎁']),
    ([("DIDN'T", 150, 'l'), ('FIT', 260, 'r')], ['😭', '📏']),
    ([('SAME.', 140, 'l'), ('SAME.', 140, 'c'), ('SAME.', 140, 'r')], ['🏋️', '💪']),
    ([('ONE TABLE', 120, 'c'), ('ONE TAKE', 150, 'c')], ['🎬', '✅']),
]
CALLOUTS_B = [
    ([('SMISKI', 210, 'c'), ('for everyone', 80, 'c')], ['💍', '🧳']),
    None,                                                   # the question lives on the end card
]
CAP_Y, CALL_Y = 760, 1290

# ---------------------------------------------------------------- reactions (source clip, in, out)
HOOK = (B + 'IMG_8838.MOV', 32.5, 38.7)
HER = [(BURGER_CLIP, 50.6, 55.2), (B + 'IMG_8838.MOV', 3.9, 7.9), (B + 'IMG_8838.MOV', 53.4, 58.2),
       (B + 'IMG_8841.MOV', 7.8, 11.7), (B + 'IMG_8598.MOV', 49.0, 53.6)]
HIS = [(G + 'IMG_1185.MOV', 0.0, 9.6)]   # ends long before the date is said


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


def add_reaction(path, a, b, trans='cut', label=None):
    t0 = now()
    shots.append(Shot(path, b - a, ss=a, zoom=(1.0, 1.04), trans=trans))
    og.append((path, a, b - a, t0, 1.0))
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
# 1 hook: best reaction
add_reaction(*HOOK)
ov.append(Overlay(0.2, HOOK[2] - HOOK[1], sprite_tag('proposing to our bridal party', 40, '💍'), (W / 2, 300), 'bounce'))
hit('click', 0.2, 0.5)

# 2 glitch rewind
t_g = now()
shots.append(S(HOOK[0], 0.9, ss=HOOK[1] + 0.5, speed=-6.0, glitch=1.0, zoom=(1.05, 1.0)))
ov.append(Overlay(t_g + 0.05, t_g + 0.9, sprite_tag('ok let\'s rewind', 44, '⏪'), (W / 2, 900), 'pop'))
hit('rewind', t_g, 0.6)
hit('glitch', t_g + 0.5, 0.5)

# 3 voiceover A over placeholders (your filmed clips go here)
PLAN_A = [
    [(S(BURGER_CLIP, 2.0, ss=22, trans='flash'), None), (S(hg(6585), 2.0, zoom=(1.0, 1.06), trans='whip'), None)],
    [(S(BURGER_CLIP, 3.0, ss=24, zoom=(1.0, 1.06)), None)],                                    # title card on top
    [(S(hb(8395), 1.4, zoom=(1.0, 1.08), trans='whip'), 'film: you two holding up the burger'),
     (S(hb(8426), 1.6, zoom=(1.0, 1.08), trans='punch'), None)],
    [(S(hb(8414), 1.0, zoom=(1.0, 1.08), trans='whip'), 'film: pulling out each item'), (S(hb(8424), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hb(8409), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(hb(8531), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hb(8405), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(hb(8418), 1.0, zoom=(1.0, 1.08), trans='punch'), None)],
    [(S(hb(8513), 1.5, zoom=(1.0, 1.06), trans='whip'), 'film: stuff spilling out of the burger'),
     (S(hb(8505), 1.5, zoom=(1.0, 1.06), trans='punch'), None)],
    [(S(hg(6568), 1.3, zoom=(1.0, 1.08), trans='whip'), 'film: Josh unpacking the gym bag'), (S(hg(6556), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hg(6575), 1.0, zoom=(1.0, 1.08), trans='punch'), None), (S(hg(6582), 1.0, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hg(6560), 1.0, zoom=(1.0, 1.08), trans='punch'), None)],
    [(S(hg(6566), 0.8, zoom=(1.0, 1.08), trans='punch'), None), (S(hg(6578), 0.8, zoom=(1.0, 1.08), trans='punch'), None),
     (S(hg(6562), 0.8, zoom=(1.0, 1.08), trans='punch'), None)],
    [(S(G + 'IMG_1185.MOV', 2.5, ss=40, soft=0.0, trans='whip'), None)],
    [(S(BURGER_CLIP, 1.5, ss=5, trans='zoomblur'), None)],
]
a_starts, a_ends = vo_block(SCRIPT_A, CALLOUTS_A, PLAN_A)
# title card over paragraph 2
t_title, t_title_end = a_starts[1], a_ends[1]
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
ov.append(Overlay(a_starts[2] + 0.1, a_ends[4], sprite_tag('her side', 44, '🍔'), (W / 2, 330), 'bounce'))
ov.append(Overlay(a_starts[5] + 0.1, a_ends[7], sprite_tag('his side', 44, '🏋️'), (W / 2, 330), 'bounce'))

# 4 full reactions
t_her = now()
for k, r in enumerate(HER):
    add_reaction(*r, trans='whip' if k else 'flash', label=('her side', '🍔') if k == 0 else None)
t_his = now()
for k, r in enumerate(HIS):
    add_reaction(*r, trans='whip' if k else 'flash', label=('his side', '🏋️') if k == 0 else None)

# 5 voiceover B: Smiski + the question
PLAN_B = [
    [(S(hb(8403), 2.0, zoom=(1.0, 1.1), trans='flash'), None)],
    [(S(hg(6585), 1.8, zoom=(1.0, 1.1), trans='whip'), None)],
    [(S(hg(6568), 2.0, soft=0.45, zoom=(1.0, 1.04), trans='flash'), None)],
]
b_starts, b_ends = vo_block(SCRIPT_B, CALLOUTS_B, PLAN_B)


# 6 scorecard end card (extends the last shot)
def scorecard():
    rows = [('personalised', '✅', '❌'), ('favourite characters', '✅', '❌'), ('everything fit in the box', '❌', '✅'),
            ('protein', '❌', '✅'), ('asked in one go', '❌', '✅'), ('smiski', '✅', '✅')]
    cw, rh = 820, 86
    card = Image.new('RGBA', (cw, 150 + rh * len(rows) + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width, card.height), 30, fill=(253, 251, 245, 245))
    fb, fr = font('info_bold', 34), font('info', 30)
    for x, (lab, ch) in zip((560, 720), [('her', '🍔'), ('his', '🏋️')]):
        card.alpha_composite(emoji(ch, 56), (x - 28, 22))
        d.text((x, 104), lab, font=fb, fill=(40, 36, 30), anchor='mm')
    for i, (lab, a, b) in enumerate(rows):
        y = 150 + rh * i + rh // 2
        d.line((30, y - rh // 2, cw - 30, y - rh // 2), fill=(225, 220, 210), width=2)
        d.text((40, y), lab, font=fr, fill=(40, 36, 30), anchor='lm')
    return card, rows


card, rows = scorecard()
t_end = b_starts[2]
end_dur = 3.5
shots[-1].dur += end_dur
TOTAL = now()
ov.append(Overlay(t_end + 0.2, TOTAL, card, (W / 2, 1180), 'slide_up', fade_out=False))
hit('ding', t_end + 0.6, 0.45)
for i, (lab, a, b) in enumerate(rows):                      # ticks pop in row by row
    y = 1180 - card.height / 2 + 150 + 86 * i + 43
    tt = t_end + 0.9 + 0.35 * i
    for x, ch in ((W / 2 - card.width / 2 + 560, a), (W / 2 - card.width / 2 + 720, b)):
        ov.append(Overlay(tt, TOTAL, sticker(ch, 58, 4), (x, y), 'bounce', fade_out=False))
    hit('pop', tt, 0.4)
q1 = sprite_text('whose side', font('bootzy', 120), 'white', 12)
q2 = sprite_text('are you on?', font('bootzy', 120), BUTTER, 12)
ov.append(Overlay(t_end + 0.1, TOTAL, q1, (W / 2 - 40, 430), 'bounce', fade_out=False))
ov.append(Overlay(t_end + 0.25, TOTAL, q2, (W / 2 + 40, 545), 'bounce', fade_out=False))
ov.append(Overlay(t_end + 0.4, TOTAL, sticker('🍔', 120), (175, 360), 'bounce', -8, fade_out=False))
ov.append(Overlay(t_end + 0.5, TOTAL, sticker('🏋️', 120), (905, 640), 'bounce', 8, fade_out=False))
hit('thud', t_end + 0.1, 0.5)

if os.environ.get('PLAN_ONLY'):
    for i, s in enumerate(shots):
        print(f'{sum(x.dur for x in shots[:i]):6.2f} {Path(s.src).name:42s} {s.dur:.2f}s')
    print('total', round(TOTAL, 2))
    sys.exit()
out = sys.argv[1]
total = render(shots, ov + top, sfx, og, out, None, TOTAL)
print('rendered', out, f'{total:.1f}s')
