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


def _proxy(shot):
    """Transcode the used part of a clip to 1080x1920@30 H.264 (cached)."""
    key = hashlib.md5(f'{shot.src}|{shot.ss}|{shot.dur}|{shot.speed}|{shot.freeze}'.encode()).hexdigest()[:12]
    out = CACHE / f'{Path(shot.src).stem}_{key}.mp4'
    if out.exists():
        return out
    src_len = 0.05 if shot.freeze else shot.dur * shot.speed + 0.2
    vf = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setpts=PTS/{shot.speed},fps={FPS}'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{shot.ss:.3f}', '-t', f'{src_len:.3f}', '-i', shot.src,
                    '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', str(out)], check=True)
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
        fill = ImageOps.fit(im, (W, H))
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
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombuffer('RGB', (W, H), buf)
        return self.last

    def close(self):
        if hasattr(self, 'proc'):
            self.proc.stdout.close()
            self.proc.wait()


def _zoom(im, s, pan=(0.5, 0.5), dx=0):
    if abs(s - 1) < 1e-3 and not dx:
        return im
    cw, ch = W / s, H / s
    cx = pan[0] * W - dx / s
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(pan[1] * H - ch / 2, 0), H - ch)
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


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
        if out < 0.15 and self.anim != 'none':
            alpha *= out / 0.15
        if self.wobble:
            rot = self.wobble * math.sin(2 * math.pi * a / 1.6)
        if self.anim == 'drop':
            rot += rot0
        spr = self.layer
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
            col = BUTTER if w.strip('.,?!:').lower() in highlight else (255, 255, 255)
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
def render(shots, overlays, sfx, og_audio, out_path, vo_path=None):
    total = sum(s.dur for s in shots)
    nframes = int(round(total * FPS))
    silent = str(CACHE / 'video_only.mp4')
    if os.environ.get('AUDIO_ONLY'):
        return _mux(silent, total, sfx, og_audio, out_path, vo_path)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                            '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    starts = np.cumsum([0] + [s.dur for s in shots])
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
        p = lt / sh.dur
        s = sh.zoom[0] + (sh.zoom[1] - sh.zoom[0]) * p
        dx = 0
        tr = min(lt / 0.2, 1)                             # 0.2s transition-in
        if sh.trans == 'punch' and tr < 1:
            s *= 1 + 0.18 * (1 - tr) ** 2
        if sh.trans == 'whip' and tr < 1:
            dx = int((1 - tr) ** 2 * W * 0.6)
        if sh.trans == 'zoomblur' and tr < 1:
            s *= 1 + 0.45 * (1 - tr) ** 2
        im = _zoom(base, s, sh.pan, dx)
        if sh.trans in ('whip', 'zoomblur') and tr < 1:
            im = im.filter(ImageFilter.BoxBlur(int(25 * (1 - tr)) + 1))
        if sh.trans == 'slide' and tr < 1:
            off = int((1 - (1 - (1 - tr) ** 3)) * H)
            prev = getattr(render, '_last', im)
            frame = prev.copy()
            frame.paste(im.crop((0, 0, W, H - off)), (0, off))
            im = frame
        if sh.soft:
            im = ImageEnhance.Brightness(im.resize((W // 6, H // 6)).resize((W, H), Image.BILINEAR)).enhance(1 - sh.soft)
        canvas = im.convert('RGBA')
        if sh.trans == 'flash' and lt < 0.18:
            canvas.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (1 - lt / 0.18)))))
        for o in overlays:
            o.draw(canvas, t)
        render._last = im
        enc.stdin.write(canvas.convert('RGB').tobytes())
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
        last_sp, (lx, ly) = out[-1] if len(out) == 1 else max(out, key=lambda o: o[0].width)
        out.append((sticker(ch, emoji_size), (lx + last_sp.width / 2 + emoji_size * 0.35, ly - emoji_size * 0.35)))
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
