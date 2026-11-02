#!/usr/bin/env python3
# Blueprint November cut of Woman Ad 3. Stage 1: caption each generated clip (bounded inputs).
# Stage 2: concat body + clips + end card, mix speech + music bed.
import subprocess, sys, json
W = '/vercel/w'
FMT = sys.argv[1]
FF = f'{W}/bin/ffmpeg'
CUT = 45.083
LENS = {1: 13.0, 2: 11.4, 3: 14.7}
H = {'9x16': 1920, '1x1': 1080}[FMT]
CAP_Y = {'9x16': 1290, '1x1': 780}[FMT]
CROP = "crop=1080:1080:0:330," if FMT == '1x1' else ""
META = [m for m in json.load(open(f'{W}/caps/caps.json')) if m['fmt'] == FMT]
cut = {2: [(0.10, 1.9, f'{W}/cgm_{FMT}.mp4')], 3: [(0.10, 1.7, f'{W}/julie_{FMT}.mp4'), (1.80, 1.95, f'{W}/zoom_{FMT}.mp4')]}
def hidden(i, m):
    return any(m['s'] < st + ln and m['e'] > st for (st, ln, f) in cut.get(i, []))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('FAIL', r.stderr[-1500:]); sys.exit(1)

# Stage 1
for i in (1, 2, 3):
    L = LENS[i]
    inputs = ['-i', f'{W}/gen/h{i}.mp4']
    fc = [f"[0:v]trim=0:{L},setpts=PTS-STARTPTS,{CROP}scale=1080:{H},fps=24,format=yuv420p[b0]"]
    n = 1; cur = 'b0'
    for (st, ln, f) in cut.get(i, []):
        idx = inputs.count('-i')
        inputs += ['-i', f]
        fc.append(f"[{idx}:v]trim=0:{ln},setpts=PTS-STARTPTS+{st}/TB,scale=1080:{H},fps=24,format=yuv420p[k{n}]")
        fc.append(f"[{cur}][k{n}]overlay=eof_action=pass[b{n}]"); cur = f'b{n}'; n += 1
    for m in META:
        if m['clip'] != i or hidden(i, m): continue
        idx = inputs.count('-i')
        inputs += ['-loop', '1', '-t', f"{m['e']+0.05}", '-i', f"{W}/caps/cap_{FMT}_{m['i']:02d}.png"]
        fc.append(f"[{cur}][{idx}:v]overlay=x=(W-w)/2:y={CAP_Y}:eof_action=pass:enable='between(t,{m['s']},{m['e']})'[b{n}]"); cur = f'b{n}'; n += 1
    cmd = [FF, '-loglevel', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-an', '-r', '24', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', f'{W}/c{i}_{FMT}.mp4']
    run(cmd)
    print('clip', i, 'ok')

# Stage 2
total = LENS[1] + LENS[2] + LENS[3] + 3.0
inputs = ['-i', f'{W}/src/w3_{FMT}.mp4', '-i', f'{W}/c1_{FMT}.mp4', '-i', f'{W}/c2_{FMT}.mp4', '-i', f'{W}/c3_{FMT}.mp4', '-i', f'{W}/end_{FMT}.mp4', '-i', f'{W}/music_loop.wav', '-i', f'{W}/gen/h1.mp4', '-i', f'{W}/gen/h2.mp4', '-i', f'{W}/gen/h3.mp4']
fc = [
 f"[0:v]trim=0:{CUT},setpts=PTS-STARTPTS,fps=24,format=yuv420p[v0]",
 f"[0:a]atrim=0:{CUT},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a0]",
 f"[4:v]trim=0:3.0,setpts=PTS-STARTPTS,fps=24,format=yuv420p,fade=t=out:st=2.5:d=0.5[v4]",
 "[v0][1:v][2:v][3:v][v4]concat=n=5:v=1:a=0[v]",
 f"[6:a]atrim=0:{LENS[1]},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=-4.5dB[s1]",
 f"[7:a]atrim=0:{LENS[2]},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=-4.5dB[s2]",
 f"[8:a]atrim=0:{LENS[3]},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=-4.5dB[s3]",
 "anullsrc=r=48000:cl=stereo,atrim=0:3.0[sil]",
 "[s1][s2][s3][sil]concat=n=4:v=0:a=1[spk]",
 f"[5:a]atrim=0:{total},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=0.28,afade=t=in:st=0:d=0.6,afade=t=out:st={total-1.2}:d=1.2[mus]",
 "[spk][mus]amix=inputs=2:duration=first:normalize=0[off]",
 "[a0][off]concat=n=2:v=0:a=1[a]",
]
cmd = [FF, '-loglevel', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]', '-r', '24', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', f'{W}/out/W3_Blueprint_Nov_{FMT}.mp4']
run(cmd)
print('final', FMT, 'ok')
