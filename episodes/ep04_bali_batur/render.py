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


def polaroids(items, t0, t1, gap=0.35):
    """Polaroids spread out so every photo stays visible: items = [(file, width, angle, (x, y))]."""
    for i, (pic, w, ang, pos) in enumerate(items):
        top.append(Overlay(t0 + 0.15 + gap * i, t1, polaroid(F + pic, w, ang), pos, 'drop', safe=False))


# --- hook: the two of us watching the sunrise ------------------------------------
h0 = add('IMG_0726.MOV', 2.4, 7.6, pan=(0.3, 0.5), zoom=(1.0, 1.05))
callout([('waking up at', 96, 'c', WHITE), ('2am', 230, 'c'), ('was worth it', 104, 'c', WHITE)], ('🌅', '🥱'),
        h0 + 0.05, h0 + 2.4, 470, emoji_size=120)

# --- 2:20am pickup (video only) ------------------------------------------------------
b = add('IMG_0636.MOV', 1.2, 0.8, trans='punch')
add('IMG_5002.MOV', 2.0, 4.0)
stamp('2:20am', 'pickup from our airbnb', ('🚐', '😴'), b, t)

# --- 4:00am jeeps (more airtime, all video) -----------------------------------------
b = add('IMG_5003.MOV', 1.4, 2.0, trans='punch')
add('IMG_0640.MOV', 1.8, 6.6)
add('IMG_0645.MOV', 1.4, 2.6)
add('IMG_5010.MOV', 1.2, 4.5, speed=1.4)
add('IMG_5003.MOV', 1.4, 15.2)
stamp('4:00am', 'switch to the jeeps', ('🚙', '🌙'), b, t)

# --- 4:40am reached the sunrise point: our view (photos as polaroids) + breakfast box -
b = add('IMG_5012.MOV', 3.0, 3.0, soft=0.35, trans='punch')
stamp('4:40am', 'reached the sunrise point', ('🌌', '✨'), b, t)
polaroids([('IMG_0649.HEIC', 290, -7, (270, 1000)), ('IMG_0648.HEIC', 290, 2, (540, 1060)),
           ('IMG_0652.HEIC', 290, 8, (810, 1000))], b, t)
tag_in('this was our view', '👀', b + 1.2, t, 1440)
bb = add('IMG_0651.MOV', 1.6, 7.0)
tag_in('breakfast box in the jeep', '🍱', bb + 0.1, t)

# --- 5:10am photoshoot under the stars (polaroids over the night video) -------------
b = add('IMG_5015.MOV', 3.0, 6.0, zoom=(1.0, 1.0), trans='punch')
stamp('5:10am', 'photoshoot under the stars', ('📸', '⭐'), b, t)
polaroids([('IMG_5027.heic', 290, -7, (270, 1000)), ('IMG_5029.heic', 290, 2, (540, 1060)),
           ('IMG_5031.HEIC', 290, 8, (810, 1000))], b, t)

# --- 5:20am the hut + food (video only) ----------------------------------------------
b = add('IMG_5036.MOV', 1.0, 0.2, trans='punch')
add('IMG_0684.MOV', 1.6, 2.5)
stamp('5:20am', 'cup noodles at the hut', ('🍜', '☕'), b, t)

# --- 5:45am first light (timelapse) --------------------------------------------------
b = add('IMG_0702.MOV', 2.6, 2.0, speed=12, trans='punch', zoom=(1.0, 1.0))
stamp('5:45am', 'first light', ('🌄', '🥹'), b, t)

# --- 6:00am sunrise photoshoot: photographer at work, then polaroids -----------------
b = add('IMG_0703.MOV', 2.0, 0.6, trans='punch')
stamp('6:00am', 'sunrise photoshoot', ('📸', '🧡'), b, t + 3.2)
tag_in('our driver is also our photographer', '📸', b + 0.3, t)
pb = add('IMG_0707.MOV', 3.2, 2.5)
polaroids([('IMG_5053.HEIC', 300, -6, (320, 820)), ('IMG_5057.HEIC', 300, 5, (760, 800)),
           ('IMG_5062.HEIC', 300, 4, (330, 1250)), ('IMG_5091.heic', 300, -5, (760, 1270))], pb, t, gap=0.3)

# --- 6:15am sea of clouds ------------------------------------------------------------
b = add('IMG_5097.MOV', 1.1, 3.0, trans='punch')
add('IMG_0722.MOV', 1.1, 2.0, pan=(0.6, 0.5))
add('IMG_0727.MOV', 1.2, 3.5)
stamp('6:15am', 'sea of clouds', ('☁️', '🌋'), b, t, y=660)

# --- 6:35am sun is up (sunrise only) -------------------------------------------------
b = add('IMG_0761.MOV', 1.1, 3.0, trans='punch')
add('IMG_0769.MOV', 1.2, 1.0)
add('IMG_0766.MOV', 1.0, 1.5)
add('IMG_0765.MOV', 1.4, 5.0)
stamp('6:35am', 'and there it is', ('☀️', '😍'), b, t, y=660)

# --- 7:40am black lava + photoshoot on the rocks -------------------------------------
b = add('IMG_0777.MOV', 1.2, 2.5, trans='punch')
add('IMG_0778.MOV', 1.0, 38.0)
stamp('7:40am', 'black lava from past eruptions', ('🖤', '🌋'), b, t)
pb = add('IMG_0779.MOV', 2.6, 1.0, soft=0.25)
polaroids([('PIC01604.JPG', 330, -5, (300, 960)), ('PIC01605.JPG', 430, 4, (700, 800)),
           ('PIC01613.JPG', 430, -3, (700, 1250))], pb, t)
callout([('photoshoot', 120, 'c'), ('on the rocks', 80, 'c', WHITE)], ('📸', '🖤'), pb, t, 400)

# --- 8:05am back through the farms ---------------------------------------------------
b = add('IMG_0780.MOV', 2.4, 6.0, trans='punch')
stamp('8:05am', 'back through the farms', ('🌿', '🚙'), b, t)

# --- 8:44am back to our airbnb -------------------------------------------------------
b = add('IMG_0820.MOV', 2.4, 0.2, trans='punch')
stamp('8:44am', 'back to our airbnb', ('🏠', '😴'), b, t)

# --- end: book on klook ---------------------------------------------------------------
e0 = add('IMG_5065.HEIC', 3.2, zoom=(1.0, 1.06))
callout([('book on', 100, 'c', WHITE), ('klook', 210, 'c')], None, e0 + 0.1, t, 440)
top.append(Overlay(e0 + 0.4, t, sticker('🎟️', 100), (W / 2 + 230, 440), 'bounce', 7))
top.append(Overlay(e0 + 0.5, t, sticker('🧡', 100), (W / 2 - 230, 450), 'bounce', -7))
tag_in('use code ROCHELLEKLOOK', '🎟️', e0 + 0.6, t, 660)
top.append(Overlay(e0 + 0.9, t, sprite_text('discount off klook experiences', font('bootzy', 62), WHITE, shadow=14, pad=24),
                   (W / 2, 760), 'pop'))

total = t
print(f'total {total:.1f}s, {len(shots)} shots')
render(shots, ov + top, [], [], OUT, total=total)      # silent: trending sound goes on in TikTok
print('wrote', OUT)
