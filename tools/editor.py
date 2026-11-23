"""Tiny frame-by-frame vertical video editor (PIL compositing + FFmpeg I/O).

Timeline = list of Shot (sequential). Overlays are timed elements drawn on top.
Audio = SFX hits + optional original-audio snippets (+ later the voiceover).
"""
import math, subprocess, os, hashlib
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance
from style import *

FPS = 30
SCALE = int(os.environ.get('EDIT_SCALE', '2'))      # 2 = 4K output (2160x3840); layout stays in 1080 units
OW, OH = W * SCALE, H * SCALE
CACHE = Path(os.environ.get('EDIT_CACHE', '/home/user/edit_cache'))
CACHE.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------- shots
@dataclass
class Shot:
    src: str                       # video or photo path, or a callable(t)->Image for generated frames
    dur: float
    ss: float = 0.0                # source in-point (video)
    speed: float = 1.0
    zoom: tuple = (1.0, 1.06)      # start/end scale (slow push-in by default)
    trans: str = 'cut'             # cut | punch | whip | flash
    freeze: bool = False           # hold the in-point frame
    photo_style: str = 'fill'      # fill | polaroid (for stills)
    pan: tuple = (0.5, 0.5)        # zoom centre (fraction of frame)
    soft: float = 0.0              # >0: dim + soften (background under a photo/card)


def _probe_color(src):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer',
                        '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip()
    return r


# light film look (not vintage): soft lifted blacks, gentle highlight roll-off, warm highs / cool lows,
# faint moving grain, very mild vignette
FILM = ("curves=all='0/0.035 0.25/0.24 0.5/0.5 0.75/0.765 1/0.97',"
        "colorbalance=rh=0.025:gh=0.008:bh=-0.02:rs=-0.012:bs=0.015,"
        "vignette=angle=0.32,noise=alls=4:allf=t")


TONEMAP = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,'
           'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,')


def _grade(src, ss, pre):
    """Auto colour-match: measure a frame, return an eq filter that pulls brightness and
    saturation towards a common target so every clip looks like the same video."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ss:.2f}', '-i', src, '-frames:v', '1',
                          '-vf', pre + 'scale=180:320', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    if not raw:
        return 'eq=contrast=1.04:saturation=1.08'
    a = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.float32) / 255
    luma = float((a @ np.array([0.2126, 0.7152, 0.0722])).mean())
    mx, mn = a.max(1), a.min(1)
    sat = float(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-3), 0).mean())
    gamma = float(np.clip(np.log(max(luma, 0.05)) / np.log(0.47), 0.8, 1.45))
    satf = float(np.clip(0.36 / max(sat, 0.05), 0.95, 1.4))
    return f'eq=contrast=1.05:gamma={gamma:.3f}:saturation={satf:.3f}'


def _proxy(shot):
    """Transcode the used part of a clip to OWxOH@30 H.264, tone-mapped (HDR) and colour-matched (cached)."""
    key = hashlib.md5(f'v5|{OW}|{shot.src}|{shot.ss}|{shot.dur}|{shot.speed}|{shot.freeze}'.encode()).hexdigest()[:12]
    out = CACHE / f'{Path(shot.src).stem}_{key}.mp4'
    if out.exists():
        return out
    pre = TONEMAP if _probe_color(shot.src) in ('arib-std-b67', 'smpte2084') else ''
    eq = _grade(shot.src, shot.ss + min(shot.dur, 2) / 2, pre)
    src_len = 0.05 if shot.freeze else shot.dur * shot.speed + 0.2
    vf = (pre + f'scale={OW}:{OH}:force_original_aspect_ratio=increase:flags=lanczos,crop={OW}:{OH},'
          f'setpts=PTS/{shot.speed},fps={FPS},{eq},{FILM}')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{shot.ss:.3f}', '-t', f'{src_len:.3f}', '-i', shot.src,
                    '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', str(out)], check=True)
    return out


class FrameSource:
    def __init__(self, shot):
        self.shot, self.n = shot, 0
        ext = Path(shot.src).suffix.lower() if isinstance(shot.src, str) else ''
        self.still = None
        if callable(shot.src):
            self.gen = shot.src
        elif ext in ('.jpg', '.jpeg', '.png'):
            self.still = self._photo(shot.src, shot.photo_style)
        else:
            p = _proxy(shot)
            self.proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                         stdout=subprocess.PIPE)
            self.last = None

    @staticmethod
    def _photo(path, style):
        im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        im.thumbnail((2000, 2000))
        im.thumbnail((OH, OH))
        fill = ImageOps.fit(im, (OW, OH))
        if style == 'fill':
            return fill
        bg = ImageEnhance.Brightness(fill.filter(ImageFilter.GaussianBlur(30))).enhance(0.6)
        pw = 760
        ph = int(pw * im.height / im.width)
        if ph > 1100:
            ph = 1100
            pw = int(ph * im.width / im.height)
        card = Image.new('RGB', (pw + 50, ph + 170), (252, 250, 245))
        card.paste(im.resize((pw, ph)), (25, 25))
        card = card.convert('RGBA').rotate(-4, resample=Image.BICUBIC, expand=True)
        bg = bg.convert('RGBA')
        sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
        sh.paste((0, 0, 0, 120), mask=card.split()[3])
        x, y = (W - card.width) // 2, (H - card.height) // 2 - 60
        bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), (x + 12, y + 20))
        bg.alpha_composite(card, (x, y))
        return bg.convert('RGB')

    def frame(self, t):
        if self.still is not None:
            return self.still
        if hasattr(self, 'gen'):
            return self.gen(t)
        if self.shot.freeze and self.last is not None:
            return self.last
        buf = self.proc.stdout.read(OW * OH * 3)
        if len(buf) == OW * OH * 3:
            self.last = Image.frombuffer('RGB', (OW, OH), buf)
        return self.last

    def close(self):
        if hasattr(self, 'proc'):
            self.proc.stdout.close()
            self.proc.wait()


def _zoom(im, s, pan=(0.5, 0.5), dx=0):
    if abs(s - 1) < 1e-3 and not dx:
        return im
    cw, ch = OW / s, OH / s
    cx = pan[0] * OW - dx * SCALE / s
    x0 = min(max(cx - cw / 2, 0), OW - cw)
    y0 = min(max(pan[1] * OH - ch / 2, 0), OH - ch)
    return im.resize((OW, OH), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def ease_out_back(x, k=1.70158):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


# ----------------------------------------------------------------------------- overlays
@dataclass
class Overlay:
    t0: float
    t1: float
    layer: Image.Image             # RGBA sprite
    pos: tuple                     # centre
    anim: str = 'pop'              # pop | fade | slide_up | none
    wobble: float = 0.0            # degrees of idle rotation sway
    full: bool = False             # full-frame layer (pos ignored)
    turn: bool = False             # fake left/right turn (horizontal squash) like an animated sticker
    fade_out: bool = True

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        a = t - self.t0
        scale, alpha, dy, rot = 1.0, 1.0, 0, 0.0
        if self.anim == 'pop':
            scale = max(0.01, ease_out_back(min(a / 0.28, 1)))
        elif self.anim == 'bounce':                         # strong sticker bounce
            scale = max(0.01, ease_out_back(min(a / 0.35, 1), 3.2))
        elif self.anim == 'drop':                           # falls in from above, settles
            p = min(a / 0.45, 1)
            dy = int(-(1 - ease_out_back(p, 1.2)) * 700)
            rot0 = (1 - p) * 14
        elif self.anim == 'fade':
            alpha = min(a / 0.25, 1)
        elif self.anim == 'slide_up':  # noqa
            p = min(a / 0.6, 1)
            dy = int((1 - (1 - (1 - p) ** 3)) * (H * 0.7))
        out = self.t1 - t
        if out < 0.15 and self.anim != 'none' and self.fade_out:
            alpha *= out / 0.15
        if self.wobble:
            rot = self.wobble * math.sin(2 * math.pi * a / 1.6)
        if self.anim == 'drop':
            rot += rot0
        spr = self.layer
        if self.turn:
            sx = 0.86 + 0.14 * abs(math.cos(math.pi * a / 1.3))
            spr = spr.resize((max(1, int(spr.width * sx)), spr.height), Image.BILINEAR)
        if self.full and scale == 1 and not rot:
            if alpha < 1:
                spr = spr.copy()
                spr.putalpha(spr.split()[3].point(lambda v: int(v * alpha)))
            canvas.alpha_composite(spr, (0, dy))
            return
        if scale != 1:
            spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
        if rot:
            spr = spr.rotate(rot, resample=Image.BILINEAR, expand=True)
        if alpha < 1:
            spr = spr.copy()
            spr.putalpha(spr.split()[3].point(lambda v: int(v * alpha)))
        cx, cy = (W / 2, H / 2) if self.full else self.pos
        x, y = int(cx - spr.width / 2), int(cy - spr.height / 2 + dy)
        canvas.alpha_composite(spr, (max(x, 0), max(y, 0)),
                               (max(-x, 0), max(-y, 0)))


def sprite_text(s, f, fill, shadow=8, pad=30):
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), s, font=f, anchor='lt')
    im = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    text(im, (pad - l, pad - t), s, f, fill, anchor='lt', shadow=shadow)
    return im


def sprite_emoji(ch, size):
    return emoji(ch, size)


def sprite_tag(s, size=46, ch=None):
    f = font('caption_reg', size)
    e = size + 12 if ch else 0
    w, h = int(f.getlength(s)) + 44 + (e + 14 if ch else 0), size + 30
    im = Image.new('RGBA', (w, h), TAG_BG)
    d = ImageDraw.Draw(im)
    if ch:
        im.alpha_composite(emoji(ch, e), (18, (h - e) // 2))
    d.text(((w + (e + 14 if ch else 0)) / 2, h / 2), s, font=f, fill=TAG_FG, anchor='mm')
    return im


class Karaoke:
    """One caption line: all words shown dim, each word fills to full colour as it's spoken.
    words: [(word, t_start), ...]; highlight: set of lowercase words drawn in BUTTER."""
    DIM = 120

    def __init__(self, words, t1, y=1400, size=44, highlight=()):
        self.t0, self.t1, self.y = words[0][1], t1, y
        f = font('caption', size)
        pad, gap = 30, f.getlength(' ')
        widths = [f.getlength(w) for w, _ in words]
        tw = sum(widths) + gap * (len(words) - 1)
        asc, desc = f.getmetrics()
        hgt = asc + desc + 2 * pad
        self.full = Image.new('RGBA', (int(tw + 2 * pad), hgt), (0, 0, 0, 0))
        self.dim = Image.new('RGBA', self.full.size, (0, 0, 0, 0))
        x, self.edges = pad, []
        for (w, ts), ww in zip(words, widths):
            col = BUTTER if w.lower() in highlight else (255, 255, 255)
            text(self.full, (x, pad), w, f, col, anchor='la', shadow=6)
            ImageDraw.Draw(self.dim).text((x, pad), w, font=f, fill=col + (self.DIM,), anchor='la')
            x += ww + gap
            self.edges.append((ts, int(x - gap / 2)))
        sh = Image.new('RGBA', self.dim.size, (0, 0, 0, 0))
        sh.putalpha(self.dim.split()[3].point(lambda v: v // 2))
        self.dim = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), self.dim)

    def draw(self, canvas, t):
        if not (self.t0 <= t < self.t1):
            return
        x0, y0 = int((W - self.full.width) / 2), int(self.y - self.full.height / 2)
        canvas.alpha_composite(self.dim, (x0, y0))
        cut = 0
        for ts, edge in self.edges:
            if t >= ts:
                cut = edge
        if cut:
            canvas.alpha_composite(self.full.crop((0, 0, cut, self.full.height)), (x0, y0))


def karaoke_from_script(paragraphs, starts, ends, words_per=5, highlight=(), y=1400, size=44):
    """Placeholder word timing: words evenly spread over each paragraph (until the VO exists)."""
    out = []
    for para, t0, t1 in zip(paragraphs, starts, ends):
        words = para.lower().split()
        step = (t1 - t0) / len(words)
        for i in range(0, len(words), words_per):
            chunk = [(w, t0 + (i + j) * step) for j, w in enumerate(words[i:i + words_per])]
            end = t0 + min(i + words_per, len(words)) * step
            out.append(Karaoke(chunk, end, y, size, highlight))
    return out


def polaroid(path, width=640, angle=-4):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    im.thumbnail((1600, 1600))
    ph = int(width * im.height / im.width)
    if ph > 860:
        ph, width = 860, int(860 * im.width / im.height)
    card = Image.new('RGBA', (width + 44, ph + 150), (252, 250, 245, 255))
    card.paste(im.resize((width, ph)), (22, 22))
    card = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    out = Image.new('RGBA', (card.width + 40, card.height + 50), (0, 0, 0, 0))
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 120), mask=card.split()[3])
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (24, 34))
    out.alpha_composite(card, (10, 10))
    return out


def captions_from_script(paragraphs, starts, ends, words_per=4):
    """Placeholder caption chunks spread evenly over each paragraph's time window."""
    out = []
    for para, t0, t1 in zip(paragraphs, starts, ends):
        words = para.lower().split()
        chunks = [' '.join(words[i:i + words_per]) for i in range(0, len(words), words_per)]
        step = (t1 - t0) / len(chunks)
        for i, c in enumerate(chunks):
            out.append((t0 + i * step, t0 + (i + 1) * step, c))
    return out


# ----------------------------------------------------------------------------- render
def render(shots, overlays, sfx, og_audio, out_path, vo_path=None, total=None):
    total = total or sum(s.dur for s in shots)
    nframes = int(round(total * FPS))
    silent = str(CACHE / 'video_only.mp4')
    if os.environ.get('AUDIO_ONLY'):
        return _mux(silent, total, sfx, og_audio, out_path, vo_path)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                            '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    starts = np.cumsum([0] + [s.dur for s in shots])
    white = Image.new('RGB', (OW, OH), (255, 255, 255))
    si, src = -1, None
    for n in range(nframes):
        t = n / FPS
        while si + 1 < len(shots) and t >= starts[si + 1]:
            if src:
                src.close()
            si += 1
            src = FrameSource(shots[si])
        sh = shots[si]
        lt = t - starts[si]
        base = src.frame(lt)
        s = sh.zoom[0] + (sh.zoom[1] - sh.zoom[0]) * min(lt / sh.dur, 1)
        dx, tr = 0, min(lt / 0.2, 1)
        if sh.trans == 'punch' and tr < 1:
            s *= 1 + 0.18 * (1 - tr) ** 2
        if sh.trans == 'whip' and tr < 1:
            dx = int((1 - tr) ** 2 * W * 0.6)
        if sh.trans == 'zoomblur' and tr < 1:
            s *= 1 + 0.45 * (1 - tr) ** 2
        im = _zoom(base, s, sh.pan, dx)
        if sh.trans in ('whip', 'zoomblur') and tr < 1:
            im = im.resize((OW // 8, OH // 8)).resize((OW, OH), Image.BILINEAR) if tr < 0.5 else \
                im.filter(ImageFilter.BoxBlur(int(20 * (1 - tr)) + 1))
        if sh.trans == 'slide' and tr < 1:
            off = int((1 - tr) ** 3 * OH)
            prev = getattr(render, '_last', im)
            frame = prev.copy()
            frame.paste(im.crop((0, 0, OW, OH - off)), (0, off))
            im = frame
        if sh.soft:
            im = ImageEnhance.Brightness(im.resize((OW // 8, OH // 8)).resize((OW, OH), Image.BILINEAR)).enhance(1 - sh.soft)
        if sh.trans == 'flash' and lt < 0.18:
            im = Image.blend(im, white, 1 - lt / 0.18)
        render._last = im
        # overlays are laid out in 1080-wide units, then scaled up onto the 4K frame
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for o in overlays:
            o.draw(ov, t)
        bb = ov.getbbox()
        if bb:
            reg = ov.crop(bb)
            if SCALE != 1:
                reg = reg.resize((reg.width * SCALE, reg.height * SCALE), Image.BICUBIC)
            frame = im.copy() if im is base else im
            frame.paste(reg, (bb[0] * SCALE, bb[1] * SCALE), reg)
            im = frame
        enc.stdin.write(im.tobytes())
    src.close()
    enc.stdin.close()
    enc.wait()
    return _mux(silent, total, sfx, og_audio, out_path, vo_path)


def _mux(silent, total, sfx, og_audio, out_path, vo_path):

    # audio: silence bed + og snippets + sfx (+ vo)
    inputs, filters, labels = ['-f', 'lavfi', '-t', f'{total:.3f}', '-i', 'anullsrc=r=44100:cl=stereo'], [], ['[1:a]']
    k = 2                                           # input 0 = video, 1 = silence bed
    for path, ss, dur, at, vol in og_audio:
        inputs += ['-ss', f'{ss}', '-t', f'{dur}', '-i', path]
        filters.append(f'[{k}:a]volume={vol},afade=t=in:d=0.08,afade=t=out:st={dur - 0.15}:d=0.15,'
                       f'adelay={int(at * 1000)}|{int(at * 1000)}[a{k}]')
        labels.append(f'[a{k}]')
        k += 1
    for path, at, vol in sfx:
        inputs += ['-i', path]
        filters.append(f'[{k}:a]volume={vol},adelay={int(at * 1000)}|{int(at * 1000)}[a{k}]')
        labels.append(f'[a{k}]')
        k += 1
    if vo_path:
        inputs += ['-i', vo_path]
        labels.append(f'[{k}:a]')
        k += 1
    filters.append(f'{"".join(labels)}amix=inputs={len(labels)}:normalize=0,alimiter=limit=0.95[out]')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', silent] + inputs +
                   ['-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[out]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-t', f'{total:.3f}', '-movflags', '+faststart', str(out_path)],
                   check=True)
    return total


# ----------------------------------------------------------------------------- emphasis callouts
def callout_lines(lines, ch=None, color=None, emoji_size=150):
    """Big Bootzy emphasis text in mixed sizes, e.g. [('THIS', 90, 'l'), ('GIANT', 240, 'c'), ('TOAD', 110, 'r')].
    Returns [(sprite, (cx, cy) offset from block centre)] so each line can animate in separately."""
    color = color or BUTTER
    sprites = []
    for s, size, align in lines:
        sprites.append((sprite_text(s, font('bootzy', size), color, shadow=12, pad=24), align))
    wmax = max(sp.width for sp, _ in sprites)
    total_h = sum(sp.height - 40 for sp, _ in sprites)
    y = -total_h / 2
    out = []
    for sp, align in sprites:
        h = sp.height - 40
        dx = {'l': -(wmax - sp.width) / 2, 'r': (wmax - sp.width) / 2}.get(align, 0)
        out.append((sp, (dx, y + h / 2)))
        y += h
    if ch:
        chs = [ch] if isinstance(ch, str) else list(ch)
        wide_sp, (lx, ly) = max(out, key=lambda o: o[0].width)
        half = wide_sp.width / 2
        spots = [(lx + half + emoji_size * 0.3, -total_h / 2 + emoji_size * 0.1, 1),       # top-right
                 (lx - half - emoji_size * 0.3, total_h / 2 - emoji_size * 0.15, -1)]      # bottom-left
        for c, (ex, ey, side) in zip(chs, spots):
            lim = W / 2 - 30 - emoji_size / 2                    # keep the whole sticker on screen
            if abs(ex) > lim:
                ex = side * lim
                ey += -side * emoji_size * 0.55                  # tuck above/below the text instead
            out.append((sticker(c, emoji_size), (ex, ey)))
    return out


def cutout_sprite(path, height, outline=8):
    """Background-removed person as a sticker (white outline + soft shadow), scaled to height."""
    im = Image.open(path).convert('RGBA')
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    pad = outline + 20
    c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    c.alpha_composite(im, (pad, pad))
    a = c.split()[3].point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(outline * 2 + 1))
    out = Image.new('RGBA', c.size, (0, 0, 0, 0))
    sh = Image.new('RGBA', c.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * 0.4))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (6, 10))
    wl = Image.new('RGBA', c.size, (255, 255, 255, 0))
    wl.putalpha(a.filter(ImageFilter.GaussianBlur(1)))
    out.alpha_composite(wl)
    out.alpha_composite(c)
    return out


def parse_emphasis(paragraphs, starts, ends, words_per=5, highlight=(), y=1400, size=44):
    """Paragraphs may mark {emphasised phrases}. Emphasised words are NOT shown as karaoke captions
    (they become big callouts instead). Placeholder timing spreads words evenly over each paragraph.
    Returns (karaoke_list, [(phrase_text, t0, t1), ...])."""
    import re
    kar, phrases = [], []
    for para, t0, t1 in zip(paragraphs, starts, ends):
        toks = []
        for m in re.finditer(r'\{([^}]*)\}|(\S+)', para):
            if m.group(1) is not None:
                ws = m.group(1).split()
                toks += [(w, len(phrases) + 0.5) for w in ws]   # tagged with a temp phrase marker
                phrases.append([m.group(1), None, None])
            else:
                toks.append((m.group(2), None))
        step = (t1 - t0) / len(toks)
        chunk = []

        def flush(end_t):
            if chunk:
                kar.append(Karaoke([(w.lower(), ts) for w, ts in chunk], end_t, y, size, highlight))
                chunk.clear()
        for i, (w, ph) in enumerate(toks):
            ts = t0 + i * step
            if ph is not None:
                flush(ts)
                p = phrases[int(ph)]
                p[1] = ts if p[1] is None else p[1]
                p[2] = ts + step
            else:
                chunk.append((w, ts))
                if len(chunk) == words_per or w.endswith(('.', '?', '!')):
                    flush(ts + step)
        flush(t1)
    return kar, [tuple(p) for p in phrases]


# ----------------------------------------------------------------------------- script <-> voiceover alignment
def _norm(w):
    import re
    return re.sub(r'[^a-z0-9]', '', w.lower())


def align_script(paragraphs, vo_words):
    """Give every script word a time from the cleaned VO's Whisper words (script text wins for spelling).
    Script may contain {emphasis phrases}. Returns list of dicts: w, s, e, para, phrase (id or None)."""
    import re, difflib
    toks, pid = [], 0
    for pi, para in enumerate(paragraphs):
        for m in re.finditer(r'\{([^}]*)\}|(\S+)', para):
            if m.group(1) is not None:
                for w in m.group(1).split():
                    toks.append(dict(w=w, para=pi, phrase=pid))
                pid += 1
            else:
                toks.append(dict(w=m.group(2), para=pi, phrase=None))
    A, B = [_norm(t['w']) for t in toks], [_norm(w['w']) for w in vo_words]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            toks[blk.a + k]['s'], toks[blk.a + k]['e'] = vo_words[blk.b + k]['s'], vo_words[blk.b + k]['e']
    # interpolate unmatched words between their matched neighbours
    known = [i for i, t in enumerate(toks) if 's' in t]
    for i, t in enumerate(toks):
        if 's' in t:
            continue
        lo = max([k for k in known if k < i], default=None)
        hi = min([k for k in known if k > i], default=None)
        t0 = toks[lo]['e'] if lo is not None else 0.0
        t1 = toks[hi]['s'] if hi is not None else t0 + 0.4 * (i - (lo or 0))
        n_lo, n_hi = (lo if lo is not None else -1), (hi if hi is not None else len(toks))
        frac0 = (i - n_lo - 1) / max(n_hi - n_lo - 1, 1)
        frac1 = (i - n_lo) / max(n_hi - n_lo - 1, 1)
        t['s'], t['e'] = t0 + (t1 - t0) * frac0, t0 + (t1 - t0) * frac1
    return toks


def clean_caption_word(w):
    import re
    w = w.replace('-', ' ').replace('%', ' percent')
    return re.sub(r"[^a-z0-9' ]", '', w.lower()).strip()


def build_captions(toks, highlight=(), max_chars=32, y=1400, size=44, y_at=None):
    """Karaoke lines for the non-emphasised words + (text, t0, t1) for each emphasised phrase.
    Lines follow phrases: break at sentence ends / emphasis / paragraphs, ~max_chars per line, never a lone word.
    y_at(t) -> caption y for a line starting at t (lets captions move for an end card)."""
    runs, phrases, cur = [], {}, []
    for t in toks:
        if t['phrase'] is not None:
            if cur:
                runs.append(cur); cur = []
            p = phrases.setdefault(t['phrase'], [[], t['s'], t['e']])
            p[0].append(t['w']); p[2] = t['e']
            continue
        if cur and cur[-1]['para'] != t['para']:
            runs.append(cur); cur = []
        cw = clean_caption_word(t['w']).split()
        for j, part in enumerate(cw):
            cur.append(dict(t, w=part, soft=(j == len(cw) - 1 and t['w'].endswith((',', ':', ';')))))
        if t['w'].endswith(('.', '?', '!')):
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    # merge lone-word runs into a neighbour in the same paragraph
    merged = []
    for r in runs:
        if merged and (len(r) == 1 or len(merged[-1]) == 1) and r[0]['para'] == merged[-1][-1]['para'] \
                and len(' '.join(x['w'] for x in merged[-1] + r)) <= max_chars + 10:
            merged[-1] += r
        else:
            merged.append(r)
    lines = []
    L = lambda ws: len(' '.join(x['w'] for x in ws))
    for r in merged:
        line = []
        for wd in r:
            if line and L(line + [wd]) > max_chars:
                soft = [i for i, x in enumerate(line[:-1]) if x.get('soft') and i >= 1]
                cut = soft[-1] + 1 if soft and L(line[:soft[-1] + 1]) >= 12 else len(line)
                lines.append(line[:cut]); line = line[cut:]
            line.append(wd)
            if wd.get('soft') and L(line) >= 16:              # natural pause: end the line here
                lines.append(line); line = []
        if line:
            if len(line) == 1 and lines and lines[-1][-1]['para'] == line[0]['para'] and L(lines[-1] + line) <= max_chars + 10:
                lines[-1] += line
            else:
                lines.append(line)
    kar = []
    for i, ln in enumerate(lines):
        nxt = lines[i + 1][0]['s'] if i + 1 < len(lines) else None
        end = min(ln[-1]['e'] + 0.4, nxt) if nxt else ln[-1]['e'] + 0.6
        yy = y_at(ln[0]['s']) if y_at else y
        kar.append(Karaoke([(x['w'], x['s']) for x in ln], end, yy, size, highlight))
    return kar, [(' '.join(p[0]), p[1], p[2]) for _, p in sorted(phrases.items())]
