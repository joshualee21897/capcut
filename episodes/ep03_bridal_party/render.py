"""AbsolutLEE I DO ep 2: the bridal party (her side vs his side). DRAFT before the VO / filmed clips.

Structure: hook (best reaction) -> glitch rewind -> voiceover A (both explain, over placeholders for your own clips)
-> full reactions (her side, his side, real audio) -> voiceover B (Smiski, question) -> scorecard end card.

usage: EDIT_SCALE=1 python3 episodes/ep03_bridal_party/render.py <out.mp4>
"""
import sys, os, json
os.environ.setdefault('EDIT_LOOK', 'mid_warm')       # option C (Rochelle's pick): clips matched to each other first, then warmed
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
       (M38, 84.7, 86.0),                                   # snorlax pillow 'oh my god' (tightened)
       (M41, 0.0, 2.25, 'never been cooler'),               # donning every item (ends before 'it's a video')
       (BURGER_CLIP, 75.9, 78.6, 'this is so cool', ('smiski ring', '💍'))]   # 'this is so cool' + showing off her Smiski ring
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
    ws = []                                                  # reactions: no transcripts (too many voices to caption reliably)
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



# ---------------------------------------------------------------- talking-head blocks (Rochelle left, Joshua right)
TALK = '/home/user/footage_ep3/new/IMG_9662.MOV'                 # 2nd recording: louder, no muffled lines
TALK_AUDIO = '/home/user/footage_ep3/talk/talk_clean.wav'           # wind/noise removed, EQ'd, levelled
TW_ = json.load(open('/home/user/footage_ep3/new/talk62_words.json'))
FIX = {'correctors': 'characters', 'teamed': 'themed', 'teamed,': 'themed', 'ask': 'asked', "smiski's": 'smiski', 'personalized': 'personalised',
       'favorite': 'favourite'}
FRAMES = {'both': ((1.2, 1.24), (0.5, 0.55)), 'R': ((1.85, 1.92), (0.33, 0.43)), 'J': ((1.85, 1.92), (0.69, 0.42)),
          'R2': ((1.45, 1.5), (0.36, 0.47)), 'J2': ((1.45, 1.5), (0.66, 0.46))}
ITEMS = '/home/user/edit_cache/items/'
ITEMS2 = '/home/user/edit_cache/items2/'
ITEMS3 = '/home/user/edit_cache/items3/'
COUPLE = '/root/.claude/uploads/486170bb-8ec7-5d42-92d8-a87d4f85fa4a/5482b717-image.jpg'   # Rochelle's edited couple photo


def cover_collage():
    """Cover frame: three burger reactions on top, the groomsmen table below, series title at the seam."""
    p = CACHE / 'cover_collage.png'
    if p.exists():
        return Image.open(p).convert('RGBA')
    from PIL import ImageOps
    import pillow_heif
    pillow_heif.register_heif_opener()
    c = Image.new('RGB', (W, H), (250, 248, 244))
    tops = [(B + 'IMG_8926.HEIC', (0.5, 0.35)), (COUPLE, (0.5, 0.3)), (B + 'IMG_8840.HEIC', (0.5, 0.3))]
    for i, (f, cen) in enumerate(tops):
        im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
        c.paste(ImageOps.fit(im, (W // 3, H // 2), centering=cen), (i * W // 3, 0))
    for j, (t, cen) in enumerate([(62.5, (0.39, 0.45)), (64.5, (0.27, 0.45)), (66.5, (0.53, 0.45)), (74.5, (0.41, 0.4))]):
        fp = CACHE / f'gm_close_{j}.png'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', G + 'IMG_1185.MOV', '-frames:v', '1', str(fp)], check=True)
        c.paste(ImageOps.fit(Image.open(fp).convert('RGB'), (W // 4, H // 2), centering=cen), (j * W // 4, H // 2))
    d = ImageDraw.Draw(c)
    for x in (W // 3, 2 * W // 3):
        d.line((x, 0, x, H // 2), fill=(250, 248, 244), width=8)
    for x in (W // 4, W // 2, 3 * W // 4):
        d.line((x, H // 2, x, H), fill=(250, 248, 244), width=8)
    d.line((0, H // 2, W, H // 2), fill=(250, 248, 244), width=8)
    out = c.convert('RGBA')
    series_title(out, '[ ep 2: the bridal party ]', cy=H // 2)
    out.save(p)
    out.convert('RGB').save(str(Path(__file__).parent / 'cover.jpg'), quality=94)
    return out


def clean_talk_seg(a, b):
    """Level this segment's speech to a common loudness FIRST, then denoise/EQ, so quiet parts aren't eaten."""
    out = CACHE / f'talkseg62_{a:.2f}_{b:.2f}.wav'
    if out.exists():
        return str(out)
    raw = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a}', '-t', f'{b - a}', '-i', TALK, '-map', '0:a:0',
                                        '-f', 's16le', '-ac', '1', '-ar', '48000', '-'], capture_output=True).stdout,
                        np.int16).astype(np.float32) / 32768
    fr = raw[:len(raw) // 2400 * 2400].reshape(-1, 2400)
    lv = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    speech = np.percentile(lv, 85)                           # loud-ish frames = speech
    gain = float(np.clip(-20 - speech, -6, 48))
    nr = 14 if gain < 20 else 30                             # very quiet recording: stronger denoise after boost
    chain = (f'volume={gain:.1f}dB,highpass=f=140,lowpass=f=11000,afftdn=nr={nr}:nf=-60:tn=1,anlmdn=s={7 if gain >= 20 else 2},'
             'equalizer=f=220:t=q:w=1.2:g=-2.5,equalizer=f=3800:t=q:w=1.0:g=3,equalizer=f=10000:t=q:w=0.8:g=1.5,'
             'deesser=i=0.3,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=2,alimiter=limit=0.9')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{a}', '-t', f'{b - a}', '-i', TALK, '-map', '0:a:0', '-af', chain,
                    '-ar', '48000', '-ac', '2', str(out)], check=True)
    return str(out)


_ENV = None


def word_end(t_end, limit):
    """Extend a cut past Whisper's word end until the voice actually fades (no clipped endings)."""
    global _ENV
    if _ENV is None:
        x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', TALK, '-map', '0:a:0', '-f', 's16le', '-ac', '1',
                                          '-ar', '16000', '-'], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
        n = len(x) // 160
        env = np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1) + 1e-12)        # 10 ms frames
        _ENV = (env, np.percentile(env, 15))
    env, floor = _ENV
    i, stop = int((t_end + 0.15) * 100), int(min(t_end + 0.6, limit) * 100)   # always keep 150 ms of tail
    while i < stop and i < len(env) and env[i] > floor * 2:
        i += 1
    return min(i / 100 + 0.12, limit)


def drop_pauses(pa, pb, min_gap=0.22, keep=0.06):
    """Split [pa, pb] wherever the voice drops out for > min_gap (a hesitation), keeping a short breath each side."""
    word_end(pa, pa + 0.01)                                         # make sure the envelope is loaded
    env, floor = _ENV
    i0, i1 = int(pa * 100), int(pb * 100)
    seg = env[i0:i1]
    if len(seg) < 10:
        return [(pa, pb)]
    level = np.percentile(seg, 80)
    quiet = seg < max(level * 0.16, floor * 1.6)                    # ~16 dB under the speech level
    out, start, j = [], pa, 0
    while j < len(quiet):
        if quiet[j]:
            k = j
            while k < len(quiet) and quiet[k]:
                k += 1
            if (k - j) / 100 > min_gap and j > 0 and k < len(quiet):
                out.append((start, pa + j / 100 + keep)); start = pa + k / 100 - keep
            j = k
        else:
            j += 1
    out.append((start, pb))
    return [(a_, b_) for a_, b_ in out if b_ - a_ > 0.12]


def talk_words(a, b):
    ws = [w for seg in TW_ for w in seg['words'] if a - 0.05 <= w['s'] < b]
    return [dict(w, w=FIX.get(w['w'].lower().strip('.,!?~'), w['w'])) for w in ws]


def src_to_tl(map_, t, snap=True):
    for ss, se, t0 in map_:
        if ss <= t <= se:
            return t0 + (t - ss)
    if not snap or not map_:
        return None
    after = [(ss, t0) for ss, se, t0 in map_ if ss > t]           # inside a cut pause: snap to the next kept moment
    if after and min(after)[0] - t < 1.5:
        return min(after)[1]
    before = [(se, t0 + se - ss) for ss, se, t0 in map_ if se < t]
    if before and t - max(before)[0] < 1.5:
        return max(before)[1]
    return None


def talk_block(segs, cap_y=1400, gap_split=0.42):
    """segs: [(src_in, src_out, frame or [(src_t, frame), ...])]. Splits at pauses (jump cuts), reframes per speaker.
    Returns a source->timeline map."""
    map_ = []
    for a, b, fr in segs:
        ws = talk_words(a, b)
        pieces, cur = [], [max(a, ws[0]['s'] - 0.08) if ws else a, None]
        for i, w in enumerate(ws):
            nxt = ws[i + 1]['s'] if i + 1 < len(ws) else None
            if nxt is not None and nxt - w['e'] > gap_split:
                pieces.append((cur[0], word_end(w['e'], nxt - 0.06))); cur = [nxt - 0.08, None]
        pieces.append((cur[0], word_end(ws[-1]['e'], b) if ws else b))
        pieces = [q for pa, pb in pieces for q in drop_pauses(pa, pb)]     # remove hesitations inside a phrase too
        frl = fr if isinstance(fr, list) else [(a, fr)]
        cuts = [t for t, _ in frl[1:]]
        split = []
        for pa, pb in pieces:                                 # also cut exactly where the framing / cutaway changes
            edges = [pa] + [c for c in cuts if pa < c < pb] + [pb]
            split += list(zip(edges, edges[1:]))
        prev = None
        for pa, pb in split:
            f = [x for t, x in frl if t <= pa + 0.01][-1]
            t0 = now()
            if isinstance(f, tuple):                          # cutaway: ('clip', path, src_in) while the talk audio continues
                _, cpath, cin = f
                off = pa - [t for t, x in frl if x is f][0]
                shots.append(Shot(cpath, pb - pa, ss=cin + off, zoom=(1.0, 1.04), trans='cut'))
            else:
                (z0, z1), pan = FRAMES[f]
                shots.append(Shot(TALK, pb - pa, ss=pa, zoom=(z0, z0), pan=pan, trans='cut'))
            og.append((clean_talk_seg(a, b), pa - a, pb - pa, t0, 1.0))
            map_.append((pa, pb, t0))
            prev = f
        toks = [dict(w=w['w'], s=src_to_tl(map_, w['s'], False), e=src_to_tl(map_, min(w['e'], b)) or 0, para=0, phrase=None)
                for w in ws if src_to_tl(map_, w['s'], False) is not None]
        if toks:
            kar, _ = build_captions(toks, set(), y_at=lambda t: cap_y)
            top.extend(kar)
    return map_


def item_pop(map_, src_t, name, pos, h=330, dur=2.6, until=None):
    t = src_to_tl(map_, src_t)
    if t is None:
        return
    spr = cutout_sprite(ITEMS + name + '.png', h, outline=6)
    if spr.width > 420:
        spr = spr.resize((420, int(spr.height * 420 / spr.width)), Image.LANCZOS)
    ov.append(Overlay(t, until if until else t + dur, spr, pos, 'bounce', 6 if pos[0] > W / 2 else -6))
    hit('pop', t, 0.5)


def callout_at(map_, src_t, lines, ch, y=1080, dur=1.8):
    t = src_to_tl(map_, src_t)
    if t is None:
        return
    for i, (spr, (dx, dy)) in enumerate(callout_lines(lines, ch, emoji_size=150)):
        is_emoji = i >= len(lines)
        top.insert(0, Overlay(t + 0.12 * i, t + dur, spr, (W / 2 + dx, y + dy), 'bounce', (8 if i % 2 else -8) if is_emoji else 0))
    hit('thud', t, 0.5)

S = Shot
# 1 hook: she reads the card (voice-focus filter to push down the background laughter); captions typed in
n_top = len(top)
add_reaction(*HOOK, afilter=VOICE_FOCUS + ',agate=threshold=0.08:ratio=8:attack=3:release=120')
del top[n_top:]
for words, t1 in [([('you', 50.5), ('know', 51.16), ("i can't", 51.8), ('say', 52.42)], 52.64),
                  ([('i', 52.64), ('do', 53.6), ('without', 53.88), ('you', 54.38)], 55.8),
                  ([('so', 55.9), ('oh', 56.64), ('i', 57.6), ("didn't", 57.8), ('know', 58.05)], 58.45)]:
    top.append(Karaoke([(w, t - HOOK[1]) for w, t in words], t1 - HOOK[1], CAP_Y, 44, set()))

# 2 blooper 'no signal' glitch (colour bars + beep) straight after the hook
t_g = now()
shots.append(S(HOOK[0], 0.12, ss=HOOK[2] - 0.1, glitch=1.5, zoom=(1.0, 1.0)))      # frame tears first
shots.append(S(lambda t: no_signal_frame(t), 0.7, zoom=(1.0, 1.0)))
hit('glitch', t_g, 0.5)
hit('beep', t_g + 0.12, 0.55)

# 3 you two explain (talking-head clip, retakes removed, jump cuts at pauses, reframed per speaker)
mapA = talk_block([
    (3.0, 10.9, 'both'),                                     # R: welcome… (cover collage on top)
    (11.3, 17.85, 'J'),                                       # J: you'll notice the difference… burger vs gym bag
    (17.9, 35.3, [(17.9, 'R'), (27.7, 'both')]),   # R … didn't fit = overflow bag
    (35.4, 48.45, [(35.4, 'J'), (46.0, 'both')]),            # J: gym bag list… getting jacked
    (48.6, 52.05, 'both'),                                    # R: every single guy…
    (52.12, 59.3, 'J'),   # J: efficiency… all at once = the table
])


def cutaway(map_, src_a, src_b, clip, clip_in):
    """Replace the picture of [src_a, src_b] (talk time) with another clip; the talk audio keeps playing."""
    ta = src_to_tl(map_, src_a)
    ends = [t0 + (se - ss) for ss, se, t0 in map_ if ss < src_b + 0.8 and se > src_a]
    tb = max(ends)                                              # hold the cutaway to the very end of the sentence
    out, t = [], 0.0
    for sh in shots:
        s0, s1 = t, t + sh.dur
        t = s1
        if s1 <= ta or s0 >= tb:
            out.append(sh); continue
        if s0 < ta:
            out.append(Shot(sh.src, ta - s0, ss=sh.ss, zoom=(sh.zoom[0], sh.zoom[0]), pan=sh.pan, trans=sh.trans))
        if s0 <= ta < s1 or (s0 >= ta and not any(o.src == clip and abs(o.ss - clip_in) < 1e-6 for o in out)):
            out.append(Shot(clip, tb - ta, ss=clip_in, zoom=(1.0, 1.04), trans='cut'))
        if s1 > tb:
            out.append(Shot(sh.src, s1 - tb, ss=sh.ss + (tb - s0), zoom=(sh.zoom[0], sh.zoom[0]), pan=sh.pan, trans='cut'))
    shots[:] = out


cutaway(mapA, 33.0, 34.85, B + 'IMG_8593.MOV', 0.2)          # 'didn't even fit inside the burger' = the overflow bag
cutaway(mapA, 53.8, 58.85, G + 'IMG_1185.MOV', 29.0)          # 'asked them all at once, one table, one take' = the table
t_title = src_to_tl(mapA, 3.2); t_title_end = src_to_tl(mapA, 10.8)
dim, parts = series_title_parts('[ ep 2: the bridal party ]', cy=H // 2 + 270)   # below their faces
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
# cover collage on "…where we propose to our bridal team, because we can't say I do without them"
t_col0, t_col1 = src_to_tl(mapA, 6.1), src_to_tl(mapA, 10.8)
ov.append(Overlay(t_col0, t_col1, cover_collage(), (0, 0), 'fade', full=True))
hit('shutter', t_col0, 0.5)
# Joshua: "one of us bought a giant burger" (Rochelle's photo stays) "…and the other bought a gym bag" (Joshua's photo)
pr = polaroid(B + 'IMG_0571.JPG', width=400, angle=-5)
pj = polaroid(G + 'IMG_6588.HEIC', width=400, angle=5)
t_b, t_g2, t_e = src_to_tl(mapA, 14.9), src_to_tl(mapA, 16.9), src_to_tl(mapA, 17.4) + 0.5
ov.append(Overlay(t_b, t_e, pr, (300, 520), 'drop')); hit('shutter', t_b + 0.3, 0.5)
ov.append(Overlay(t_g2, t_e, pj, (780, 560), 'drop')); hit('shutter', t_g2 + 0.3, 0.5)
item_pop(mapA, 20.4, 'bm_burger', (540, 470), dur=1.6)
# "everyone got something similar but personalised… characters and brands": the 4 packed sets slide up and fill the screen
t_p0, t_p1 = src_to_tl(mapA, 22.3), src_to_tl(mapA, 27.6)
for k, (pk, (x, y, r)) in enumerate(zip(['IMG_8506', 'IMG_8521', 'IMG_8536', 'IMG_8548'],
                                         [(300, 560, -8), (780, 640, 6), (330, 1180, 5), (770, 1300, -6)])):
    pol = polaroid(B + pk + '.HEIC', width=520, angle=r)
    ov.append(Overlay(t_p0 + 0.35 * k, t_p1, pol, (x, y), 'slide_up', safe=False))
    hit('shutter', t_p0 + 0.35 * k + 0.4, 0.4)
callout_at(mapA, 33.6, [("DIDN'T", 150, 'l'), ('FIT', 260, 'r')], ['😭', '📏'])
# Joshua's list: the gym bag alone, then each item
GYM_END = None


def item2(src_t, nm, pos, h=340, dur=1.0, maxw=460):
    t = src_to_tl(mapA, src_t)
    spr = cutout_sprite(nm + '.png', h, outline=6)
    if spr.width > maxw:
        spr = spr.resize((maxw, int(spr.height * maxw / spr.width)), Image.LANCZOS)
    end = src_to_tl(mapA, GYM_END) if GYM_END else t + dur
    ov.append(Overlay(t, end, spr, pos, 'bounce', 6 if pos[0] > W / 2 else -6)); hit('pop', t, 0.5)
GYM_END = 46.2                                               # everything stays until 'getting jacked'
item2(36.8, ITEMS2 + 'gm_bag_only', (560, 470), h=270, maxw=380)          # top row + right column, clear of his head
item2(40.0, ITEMS2 + 'g6556_1', (200, 470), h=220, maxw=260); item2(41.2, ITEMS2 + 'g6554_1', (900, 470), h=260, maxw=210)
item2(42.3, ITEMS2 + 'g6582_1', (890, 760), h=190, maxw=260); item2(43.4, ITEMS2 + 'g6560_1', (890, 1010), h=190, maxw=260)
item2(44.8, ITEMS2 + 'g6553_1', (890, 1250), h=190, maxw=250)
callout_at(mapA, 46.3, [('GETTING', 120, 'l'), ('JACKED', 210, 'r')], ['💪', '🏋️'])
callout_at(mapA, 50.6, [('SAME.', 140, 'l'), ('SAME.', 140, 'c'), ('SAME.', 140, 'r')], ['🏋️', '💪'])
callout_at(mapA, 56.4, [('ONE TABLE', 120, 'c'), ('ONE TAKE', 150, 'c')], ['🎬', '✅'], dur=2.6)
ov.append(Overlay(src_to_tl(mapA, 18.0), src_to_tl(mapA, 34.8), sprite_tag('her side', 44, '🍔'), (W / 2, 300), 'bounce'))
ov.append(Overlay(src_to_tl(mapA, 35.5), src_to_tl(mapA, 58.8), sprite_tag('his side', 44, '🏋️'), (W / 2, 300), 'bounce'))

# 4 full reactions
t_her = now()
for k, r in enumerate(HER):
    lab = r[4] if len(r) > 4 else (('her side', '🍔') if k == 0 else None)
    add_reaction(*r[:4], trans=('flash' if k == 0 else 'punch' if k % 2 else 'whip'), label=lab)
t_his = now()
for k, r in enumerate(HIS):
    add_reaction(*r, trans=('flash' if k == 0 else 'punch' if k % 2 else 'whip'), label=('his side', '🏋️') if k == 0 else None)

# 5 Smiski lines + 'and they all said…' (talking-head)
mapB = talk_block([(62.9, 71.7, 'both'), (80.5, 82.9, 'both')])
t_sm = src_to_tl(mapB, 66.6)
for path, pos, h in [(ITEMS3 + 'rings_8', (330, 410), 230), (ITEMS2 + 'gm_tag_big', (770, 390), 300)]:
    spr = cutout_sprite(path + '.png', h, outline=7)
    ov.append(Overlay(t_sm, src_to_tl(mapB, 71.2), spr, pos, 'bounce', 6 if pos[0] > W / 2 else -6))
hit('pop', t_sm, 0.5)
callout_at(mapB, 64.3, [('SMISKI', 200, 'c'), ('coded wedding', 80, 'c')], ['💍', '🧳'], dur=1.9)

# 6 ending: 'they all said yes' collage, everyone's YES lined up to land at the same moment
YES = [(BURGER_CLIP, 80.35, 'bridesmaid'), (B + 'IMG_8838.MOV', 26.7, 'bridesman'),
       (B + 'IMG_8598.MOV', 51.64, 'bridesmaid'), (G + 'IMG_1185.MOV', 5.5, 'groomsmen')]   # the 'wooo'
LEAD, CDUR = 0.12, 2.6                                      # every tile starts right on its yes
col = collage_clip([(src, t - LEAD) for src, t, _ in YES], CDUR, 'collage_yes.mp4')
t_col = now()
shots.append(Shot(str(col), CDUR, zoom=(1.0, 1.03), trans='flash'))
for src, t, lab in YES:
    og.append((src, t - LEAD, CDUR, t_col, 0.8))
t_yes = t_col + 0.15
for i, (spr, (dx, dy)) in enumerate(callout_lines([('they all said', 90, 'c'), ('YES!', 300, 'c')], ['💍', '🥹'], emoji_size=150)):
    top.append(Overlay(t_yes + 0.1 * i, t_col + CDUR, spr, (W / 2 + dx, H / 2 + dy), 'bounce',
                       (8 if i % 2 else -8) if i >= 2 else 0, fade_out=False))
hit('thud', t_yes, 0.6)
hit('sparkle', t_yes + 0.15, 0.5)
TOTAL = now()

if os.environ.get('PLAN_ONLY'):
    for i, s in enumerate(shots):
        print(f'{sum(x.dur for x in shots[:i]):6.2f} {(Path(s.src).name if isinstance(s.src, str) else "gen"):42s} {s.dur:.2f}s')
    print('total', round(TOTAL, 2))
    for o_ in og: print('OG', [round(v, 2) if isinstance(v, float) else (v[-30:] if isinstance(v, str) else v) for v in o_[:5]])
    sys.exit()
kars = sorted([o for o in top if isinstance(o, Karaoke)], key=lambda o: o.t0)
for k1, k2 in zip(kars, kars[1:]):                            # one caption line on screen at a time
    if k1.t1 > k2.t0 - 0.02:
        k1.t1 = k2.t0 - 0.02
out = sys.argv[1]
total = render(shots, ov + top, sfx, og, out, None, TOTAL)
print('rendered', out, f'{total:.1f}s')
