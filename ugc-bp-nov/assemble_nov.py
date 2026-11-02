#!/usr/bin/env python3
# Assemble the Blueprint November cut of Woman Ad 3 in the sandbox.
# Timeline: W3 body [0,45.083) -> h1 -> h2 (CGM cutaway) -> h3 (Zoom cutaway) -> end card.
import subprocess, os, sys
W = '/vercel/w'
FMT = sys.argv[1]            # 9x16 or 1x1
FF = f'{W}/bin/ffmpeg'
REG = f'{W}/fonts/PlayfairDisplay-Regular.ttf'
IT = f'{W}/fonts/PlayfairDisplay-Italic.ttf'
CUT = 45.083
# trimmed clip lengths (speech end + small tail)
L1, L2, L3 = 13.0, 11.4, 14.7
H = {'9x16': 1920, '1x1': 1080}[FMT]
CAP_Y = {'9x16': 1290, '1x1': 780}[FMT]
FS = {'9x16': 74, '1x1': 60}[FMT]
CROP = "crop=1080:1080:0:330," if FMT == '1x1' else ""

# captions: (clip, start, end, text, italic_blue)
caps = [
 (1, 0.05, 1.25, "Honestly,", 0), (1, 1.25, 2.55, "the best longevity offer", 1), (1, 2.55, 4.2, "I've ever seen.", 0),
 (1, 4.3, 5.9, "Top instructors.", 0), (1, 6.4, 8.8, "Your own longevity protocol.", 1), (1, 8.8, 10.5, "built on your numbers.", 0), (1, 10.5, 12.9, "In only 18 weeks.", 1),
 (2, 0.05, 1.7, "They ship a CGM to your house.", 0), (2, 1.85, 2.65, "Free.", 1), (2, 2.65, 3.9, "Only in November:", 0), (2, 3.9, 6.1, "full VIP access.", 1), (2, 6.15, 7.7, "Free. Yes, free.", 1), (2, 8.1, 10.0, "to the longevity masterclass", 0), (2, 10.0, 11.3, "event of the year.", 1),
 (3, 0.05, 2.2, "with the world's #2 slowest ager,", 0), (3, 2.25, 3.7, "Julie Gibson Clark.", 1), (3, 3.75, 5.5, "This November 14th.", 1), (3, 5.6, 7.0, "Over 50% off", 1), (3, 7.0, 8.1, "your first month.", 0), (3, 8.15, 9.7, "Try it for $79.", 1), (3, 9.8, 12.4, "14-day money-back guarantee.", 0), (3, 12.6, 13.75, "Sign up now.", 0), (3, 13.8, 14.7, "I'm in.", 1),
]

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "\\%").replace("#", "\\#")

import json
META = [m for m in json.load(open(f'{W}/caps/caps.json')) if m['fmt'] == FMT]
CAPIN = {}  # caption index -> ffmpeg input index

# cutaways: (clip, start, length, file)
cut = {2: [(0.10, 2.25, f'{W}/cgm_{FMT}.mp4')], 3: [(2.25, 2.29, f'{W}/zoom_{FMT}.mp4')]}

inputs = [f'{W}/src/w3_{FMT}.mp4', f'{W}/gen/h1.mp4', f'{W}/gen/h2.mp4', f'{W}/gen/h3.mp4', f'{W}/end_{FMT}.mp4', f'{W}/music_loop.wav', f'{W}/cgm_{FMT}.mp4', f'{W}/zoom_{FMT}.mp4']
for m in META:
    CAPIN[m['i']] = len(inputs); inputs.append(f"{W}/caps/cap_{FMT}_{m['i']:02d}.png")
fc = []
fc.append(f"[0:v]trim=0:{CUT},setpts=PTS-STARTPTS,format=yuv420p[v0]")
fc.append(f"[0:a]atrim=0:{CUT},asetpts=PTS-STARTPTS[a0]")
lens = {1: L1, 2: L2, 3: L3}
for i in (1, 2, 3):
    chain = f"[{i}:v]trim=0:{lens[i]},setpts=PTS-STARTPTS,{CROP}scale=1080:{H},fps=24,format=yuv420p"
    if i in cut:
        # overlay cutaway
        for k, (st, ln, f) in enumerate(cut[i]):
            idx = 6 if i == 2 else 7
            fc.append(f"[{idx}:v]trim=0:{ln},setpts=PTS-STARTPTS+{st}/TB,scale=1080:{H},fps=24,format=yuv420p[c{i}]")
            chain += f"[p{i}];[p{i}][c{i}]overlay=eof_action=pass:enable='between(t,{st},{st+ln})'"
    n = 0
    for m in META:
        if m['clip'] != i: continue
        idx = CAPIN[m['i']]
        chain += f"[q{i}_{n}];[q{i}_{n}][{idx}:v]overlay=x=(W-w)/2:y={CAP_Y}:enable='between(t,{m['s']},{m['e']})'"
        n += 1
    chain += f"[v{i}]"
    fc.append(chain)
    fc.append(f"[{i}:a]atrim=0:{lens[i]},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=-4.5dB[s{i}]")
fc.append(f"[4:v]trim=0:3.0,setpts=PTS-STARTPTS,fps=24,format=yuv420p,fade=t=out:st=2.5:d=0.5[v4]")
fc.append(f"[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0[v]")
# speech track for offer section + silence for end card
fc.append(f"[s1][s2][s3]concat=n=3:v=0:a=1[sp]")
fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:3.0[sil]")
fc.append(f"[sp][sil]concat=n=2:v=0:a=1[spk]")
total = L1 + L2 + L3 + 3.0
fc.append(f"[5:a]atrim=0:{total},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=0.28,afade=t=in:st=0:d=0.6,afade=t=out:st={total-1.2}:d=1.2[mus]")
fc.append(f"[spk][mus]amix=inputs=2:duration=first:normalize=0[off]")
fc.append(f"[a0][off]concat=n=2:v=0:a=1[a]")
cmd = [FF, '-loglevel', 'error', '-y']
for k, f in enumerate(inputs):
    if f.endswith('.png'): cmd += ['-loop', '1']
    cmd += ['-i', f]
cmd += ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]', '-r', '24', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', f'{W}/out/W3_Blueprint_Nov_{FMT}.mp4']
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.returncode, r.stderr[-2000:])
