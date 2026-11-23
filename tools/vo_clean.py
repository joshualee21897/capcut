"""Clean a voice memo using Whisper word timestamps + the audio's own energy.

- keep ranges (raw-time, in the order given) let you drop retakes and splice the best take of a line
- each word's edges are extended to where the sound really starts/ends (no clipped "s", "dy", "k" endings)
- everything between words (uh/um, breaths, gulps, dead air) is removed
- any silence left (incl. inside a word span) is capped: short mid-sentence, a bit longer at sentence ends
- denoise + presence EQ + compression + loudness normalise
Writes vo_clean.wav and words_clean.json (word timings on the NEW timeline).

usage: python3 tools/vo_clean.py raw.wav words_raw.json out_dir --keep 0:84 --keep 95:101 --keep 90.6:93 --keep 109.5:999
"""
import argparse, json, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('raw'); ap.add_argument('words'); ap.add_argument('out')
ap.add_argument('--keep', action='append', required=True)
ap.add_argument('--tempo', type=float, default=1.0)
a = ap.parse_args()

SR, HOP = 48000, 480                                    # 10 ms envelope frames
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', a.raw, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                                 capture_output=True).stdout, np.int16).astype(np.float32) / 32768


def envelope(sig):
    n = len(sig) // HOP
    hp = np.convolve(sig, [1, -0.95], 'same')            # pre-emphasis so soft "s"/"t" tails register
    return np.sqrt((hp[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-12)


env = envelope(x)
floor = np.percentile(env, 10)
fr = lambda t: int(t * SR / HOP)

all_words = json.load(open(a.words))
ranges = [tuple(map(float, k.split(':'))) for k in a.keep]
seq = []                                                 # words in output order, with their range
for r0, r1 in ranges:
    seq += [dict(w, r0=r0, r1=r1) for w in all_words if r0 <= w['s'] < r1]

# --- true word edges from energy ------------------------------------------------
for i, w in enumerate(seq):
    lo = seq[i - 1]['e'] if i and seq[i - 1]['r0'] == w['r0'] else w['r0']
    hi = seq[i + 1]['s'] if i + 1 < len(seq) and seq[i + 1]['r0'] == w['r0'] else min(w['r1'], len(x) / SR)
    peak = env[fr(w['s']):max(fr(w['e']), fr(w['s']) + 1)].max()
    thr = max(floor * 2.5, peak * 0.05)
    e, lowest, limit = fr(w['e']), env[fr(w['e'])], fr(min(w['e'] + 0.35, hi - 0.02))
    while e < limit:
        if env[e] > thr:
            if lowest < thr * 1.3 and env[e] > peak * 0.35:      # near-silence then a strong sound...
                k = e
                while k < limit and env[k] > thr:
                    k += 1
                if (k - e) * HOP / SR > 0.2:                    # ...that lasts: a new "uh", not a syllable
                    break
            lowest = min(lowest, env[e])
            e += 1
            continue
        # quiet: bridge a short closure if a SHORT burst follows (final "k", "t", "d" release)
        j = e
        while j < limit and env[j] <= thr and j - e < fr(0.15):
            j += 1
        if j < limit and env[j] > thr:
            k = j
            while k < limit and env[k] > thr:
                k += 1
            if (k - j) * HOP / SR < 0.2:
                e = k
                continue
        break
    s = fr(w['s'])
    # long quiet lead-in inside the word span (pause/breath before the word): skip it
    on = s
    while on < fr(w['e']) and env[on] < floor * 3:       # only true near-silence, never soft consonants
        on += 1
    if (on - s) * HOP / SR > 0.25:
        s = on - fr(0.06)
    else:
        while s > fr(max(w['s'] - 0.15, lo + 0.02)) and env[s - 1] > thr:
            s -= 1
    w['s'] = max(w['s'], s * HOP / SR)
    w['cs'], w['ce'] = max(s * HOP / SR - 0.03, lo), min(e * HOP / SR + 0.05, hi)

# --- splice words, inserting short pauses ---------------------------------------
fade = int(0.006 * SR)
GAP_WORD, GAP_COMMA, GAP_END = 0.05, 0.12, 0.28
out, t_new, new_words, sentence_end_at = [], 0.0, [], []
for i, w in enumerate(seq):
    seg = x[int(w['cs'] * SR):int(w['ce'] * SR)].copy()
    if len(seg) > 2 * fade:
        r = np.linspace(0, 1, fade)
        seg[:fade] *= r
        seg[-fade:] *= r[::-1]
    new_words.append(dict(w=w['w'], s=t_new + (w['s'] - w['cs']), e=t_new + (min(w['ce'], w['e'] + 0.25) - w['cs'])))
    out.append(seg)
    t_new += len(seg) / SR
    if i + 1 < len(seq):
        end = w['w'].endswith(('.', '?', '!'))
        pause = GAP_END if end else GAP_COMMA if w['w'].endswith(',') else GAP_WORD
        if seq[i + 1]['r0'] == w['r0']:
            pause = min(pause, max(seq[i + 1]['cs'] - w['ce'], 0.0)) if not end else pause
        out.append(np.zeros(int(pause * SR), np.float32))
        if end:
            sentence_end_at.append(t_new)
        t_new += pause
y = np.concatenate(out)

# --- cap any remaining silence (e.g. a pause inside a word span) ------------------
ey = envelope(y)
quiet = ey < max(np.percentile(ey, 10) * 2.5, floor * 2.5)
keep_mask = np.ones(len(y), bool)
removed = []                                             # (new_time_of_cut, seconds_removed)
i = 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        t0, t1 = i * HOP / SR, j * HOP / SR
        cap = 0.30 if any(abs(t0 - se) < 0.25 for se in sentence_end_at) else 0.14
        if t1 - t0 > cap:
            c0, c1 = t0 + cap / 2, t1 - cap / 2
            keep_mask[int(c0 * SR):int(c1 * SR)] = False
            removed.append((c0, c1 - c0))
        i = j
    else:
        i += 1
y = y[keep_mask]
shift = lambda t: t - sum(d for c, d in removed if c < t)
for w in new_words:
    w['s'], w['e'] = round(shift(w['s']), 3), round(shift(w['e']), 3)
print(f'kept {len(new_words)} words, raw {len(x) / SR:.1f}s -> {len(y) / SR:.1f}s, '
      f'{len(new_words) / (len(y) / SR):.2f} words/s, capped {len(removed)} silences')

tmp = f'{a.out}/vo_cut.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', tmp],
               input=y.tobytes(), check=True)
chain = ','.join(['highpass=f=85', 'lowpass=f=15000', 'afftdn=nr=14:nf=-38:tn=1',
                  'equalizer=f=220:t=q:w=1.2:g=-2', 'equalizer=f=4200:t=q:w=1.0:g=3', 'equalizer=f=11000:t=q:w=0.8:g=1.5',
                  'deesser=i=0.3', 'acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3',
                  f'atempo={a.tempo}', 'loudnorm=I=-16:TP=-1.5:LRA=7'])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', chain, '-ar', '48000', '-ac', '2',
                f'{a.out}/vo_clean.wav'], check=True)
for w in new_words:
    w['s'], w['e'] = round(w['s'] / a.tempo, 3), round(w['e'] / a.tempo, 3)
json.dump(dict(tempo=a.tempo, words=new_words), open(f'{a.out}/words_clean.json', 'w'), indent=0)
print('done', f'{len(y) / SR / a.tempo:.1f}s')
