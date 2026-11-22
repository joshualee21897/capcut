"""Log a folder of raw footage cheaply: duration, capture time, Whisper transcript,
and labelled contact sheets (several clips per image) for quick visual review.

usage: python3 tools/log_footage.py <footage_dir> <out_dir>
"""
import json, subprocess, sys, os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
FRAMES, TW = 6, 160            # frames per clip, thumb width
CLIPS_PER_SHEET = 8
VID = {'.mov', '.mp4', '.m4v'}
IMG = {'.jpg', '.jpeg', '.png', '.heic'}


def probe(p):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format',
                                   '-show_streams', str(p)], capture_output=True, text=True).stdout)
    tags = j['format'].get('tags', {})
    t = tags.get('com.apple.quicktime.creationdate') or tags.get('creation_time', '')
    return float(j['format'].get('duration', 0)), t


def frame_at(p, t):
    # -ss before -i: fast keyframe seek; ffmpeg auto-applies rotation
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(p), '-frames:v', '1',
                          '-vf', f'scale={TW}:-2', '-f', 'image2pipe', '-c:v', 'png', '-'],
                         capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert('RGB') if raw else None


def audio(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vn', '-f', 's16le', '-ac', '1',
                          '-ar', '16000', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu', compute_type='int8')
font = ImageFont.truetype('/home/user/capcut/fonts/PublicSans-Italic%5Bwght%5D.ttf', 18)

files = sorted(f for f in src.iterdir() if f.suffix.lower() in VID | IMG)
log, rows = [], []
for f in files:
    entry = {'file': f.name}
    if f.suffix.lower() in VID:
        dur, t = probe(f)
        entry.update(type='video', duration=round(dur, 1), created=t)
        a = audio(f)
        segs, info = model.transcribe(a, vad_filter=True, beam_size=1) if len(a) > 8000 else ([], None)
        entry['transcript'] = ' '.join(s.text.strip() for s in segs)
        thumbs = [frame_at(f, dur * (i + 0.5) / FRAMES) for i in range(FRAMES)]
    else:
        im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
        entry.update(type='photo', created=(im.getexif().get(306) or ''))
        im.thumbnail((TW, TW * 2))
        thumbs = [im]
    thumbs = [t for t in thumbs if t]
    log.append(entry)
    label = f"{f.stem}  {entry.get('duration', 'photo')}{'s' if entry['type'] == 'video' else ''}"
    rows.append((label, thumbs))
    print(label, '|', entry.get('transcript', '')[:80], flush=True)

(out / 'footage_log.json').write_text(json.dumps(log, indent=1))
with open(out / 'footage_log.md', 'w') as md:
    for e in log:
        md.write(f"- **{e['file']}** ({e['type']}, {e.get('duration', '')}s, {e.get('created', '')})"
                 f"{': ' + e['transcript'] if e.get('transcript') else ''}\n")

for s in range(0, len(rows), CLIPS_PER_SHEET):
    chunk = rows[s:s + CLIPS_PER_SHEET]
    th = max(t.height for _, ts in chunk for t in ts)
    sheet = Image.new('RGB', (TW * FRAMES + 8 * FRAMES, (th + 30) * len(chunk)), (25, 25, 25))
    d = ImageDraw.Draw(sheet)
    for r, (label, ts) in enumerate(chunk):
        y = r * (th + 30)
        d.text((6, y + 4), label, font=font, fill=(255, 226, 122))
        for i, t in enumerate(ts):
            sheet.paste(t, (i * (TW + 8), y + 28))
    sheet.save(out / f'sheet_{s // CLIPS_PER_SHEET + 1:02d}.jpg', quality=80)
print('done', len(log))
