"""Lock handheld booth clips to one reference frame: per-shot scale, per-frame sub-pixel translation
(FFT normalised cross-correlation on the booth sign), smoothed, then crop the same booth-relative rectangle."""
import subprocess
import numpy as np
from PIL import Image
from align import register, frame, _edges, _ncc, WS

SRC_W, SRC_H = 2160, 3840


def _peak(c):
    iy, ix = np.unravel_index(np.argmax(c), c.shape)
    def sub(a, i):
        if 0 < i < len(a) - 1:
            d = a[i - 1] - 2 * a[i] + a[i + 1]
            return i + (0.5 * (a[i - 1] - a[i + 1]) / d if d else 0)
        return float(i)
    return sub(c[iy], ix), sub(c[:, ix], iy), c[iy, ix]


BOTTOM = (0.03, 0.72, 0.45, 0.92)          # Buzz/Woody/Jessie standee + base (in front of the people)


def track(path, ss, dur, ref, box, s_fix=None, fps=30, bottom=BOTTOM):
    """Per-frame (s, dx, sy, ty): ref_x = sc_x + dx, ref_y = sy * sc_y + ty, where sc = target scaled by s.
    The top template (booth sign) and the bottom template (standees) are matched separately, so the vertical
    scale absorbs the different camera height and the whole booth stays put."""
    ref_e = _edges(frame(*ref))
    H, W = ref_e.shape
    def band(b):
        x0, y0, x1, y1 = int(b[0] * W), int(b[1] * H), int(b[2] * W), int(b[3] * H)
        return (x0, y0), ref_e[y0:y1, x0:x1]
    (tx0, ty0), tpl_t = band(box)
    (bx0, by0), tpl_b = band(bottom)
    s = s_fix or register(*ref, path, ss + dur / 2, box=box)[0]
    hw = int(round(SRC_H * WS / SRC_W))
    w_, h_ = int(WS * s), int(hw * s)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-t', f'{dur + 0.1:.3f}', '-i', path,
                          '-vf', f'scale={w_}:{h_},fps={fps}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                         capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h_, w_)
    out = []
    for f in frames:
        e = _edges(Image.fromarray(f))
        pxt, pyt, _ = _peak(_ncc(e, tpl_t))
        # bottom band: search near where the top match predicts it (vertical scale 0.90..1.06, x within +-14)
        cb = _ncc(e, tpl_b)
        xb = int(round(pxt + (bx0 - tx0)))
        y_lo = max(int(pyt + (by0 - ty0) / 1.06), 0); y_hi = min(int(pyt + (by0 - ty0) / 0.90) + 1, cb.shape[0])
        x_lo, x_hi = max(xb - 14, 0), min(xb + 15, cb.shape[1])
        win = cb[y_lo:y_hi, x_lo:x_hi]
        if win.size:
            pxb_w, pyb_w, _ = _peak(win)
            pxb, pyb = x_lo + pxb_w, y_lo + pyb_w
        else:
            pxb, pyb = pxt + (bx0 - tx0), pyt + (by0 - ty0)
        # affine (scale s, vertical scale sy, slight x-shear k) that lands both the sign and the standees:
        #   ref_x = sc_x + dx + k * sc_y        ref_y = sy * sc_y + ty
        sy = (by0 - ty0) / (pyb - pyt)
        ty = ty0 - sy * pyt
        k = ((bx0 - pxb) - (tx0 - pxt)) / (pyb - pyt)
        dx = tx0 - pxt - k * pyt
        out.append((s, dx, sy, ty, k))
    a = np.array(out)
    k = 5                                                      # smooth (keep it locked, no jitter)
    for j in (1, 2, 3, 4):
        pad = np.pad(a[:, j], (k, k), mode='edge')
        a[:, j] = np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode='valid')
    return a


def coverage(tr):
    """Region of the reference (working coords) covered by every frame of a track."""
    hw = SRC_H * WS / SRC_W
    def xr(t, y):                           # ref x of the target's left/right edge at target row y (scaled)
        s, dx, sy, ty, k = t
        return dx + k * y, dx + k * y + s * WS
    xs0 = max(max(xr(t, 0)[0], xr(t, t[0] * hw)[0]) for t in tr)
    xs1 = min(min(xr(t, 0)[1], xr(t, t[0] * hw)[1]) for t in tr)
    ys0 = max(t[3] for t in tr); ys1 = min(t[3] + t[2] * t[0] * hw for t in tr)
    return xs0, ys0, xs1, ys1


def render_locked(path, ss, dur, tr, crop, out, size=(1080, 1920), fps=30, plate=None):
    """Write the clip cropped to `crop` (reference working coords) for every frame using its track."""
    m = SRC_W / WS
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{size[0]}x{size[1]}',
                            '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14',
                            '-pix_fmt', 'yuv420p', str(out)], stdin=subprocess.PIPE)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-t', f'{dur + 0.1:.3f}', '-i', path,
                            '-vf', f'fps={fps}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = 0
    while True:
        buf = dec.stdout.read(SRC_W * SRC_H * 3)
        if len(buf) < SRC_W * SRC_H * 3:
            break
        s, dx, sy, ty, k = tr[min(n, len(tr) - 1)]
        rx, ry = (crop[2] - crop[0]) / size[0], (crop[3] - crop[1]) / size[1]
        q = m / s
        coef = (rx * q, -k * ry / sy * q, (crop[0] - dx - k * (crop[1] - ty) / sy) * q,
                0.0, ry / sy * q, (crop[1] - ty) / sy * q)
        im = Image.frombuffer('RGB', (SRC_W, SRC_H), buf).transform(size, Image.AFFINE, coef, Image.BICUBIC)
        if plate is not None:                  # fill any area this camera didn't see with the still booth plate
            mask = Image.new('L', (SRC_W, SRC_H), 255).transform(size, Image.AFFINE, coef, Image.BILINEAR)
            if mask.getextrema()[0] < 255:
                from PIL import ImageFilter
                mask = mask.point(lambda v: 255 if v > 250 else 0).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(6))
                base = plate.copy()
                base.paste(im, (0, 0), mask)
                im = base
        enc.stdin.write(im.tobytes())
        n += 1
    dec.stdout.close(); dec.wait()
    enc.stdin.close(); enc.wait()
    return n
