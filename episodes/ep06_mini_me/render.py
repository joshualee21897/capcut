"""'today we will turn into cute little mini us' at the Toy Story booth: both adults -> both kids, 2 rounds.

Whole booth in frame and locked still: every frame of every clip is registered to one reference frame on the
booth sign and cropped with the same booth-relative rectangle. One caption line per pose change.
Cut timing copied from the reference. Exported silent (trending sound added in TikTok).
usage: EDIT_SCALE=1 python3 episodes/ep06_mini_me/render.py [out.mp4]
"""
import os, sys, hashlib, json
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, HERE)
os.environ.setdefault('EDIT_LOOK', 'mid_warm')
from editor import *          # noqa
from stabilize import track, coverage, render_locked, SRC_W, SRC_H
from align import WS

F = '/home/user/footage_kids/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'renders/ep06_mini_me_preview.mp4'
REF = (F + 'IMG_9833.MOV', 1.5)
BOX = (0.05, 0.12, 0.75, 0.30)                 # booth sign template (no people in it)
CUTS = [0, 0.87, 1.67, 2.6, 3.43, 4.3, 5.07, 5.9, 6.87]
CLIPS = [('IMG_9833.MOV', 1.3),                # round 1: standing
         ('IMG_9833.MOV', 6.5),                #          hands on cheeks
         ('IMG_9833.MOV', 12.2),               #          both leaning, laughing
         ('IMG_9831.MOV', 1.6),                #          kids: girl's peace sign
         ('IMG_9833.MOV', 26.2),               # round 2: peace sign
         ('IMG_9833.MOV', 19.2),               #          waving
         ('IMG_9833.MOV', 32.2),               #          both bent down low
         ('IMG_9831.MOV', 13.9)]               #          kids: hand on cheek
BOOTH_C = (168, 330)                           # booth centre in reference working coords

tracks = []
for k, (name, ss) in enumerate(CLIPS):
    dur = CUTS[k + 1] - CUTS[k]
    key = hashlib.md5(repr(('trk5', name, ss, dur, REF, BOX)).encode()).hexdigest()[:10]
    p = CACHE / f'minime_trk_{key}.json'
    if p.exists():
        tr = json.loads(p.read_text())
    else:
        tr = track(F + name, ss, dur, REF, BOX).tolist()
        p.write_text(json.dumps(tr))
    tracks.append(tr)
    print(name, ss, 'scale %.3f' % tr[0][0], 'sy %.3f..%.3f  shear %.3f..%.3f' % (
        min(t[2] for t in tr), max(t[2] for t in tr), min(t[4] for t in tr), max(t[4] for t in tr)))

# biggest 9:16 rectangle every frame covers, centred on the booth, with a small safety margin
cov = [coverage(t) for t in tracks]
X0, Y0 = max(c[0] for c in cov), max(c[1] for c in cov)
X1, Y1 = min(c[2] for c in cov), min(c[3] for c in cov)
cx, cy = BOOTH_C
half_w = min(cx - X0, X1 - cx, (cy - Y0) * 9 / 16, (Y1 - cy) * 9 / 16) * 0.985
CROP = (cx - half_w, cy - half_w * 16 / 9, cx + half_w, cy + half_w * 16 / 9)
print('covered', [round(v, 1) for v in (X0, Y0, X1, Y1)], 'crop', [round(v, 1) for v in CROP],
      'zoom %.2f' % (WS / (2 * half_w)))

shots = []
for k, ((name, ss), tr) in enumerate(zip(CLIPS, tracks)):
    dur = CUTS[k + 1] - CUTS[k]
    key = hashlib.md5(repr(('lock5', name, ss, dur, [round(v, 2) for v in CROP], tr[0])).encode()).hexdigest()[:10]
    out = CACHE / f'minime_lock_{key}.mp4'
    if not out.exists():
        render_locked(F + name, ss, dur, tr, CROP, out, size=(OW, OH))
    shots.append(Shot(str(out), dur, 0.0, zoom=(1.0, 1.0)))

# captions: white Bootzy, one line per pose change, staggered like the trend; resets each round
LINES = ['today we will', 'turn into', 'cute little', 'mini us']
POS = [(330, 230), (460, 320), (350, 410), (400, 525)]     # left side: clear of Josh's head
top = []
for r in range(2):
    base = 4 * r
    for k, s_ in enumerate(LINES):
        t0, t1 = CUTS[base + k], CUTS[base + 4]
        top.append(Overlay(t0, t1, sprite_text(s_, font('bootzy', 80 if k < 3 else 104), (255, 255, 255),
                                               shadow=12, pad=24), POS[k], 'pop', fade_out=False))
    top.append(Overlay(CUTS[base + 3] + 0.06, CUTS[base + 4], sticker('🤠', 104), (650, 500), 'bounce', 8,
                       fade_out=False))

render(shots, top, [], [], OUT, total=CUTS[-1])      # silent: trending sound goes on in TikTok
print('wrote', OUT)
