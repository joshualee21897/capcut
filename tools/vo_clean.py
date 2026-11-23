"""Clean a voice memo using Whisper word timestamps.

- keeps only the spoken words (drops 'uh/um', breaths, gulps and dead air that sit between words)
- drops unwanted retakes (time ranges)
- tightens pauses (word gap / comma / sentence end)
- denoise + presence EQ + compression + loudness normalise
- optional speed-up (atempo, pitch preserved)
Writes vo_clean.wav and words_clean.json (word timings on the NEW timeline).

usage: python3 tools/vo_clean.py raw.wav words_raw.json out_dir --drop 84:93 --drop 106:109 [--tempo auto|1.0|1.1]
"""
import argparse, json, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('raw'); ap.add_argument('words'); ap.add_argument('out')
ap.add_argument('--drop', action='append', default=[])
ap.add_argument('--tempo', default='auto')
a = ap.parse_args()

SR = 48000
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', a.raw, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                                 capture_output=True).stdout, np.int16).astype(np.float32) / 32768
words = json.load(open(a.words))
drops = [tuple(map(float, d.split(':'))) for d in a.drop]
words = [w for w in words if not any(d0 <= w['s'] < d1 for d0, d1 in drops)]

PRE, POST = 0.05, 0.07
GAP_WORD, GAP_COMMA, GAP_END = 0.06, 0.14, 0.30
fade = int(0.006 * SR)

out, new_words, t_new = [], [], 0.0
for i, w in enumerate(words):
    prev_end = words[i - 1]['e'] if i else 0
    nxt_start = words[i + 1]['s'] if i + 1 < len(words) else len(x) / SR
    s = max(w['s'] - PRE, (prev_end + w['s']) / 2 if i else 0)
    e = min(w['e'] + POST, (w['e'] + nxt_start) / 2)
    seg = x[int(s * SR):int(e * SR)].copy()
    if len(seg) > 2 * fade:
        ramp = np.linspace(0, 1, fade)
        seg[:fade] *= ramp
        seg[-fade:] *= ramp[::-1]
    new_words.append(dict(w=w['w'], s=round(t_new + (w['s'] - s), 3), e=round(t_new + (w['e'] - s), 3)))
    out.append(seg)
    t_new += len(seg) / SR
    if i + 1 < len(words):
        gap = words[i + 1]['s'] - w['e']
        target = GAP_END if w['w'].endswith(('.', '?', '!')) else GAP_COMMA if w['w'].endswith(',') else GAP_WORD
        pause = min(gap, target) - (POST + PRE) if gap > target else 0
        if pause > 0:
            out.append(np.zeros(int(pause * SR), np.float32))
            t_new += pause
y = np.concatenate(out)
spoken = sum(w['e'] - w['s'] for w in new_words)
rate = len(new_words) / (len(y) / SR)
tempo = (1.1 if rate < 2.9 else 1.0) if a.tempo == 'auto' else float(a.tempo)
print(f'kept {len(new_words)} words, {len(x) / SR:.1f}s -> {len(y) / SR:.1f}s, {rate:.2f} words/s, tempo {tempo}')

tmp = f'{a.out}/vo_cut.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', tmp],
               input=y.tobytes(), check=True)
chain = ','.join([
    'highpass=f=85', 'lowpass=f=15000',
    'afftdn=nr=14:nf=-38:tn=1',                     # broadband noise reduction (tracks the noise floor)
    'equalizer=f=220:t=q:w=1.2:g=-2',               # less boom/mud
    'equalizer=f=4200:t=q:w=1.0:g=3',               # presence / crispness
    'equalizer=f=11000:t=q:w=0.8:g=1.5',            # air
    'deesser=i=0.35',
    'acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3',
    f'atempo={tempo}',
    'loudnorm=I=-16:TP=-1.5:LRA=7',
])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', chain, '-ar', '48000', '-ac', '2',
                f'{a.out}/vo_clean.wav'], check=True)
for w in new_words:
    w['s'], w['e'] = round(w['s'] / tempo, 3), round(w['e'] / tempo, 3)
json.dump(dict(tempo=tempo, words=new_words), open(f'{a.out}/words_clean.json', 'w'), indent=0)
print('done', f'{len(y) / SR / tempo:.1f}s')
