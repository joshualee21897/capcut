"""'today i will turn into a cute little mini me' at the Toy Story booth: 2 rounds (Rochelle -> girl, Josh -> boy).

Every shot is registered to one reference frame on the booth sign, then cropped with the same booth-relative
rectangle, so the swap from adult to kid looks like one locked-off camera. Cut timing copied from the reference.
Exported silent (trending sound added in TikTok).
usage: EDIT_SCALE=1 python3 episodes/ep06_mini_me/render.py [out.mp4]
"""
import os, sys, subprocess, hashlib
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, HERE)
os.environ.setdefault('EDIT_LOOK', 'mid_warm')
from editor import *          # noqa
from align import register, WS

F = '/home/user/footage_kids/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'renders/ep06_mini_me_preview.mp4'
REF = (F + 'IMG_9833.MOV', 1.5)
BOX = (0.05, 0.12, 0.75, 0.30)                 # booth sign template (no people in it)
SRC_W = 2160                                   # source width after rotation (portrait 4K)
CUTS = [0, 0.87, 1.67, 2.6, 3.43, 4.3, 5.07, 5.9, 6.87]

# crop rectangles in reference working coordinates (WS = 360 wide), 9:16
CROP = {'R': (0, 110, 216, 494), 'J': (112, 110, 328, 494)}
ROUNDS = [('R', [('IMG_9833.MOV', 1.2, 1.5), ('IMG_9833.MOV', 6.5, 6.8), ('IMG_9833.MOV', 32.2, 32.5),
                 ('IMG_9831.MOV', 1.6, 1.9)]),
          ('J', [('IMG_9833.MOV', 0.6, 1.0), ('IMG_9833.MOV', 29.2, 29.5), ('IMG_9833.MOV', 12.2, 12.5),
                 ('IMG_9831.MOV', 3.7, 4.0)])]


def aligned_clip(name, ss, t_reg, dur, crop):
    """Cut + crop the clip so the booth lands where it is in the reference crop; cached."""
    s, dx, dy, score = register(*REF, F + name, t_reg, box=BOX)
    m = SRC_W / WS
    x0, y0, x1, y1 = [(v - d) / s * m for v, d in zip(crop, (dx, dy, dx, dy))]
    w, h = int(x1 - x0) // 2 * 2, int(y1 - y0) // 2 * 2
    key = hashlib.md5(repr((name, ss, dur, crop, round(s, 3), dx, dy)).encode()).hexdigest()[:10]
    out = CACHE / f'minime_{key}.mp4'
    if not out.exists():
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{ss:.3f}', '-t', f'{dur + 0.3:.3f}', '-i', F + name,
                        '-vf', f'crop={w}:{h}:{int(x0)}:{int(y0)},scale=2160:3840:flags=lanczos',
                        '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', str(out)], check=True)
    print(f'{name} @{ss}: s={s:.3f} dx={dx} dy={dy} match={score:.2f} crop={w}x{h}')
    return str(out)


shots = []
i = 0
for side, clips in ROUNDS:
    for name, ss, t_reg in clips:
        dur = CUTS[i + 1] - CUTS[i]
        shots.append(Shot(aligned_clip(name, ss, t_reg, dur, CROP[side]), dur, 0.0, zoom=(1.0, 1.0)))
        i += 1

# text: white Bootzy, one line per beat, staggered like the trend; resets each round.
# round 1 sits above Rochelle's head; round 2 sits on Josh's shirt (his head is high in frame), above the boy
LINES = ['today i will', 'turn into', 'a cute little', 'mini me']
XS = [380, 650, 420, 620]
Y0 = [250, 800]
top = []
for r in range(2):
    base = 4 * r
    for k, s_ in enumerate(LINES):
        t0, t1 = CUTS[base + k], CUTS[base + 4]
        y = Y0[r] + k * 92 + (12 if k == 3 else 0)
        top.append(Overlay(t0, t1, sprite_text(s_, font('bootzy', 80 if k < 3 else 104), (255, 255, 255),
                                               shadow=12, pad=24), (XS[k], y), 'pop', fade_out=False))
    top.append(Overlay(CUTS[base + 3] + 0.06, CUTS[base + 4], sticker('🤠', 104), (830, Y0[r] + 3 * 92 - 20),
                       'bounce', 8, fade_out=False))

render(shots, top, [], [], OUT, total=CUTS[-1])      # silent: trending sound goes on in TikTok
print('wrote', OUT)
