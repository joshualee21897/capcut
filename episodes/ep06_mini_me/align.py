"""Register frames of the booth clips to a reference frame (scale + translation) using the booth sign/frame
as a template: brute-force scales + FFT normalised cross-correlation (numpy only)."""
import subprocess
from io import BytesIO
import numpy as np
from PIL import Image, ImageFilter

WS = 360            # working width


def frame(path, t, w=WS):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1',
                        '-vf', f'scale={w}:-2', '-f', 'image2pipe', '-c:v', 'png', '-'], capture_output=True).stdout
    return Image.open(BytesIO(r)).convert('L')


def _edges(im):
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(1))).astype(float)
    gx = np.abs(np.diff(a, axis=1, prepend=a[:, :1]))
    gy = np.abs(np.diff(a, axis=0, prepend=a[:1]))
    return gx + gy


def _ncc(img, tpl):
    th, tw = tpl.shape
    t = tpl - tpl.mean()
    t /= (np.sqrt((t ** 2).sum()) + 1e-9)
    H, W = img.shape
    F = np.fft.rfft2(img, s=(H + th, W + tw))
    Ft = np.fft.rfft2(t[::-1, ::-1], s=(H + th, W + tw))
    corr = np.fft.irfft2(F * Ft, s=(H + th, W + tw))[th - 1:H, tw - 1:W]
    c1 = np.pad(np.cumsum(np.cumsum(img, 0), 1), ((1, 0), (1, 0)))
    c2 = np.pad(np.cumsum(np.cumsum(img ** 2, 0), 1), ((1, 0), (1, 0)))
    box = lambda c: c[th:, tw:] - c[:-th, tw:] - c[th:, :-tw] + c[:-th, :-tw]
    s1, s2 = box(c1), box(c2)
    var = np.maximum(s2 - s1 ** 2 / (th * tw), 1e-6)
    return corr / np.sqrt(var)


def register(ref_path, ref_t, path, t, box=(0.04, 0.03, 0.80, 0.40)):
    """Return (s, dx, dy): ref_xy = s * tgt_xy + (dx, dy), in working (WS-wide) pixels."""
    ref, tgt = _edges(frame(ref_path, ref_t)), frame(path, t)
    H, W = ref.shape
    x0, y0, x1, y1 = int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)
    tpl = ref[y0:y1, x0:x1]
    best = None
    for s in np.linspace(0.75, 1.35, 31):
        im = _edges(tgt.resize((int(tgt.width * s), int(tgt.height * s)), Image.BILINEAR))
        if im.shape[0] < tpl.shape[0] or im.shape[1] < tpl.shape[1]:
            continue
        c = _ncc(im, tpl)
        iy, ix = np.unravel_index(np.argmax(c), c.shape)
        if best is None or c[iy, ix] > best[0]:
            best = (c[iy, ix], s, ix, iy)
    score, s, ix, iy = best
    # template top-left (x0,y0) in ref corresponds to (ix,iy) in the s-scaled target
    return s, x0 - ix, y0 - iy, score
