"""AbsolutLEE abroad · Bali: Mount Batur sunrise jeep tour.

Text only (trending sound added in TikTok), exported silent. Timeline follows the real capture times.
usage: EDIT_SCALE=1 python3 episodes/ep04_bali_batur/render.py renders/ep04_draft_v1_preview.mp4
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
os.environ.setdefault('EDIT_LOOK', 'mid_warm')
from editor import *          # noqa

F = '/home/user/footage_bali/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'renders/ep04_draft_v1_preview.mp4'
WHITE = (255, 255, 255)

shots, ov, top = [], [], []
t = 0.0


def add(src, dur, ss=0.0, **kw):
    global t
    name = src if src.startswith('/') else F + src
    shots.append(Shot(name, dur, ss, **kw))
    t0 = t
    t += dur
    return t0


def callout(lines, ch, t0, t1, y, emoji_size=110):
    for i, (spr, (dx, dy)) in enumerate(callout_lines(lines, ch, emoji_size=emoji_size)):
        is_emoji = i >= len(lines)
        top.append(Overlay(t0 + 0.1 * i + (0.05 if is_emoji else 0), t1, spr, (W / 2 + dx, y + dy),
                           'bounce' if is_emoji else 'pop', (7 if i % 2 else -7) if is_emoji else 0))


def stamp(time_s, label, ch, t0, t1, y=430):
    """Time stamp beat: big butter time, white label underneath, emoji pair flanking the time."""
    parts = callout_lines([(time_s, 200, 'c'), (label, 78, 'c', WHITE)])
    for i, (spr, (dx, dy)) in enumerate(parts):
        top.append(Overlay(t0 + 0.1 * i, t1, spr, (W / 2 + dx, y + dy), 'pop'))
    tw, (_, ty) = parts[0][0].width, parts[0][1]
    for j, (c, side) in enumerate(zip(ch, (-1, 1))):
        x = W / 2 + side * (tw / 2 + 40)
        top.append(Overlay(t0 + 0.2 + 0.08 * j, t1, sticker(c, 100), (x, y + ty - 10 * side), 'bounce', 7 * side))


def tag_in(s, ch, t0, t1, y=1360):
    top.append(Overlay(t0, t1, sprite_tag(s, 46, ch), (W / 2, y), 'pop'))


# --- hook: the two of us watching the sunrise ------------------------------------
h0 = add('IMG_0726.MOV', 2.4, 7.6, pan=(0.3, 0.5), zoom=(1.0, 1.05))
callout([('worth the', 100, 'c', WHITE), ('2am', 230, 'c'), ('wake up', 110, 'c', WHITE)], ('🌅', '🥱'),
        h0 + 0.05, h0 + 2.4, 470, emoji_size=120)

# --- title ------------------------------------------------------------------------
t_title = add('IMG_0725.MOV', 2.2, 14.0, zoom=(1.0, 1.04))
delays = {'absolutlee': 0.0, 'abr': 0.2, 'globe': 0.35, 'ad': 0.2, 'tag1': 0.55, 'tag2': 0.7,
          'flag': 0.85, 'sun': 0.95, 'plane': 1.05}
for name, spr, c in abroad_title_parts('[ mount batur sunrise jeep tour ]', '[ bali, indonesia ]', cy=560):
    anim = 'bounce' if name in ('globe', 'flag', 'sun', 'plane') else 'pop'
    top.append(Overlay(t_title + delays[name], t_title + 2.2, spr, c, anim,
                       4 if name in ('flag', 'sun', 'plane') else 0))

# --- 2:20am pickup ------------------------------------------------------------------
b = add('IMG_0636.MOV', 1.2, 0.8, trans='punch')
add('IMG_5002.MOV', 1.0, 5.0)
add('IMG_5001.HEIC', 0.8)
stamp('2:20am', 'pickup from our airbnb', ('🚐', '😴'), b, t)

# --- 4:00am jeeps -------------------------------------------------------------------
b = add('IMG_5003.MOV', 1.0, 3.0, trans='punch')
add('IMG_5004.HEIC', 0.8)
add('IMG_0645.MOV', 0.8, 3.0)
add('IMG_5010.MOV', 1.0, 4.5, speed=1.4)
stamp('4:00am', 'switch to the jeeps', ('🚙', '🌙'), b, t)

# --- 4:40am reached the sunrise point: stars + breakfast box ------------------------
b = add('IMG_0649.HEIC', 1.0, trans='punch', zoom=(1.0, 1.08))
add('IMG_0652.HEIC', 0.9, zoom=(1.06, 1.0))
bb = add('IMG_0651.MOV', 1.5, 7.0)
stamp('4:40am', 'reached the sunrise point', ('🌌', '✨'), b, t)
tag_in('breakfast box in the jeep', '🍱', bb + 0.1, t)

# --- 5:10am photoshoot under the stars ----------------------------------------------
b = add('IMG_5027.heic', 0.7, trans='flash')
add('IMG_5029.heic', 0.7, trans='flash')
add('IMG_5031.HEIC', 0.7, trans='flash')
add('IMG_5032.heic', 0.8, trans='flash')
stamp('5:10am', 'photoshoot under the stars', ('📸', '⭐'), b, t)

# --- 5:20am the hut + food ----------------------------------------------------------
b = add('IMG_5036.MOV', 1.0, 0.2, trans='punch')
add('IMG_0684.MOV', 1.4, 4.0)
add('IMG_5037.HEIC', 0.9)
stamp('5:20am', 'cup noodles at the hut', ('🍜', '☕'), b, t)

# --- 5:45am first light (timelapse) --------------------------------------------------
b = add('IMG_0702.MOV', 2.6, 2.0, speed=12, trans='punch', zoom=(1.0, 1.0))
stamp('5:45am', 'first light', ('🌄', '🥹'), b, t)

# --- 6:00am sunrise photoshoot -------------------------------------------------------
b = add('IMG_5053.HEIC', 0.7, trans='flash')
add('IMG_5057.HEIC', 0.8, trans='flash')
add('IMG_5062.HEIC', 0.8, trans='flash')
add('IMG_5091.heic', 0.9, trans='flash')
stamp('6:00am', 'sunrise photoshoot', ('📸', '🧡'), b, t)

# --- 6:15am sea of clouds ------------------------------------------------------------
b = add('IMG_5097.MOV', 1.1, 3.0, trans='punch')
add('IMG_0722.MOV', 1.1, 2.0, pan=(0.6, 0.5))
add('IMG_0727.MOV', 1.2, 3.5)
stamp('6:15am', 'sea of clouds', ('☁️', '🌋'), b, t)

# --- 6:35am sun is up ----------------------------------------------------------------
b = add('IMG_0761.MOV', 1.0, 3.0, trans='punch')
add('IMG_0769.MOV', 1.2, 1.0)
add('IMG_0767.HEIC', 0.8)
stamp('6:35am', 'and there it is', ('☀️', '😍'), b, t)

# --- 7:40am black lava + photoshoot on the rocks -------------------------------------
b = add('IMG_0777.MOV', 1.2, 2.5, trans='punch')
add('IMG_0778.MOV', 1.0, 38.0)
stamp('7:40am', 'black lava from past eruptions', ('🖤', '🌋'), b, t)
pb = add('IMG_0779.MOV', 2.2, 1.0, soft=0.25)
for i, (pic, ang, pos) in enumerate([('PIC01582.JPG', -6, (420, 880)), ('PIC01605.JPG', 5, (660, 1010)),
                                     ('PIC01613.JPG', -3, (540, 1140))]):
    top.append(Overlay(pb + 0.15 + 0.5 * i, t, polaroid(F + pic, 560, ang), pos, 'drop'))
callout([('photoshoot', 120, 'c'), ('on the rocks', 80, 'c', WHITE)], ('📸', '🖤'), pb, t, 400)

# --- 8:05am back through the farms ---------------------------------------------------
b = add('IMG_0780.MOV', 2.4, 6.0, trans='punch')
stamp('8:05am', 'back through the farms', ('🌿', '🚙'), b, t)

# --- end: book on klook ---------------------------------------------------------------
e0 = add('IMG_5066.HEIC', 3.2, zoom=(1.0, 1.06))
callout([('book on', 100, 'c', WHITE), ('klook', 210, 'c'), ('discount off klook experiences', 58, 'c', WHITE)],
        None, e0 + 0.1, t, 460)
top.append(Overlay(e0 + 0.4, t, sticker('🎟️', 100), (W / 2 + 230, 440), 'bounce', 7))
top.append(Overlay(e0 + 0.5, t, sticker('🧡', 100), (W / 2 - 230, 450), 'bounce', -7))
tag_in('code in caption', '👀', e0 + 0.8, t, 700)

total = t
print(f'total {total:.1f}s, {len(shots)} shots')
render(shots, ov + top, [], [], OUT, total=total)      # silent: trending sound goes on in TikTok
print('wrote', OUT)
