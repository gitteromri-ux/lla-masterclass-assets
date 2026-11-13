#!/usr/bin/env bash
# 83.2s master: navy AUTOMATIC card synced to VO, resolving final chord, audio polish, text-dip between Cards 2-3.
set -euo pipefail
cd "$(dirname "$0")"
python build.py
python auto-anim.py
ffmpeg -v error -y -loop 1 -framerate 30 -t 0.7167 -i card-blank.png -framerate 30 -i auto-frames/f%03d.png -loop 1 -framerate 30 -t 2.8 -i card-automatic.png -filter_complex "[0][1][2]concat=n=3:v=1:a=0,trim=0:5.05,format=yuv420p" -c:v libx264 -crf 12 -preset veryfast -r 30 auto-clip.mp4
ffmpeg -v error -y \
 -i source/masterclass-source.mp4 \
 -i scene-1.mp4 \
 -loop 1 -framerate 30 -i card-2.png \
 -loop 1 -framerate 30 -i card-3.png \
 -loop 1 -framerate 30 -i press-fixed.png \
 -loop 1 -framerate 30 -i card-blank.png \
 -loop 1 -framerate 30 -i hold-335.png \
 -loop 1 -framerate 30 -i hold-335y.png \
 -loop 1 -framerate 30 -i hold-100.png \
 -i auto-clip.mp4 \
 -filter_complex_threads 2 -filter_complex \
"[5:v]copy[bk2];\
[9:v]setpts=PTS-STARTPTS+53.683333/TB,setsar=1[auto];\
[4:v]format=yuva420p,fade=t=out:st=13.033:d=0.35:alpha=1[pf];\
[0:v]trim=0:62.8,setpts=PTS-STARTPTS[vb];[vb][pf]overlay=enable='between(t,9.666667,13.4)'[vp1];[vp1][6:v]overlay=enable='between(t,18.15,19.12)'[vp2];[vp2][7:v]overlay=enable='between(t,40.15,41.12)'[vp3];[vp3][8:v]overlay=enable='between(t,45.75,46.52)'[vp];\
[vp][auto]overlay=eof_action=pass:enable='between(t,53.683333,58.733333)',trim=0:62.8,setsar=1[v0];\
[1:v]trim=0:5.2,setpts=PTS-STARTPTS,setsar=1[c1];\
[2:v]trim=0:4.3,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[c2];\
[bk2]trim=0:0.4,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[bl];\
[3:v]trim=0:10.9,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[c3];\
[c2][bl]xfade=transition=fade:duration=0.2:offset=4.1[c2b];[c2b][c3]xfade=transition=fade:duration=0.2:offset=4.3[c23];\
[v0][c1][c23]concat=n=3:v=1:a=0,trim=0:83.2[v];\
[0:a]atrim=0:62.8,asetpts=PTS-STARTPTS,volume='if(lt(t,2.6),2,if(lt(t,3.0),2-(t-2.6)*2.5,1))':eval=frame[body];\
[0:a]atrim=90:92.366667,asetpts=PTS-STARTPTS,volume=1.2[lead];\
[0:a]atrim=113.5:129.5,asetpts=PTS-STARTPTS[voice];\
[0:a]atrim=132.9:135.7,asetpts=PTS-STARTPTS[res];\
[voice][res]acrossfade=d=0.4:c1=qsin:c2=qsin[end];[lead][end]acrossfade=d=0.25:c1=qsin:c2=qsin[bed];\
[body][bed]acrossfade=d=0.1:c1=qsin:c2=qsin,alimiter=limit=0.89:level=false,apad,atrim=0:83.2,afade=t=out:st=82.4:d=0.8[a]" \
 -map "[v]" -map "[a]" -t 83.2 -r 30 -c:v libx264 -preset veryfast -crf 18 -threads 8 \
 -c:a aac -b:a 320k -ar 48000 -pix_fmt yuv420p -movflags +faststart \
 Julie-Masterclass-Nov14-Launch-Final.mp4
