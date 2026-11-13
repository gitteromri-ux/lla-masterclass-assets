#!/usr/bin/env bash
# Latest cut: AUTOMATIC card removed (Ken Burns on approved Julie photo covers AirPod shots 53.683-58.733),
# Enroll + separate VIP cards removed, date card carries "90 Min VIP Masterclass + Live Q&A Included".
set -euo pipefail
cd "$(dirname "$0")"
python build.py
python urgent-fixes.py
ffmpeg -v error -y \
 -i source/masterclass-source.mp4 \
 -i scene-1.mp4 \
 -loop 1 -framerate 30 -i card-2.png \
 -loop 1 -framerate 30 -i card-3.png \
 -loop 1 -framerate 30 -i press-fixed.png \
 -loop 1 -framerate 30 -t 5.1 -i source/julie/julie-lifestyle.jpg \
 -loop 1 -framerate 30 -i hold-335.png \
 -loop 1 -framerate 30 -i hold-335y.png \
 -loop 1 -framerate 30 -i hold-100.png \
 -filter_complex_threads 2 -filter_complex \
"[5:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,zoompan=z='1.0+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih*0.42-(ih/zoom*0.42)':d=1:s=1920x1080:fps=30,trim=0:5.05,format=yuva420p,setpts=PTS-STARTPTS+53.683333/TB[kb];\
[0:v]trim=0:62.8,setpts=PTS-STARTPTS[vb];[vb][4:v]overlay=enable='between(t,9.666667,13.033333)'[vp1];[vp1][6:v]overlay=enable='between(t,18.15,19.12)'[vp2];[vp2][7:v]overlay=enable='between(t,40.15,41.12)'[vp3];[vp3][8:v]overlay=enable='between(t,45.75,46.52)'[vp];\
[vp][kb]overlay=eof_action=pass:enable='between(t,53.683333,58.733333)',trim=0:62.8,setsar=1[v0];\
[1:v]trim=0:5.2,setpts=PTS-STARTPTS,setsar=1[c1];\
[2:v]trim=0:4.5,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[c2];\
[3:v]trim=0:8.9,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[c3];\
[c2][c3]xfade=transition=fade:duration=0.4:offset=4.1[c23];\
[v0][c1][c23]concat=n=3:v=1:a=0,trim=0:81[v];\
[0:a]atrim=0:62.8,asetpts=PTS-STARTPTS[body];\
[0:a]atrim=90:92.366667,asetpts=PTS-STARTPTS,volume=0.78[lead];\
[0:a]atrim=113.5:130.5,asetpts=PTS-STARTPTS[voice];\
[0:a]atrim=130.5:136.633333,asetpts=PTS-STARTPTS,aecho=0.8:0.75:700|1400|2200:0.4|0.25|0.14,apad,atrim=0:6.133333[tail];\
[voice][tail]concat=n=2:v=0:a=1[end];[lead][end]acrossfade=d=0.2:c1=qsin:c2=qsin[bed];\
[body][bed]acrossfade=d=0.1:c1=qsin:c2=qsin,alimiter=limit=0.89:level=false,apad,atrim=0:81,afade=t=out:st=79.6:d=1.4[a]" \
 -map "[v]" -map "[a]" -t 81 -r 30 -c:v libx264 -preset veryfast -crf 18 -threads 8 \
 -c:a aac -b:a 320k -ar 48000 -pix_fmt yuv420p -movflags +faststart \
 Julie-Masterclass-Nov14-Launch-Final.mp4
