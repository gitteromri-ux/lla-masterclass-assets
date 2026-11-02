import subprocess, sys, json, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
S=os.path.dirname(os.path.abspath(__file__)); U='/home/user/gitteromri-ux/lla-julie-ugc-ads'; REPO='/home/user/lla-masterclass-assets/ugc-bp-nov'
FMT=sys.argv[1]; H={'9x16':1920,'1x1':1080}[FMT]; OFF=0 if FMT=='9x16' else 409; CAP_Y={'9x16':1290,'1x1':780}[FMT]
W3=f'{U}/claude-fixes/final/ad5-woman46-h3__{FMT}__75.mp4'; BP=f'{U}/blueprint/w46__{FMT}.mp4'
BG=f'{U}/hookbuild/'+('cardbg9.png' if FMT=='9x16' else 'cardbg1b.png'); EX=f'{U}/hookbuild/Exhilarate.mp3'
FREG=f'{REPO}/fonts/PlayfairDisplay-Regular.ttf'; FIT=f'{REPO}/fonts/PlayfairDisplay-Italic.ttf'
WHITE=(250,248,245); BLUE=(158,190,235); RULE=(69,81,113)
CROP="crop=1080:1080:0:330," if FMT=='1x1' else ""
HOOK_END=21.8; BP_IN=22.65; BP_OUT=51.917; LENS={1:13.0,2:11.4,3:14.7}; SR=48000
META=[m for m in json.load(open(f'{REPO}/caps/caps.json')) if m['fmt']==FMT]
for d in ('cards','out','seg'): os.makedirs(f'{S}/{d}',exist_ok=True)
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print('FAIL',' '.join(cmd)[:400],r.stderr[-1500:]); sys.exit(1)
def size_for(path,text,width,start):
    s=start
    while s>30 and ImageFont.truetype(path,s).getlength(text)>width: s-=2
    return s
def card_text(name,big,sub,small):
    im=Image.new('RGBA',(1080,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    rows=[(big,FREG,min(177,size_for(FREG,big,940,177)),WHITE,790-OFF)]
    if sub: rows.append((sub,FIT,min(80,size_for(FIT,sub,940,80)),BLUE,1040-OFF))
    if small: rows.append((small,FIT,min(56,size_for(FIT,small,900,56)),BLUE,1140-OFF))
    for t,fp,sz,c,y in rows:
        f=ImageFont.truetype(fp,sz); b=f.getbbox(t); w=b[2]-b[0]; d.text(((1080-w)//2-b[0],y-b[1]),t,font=f,fill=c+(255,))
    y=1262-OFF; d.rectangle([470,y,610,y+2],fill=RULE+(255,))
    p=f'{S}/cards/{name}_{FMT}.png'; im.save(p); return p
def card_seg(name,ln):
    txt=f'{S}/cards/{name}_{FMT}.png'; out=f'{S}/seg/{name}_{FMT}.mp4'
    run(['ffmpeg','-loglevel','error','-y','-loop','1','-t',str(ln),'-i',BG,'-loop','1','-t',str(ln),'-i',txt,'-filter_complex',
         f"[1:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1,fade=t=out:st={ln-0.125}:d=0.125:alpha=1[t];[0:v]format=yuv420p[b];[b][t]overlay=format=auto,format=yuv420p,fps=24",
         '-r','24','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',out]); return out
C={}
C['bp']=card_text('bp','The Longevity Blueprint.','18 weeks. Live on Zoom.',None)
C['k1']=card_text('k1','The Longevity Blueprint.','Your own protocol. 18 weeks, live.',None)
C['k2']=card_text('k2','Over 50% off.','First month $79. 14-day refund.',None)
C['k4']=card_text('k4','VIP masterclass. Free.','Julie Gibson Clark. November 14.',None)
C['k5']=card_text('k5','Enroll now.','longevitylifeacademy.com',None)
KL=[('k1',2.75),('k2',2.5),('k4',2.75),('k5',2.5)]
segs=[card_seg(n,l) for n,l in KL]
def cut_src(name,a,b):
    p=f'{S}/{name}_{FMT}.mp4'
    if not os.path.exists(p): run(['ffmpeg','-loglevel','error','-y','-ss',str(a),'-to',str(b),'-i',BP,'-an','-r','24','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',p])
    return p
cgm=cut_src('cgm',58.5,60.4); zoom=cut_src('zoom',51.917,53.9); jt=cut_src('jt',33.3,35.4); end=cut_src('end',77.958,81.5)
OV={1:[],2:[(0.10,1.9,cgm),(8.1,3.2,zoom)],3:[(0.10,2.1,jt)]}
def hidden(i,m): return any(m['s']<st+ln+0.3 and m['e']>st-0.3 for st,ln,f in OV[i])
for i in (1,2,3):
    if os.path.exists(f'{S}/c{i}_{FMT}.mov') and os.path.getsize(f'{S}/c{i}_{FMT}.mov')>1e6: print('clip',i,'cached'); continue
    L=LENS[i]; inputs=['-i',f'{S}/gen/h{i}a.mp4','-i',f'{S}/gen/h{i}b.mp4','-i',f'{S}/gen/h{i}c.mp4']
    fc=["[0:v]trim=0:5,setpts=PTS-STARTPTS[a];[1:v]trim=0:5,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[cat]",
        f"[cat]trim=0:{L},setpts=PTS-STARTPTS,{CROP}scale=1080:{H},fps=24,format=yuv420p[b0]",
        "[0:a]atrim=0:5,asetpts=PTS-STARTPTS[x];[1:a]atrim=0:5,asetpts=PTS-STARTPTS[y];[2:a]asetpts=PTS-STARTPTS[z];[x][y][z]concat=n=3:v=0:a=1[acat]",
        f"[acat]atrim=0:{L},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[ao]"]
    n=1; cur='b0'
    for st,ln,f in OV[i]:
        idx=inputs.count('-i'); inputs+=['-i',f]
        fc.append(f"[{idx}:v]trim=0:{ln},setpts=PTS-STARTPTS+{st}/TB,scale=1080:{H},fps=24,format=yuv420p[k{n}]"); fc.append(f"[{cur}][k{n}]overlay=eof_action=pass[b{n}]"); cur=f'b{n}'; n+=1
    for m in META:
        if m['clip']!=i or hidden(i,m): continue
        idx=inputs.count('-i'); inputs+=['-loop','1','-t',f"{m['e']+0.05}",'-i',f"{REPO}/caps/cap_{FMT}_{m['i']:02d}.png"]
        fc.append(f"[{cur}][{idx}:v]overlay=x=(W-w)/2:y={CAP_Y}:eof_action=pass:enable='between(t,{m['s']},{m['e']})'[b{n}]"); cur=f'b{n}'; n+=1
    run(['ffmpeg','-loglevel','error','-y']+inputs+['-filter_complex',';'.join(fc),'-map',f'[{cur}]','-map','[ao]','-r','24','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-c:a','pcm_s16le',f'{S}/c{i}_{FMT}.mov'])
    print('clip',i,'ok',flush=True)
# ---- audio: voice level match + music bed with the original gain recipe
def rd(path,ss,dur):
    r=subprocess.run(['ffmpeg','-v','error','-ss',f'{ss:.4f}','-t',f'{dur:.4f}','-i',path,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    x=np.frombuffer(r,np.float32).reshape(-1,2).copy(); N=int(round(dur*SR)); return np.vstack([x,np.zeros((max(0,N-len(x)),2),np.float32)])[:N]
def act(a):
    m=a.mean(1); m=m[:len(m)//480*480]; e=np.sqrt((m.reshape(-1,480)**2).mean(1)); thr=np.percentile(e,60); return np.sqrt((e[e>=thr]**2).mean())
ref=act(rd(BP,36.0,14.0))
speech=[]
for i in (1,2,3):
    v=rd(f'{S}/c{i}_{FMT}.mov',0,LENS[i]); g=float(np.clip(ref/act(v),0.35,1.4)); v*=g; f=int(0.03*SR); v[:f]*=np.linspace(0,1,f)[:,None]; v[-f:]*=np.linspace(1,0,f)[:,None]; speech.append(v); print('voice gain',i,round(g,3))
SP=sum(LENS.values()); KT=sum(l for _,l in KL); ENDL=3.5; T=SP+KT+ENDL; N=int(T*SR)
voice=np.vstack(speech); voice=np.vstack([voice,np.zeros((N-len(voice),2),np.float32)])
gg=np.full(N,0.0665,np.float32); a=int(SP*SR); r=int(0.5*SR); gg[a:]=0.30; gg[a:a+r]=np.linspace(0.0665,0.30,r); gg[:r]*=np.linspace(0,1,r)
gg=np.convolve(gg,np.ones(4800)/4800,mode='same').astype(np.float32); f=int(0.6*SR); gg[-f:]*=np.linspace(1,0,f)
music=rd(EX,61.0,T)*gg[:,None]
mix=np.clip(voice+music,-1,1)
import wave
with wave.open(f'{S}/offer_{FMT}.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
# ---- stage 2
inputs=['-i',W3,'-i',BP,'-loop','1','-t','1.1','-i',BG,'-loop','1','-t','1.1','-i',C['bp'],'-i',f'{S}/c1_{FMT}.mov','-i',f'{S}/c2_{FMT}.mov','-i',f'{S}/c3_{FMT}.mov']+sum([['-i',s] for s in segs],[])+['-i',end,'-i',f'{S}/offer_{FMT}.wav']
ns=len(segs); ei=7+ns; ai=8+ns
fc=[f"[0:v]trim=0:{HOOK_END},setpts=PTS-STARTPTS,fps=24,format=yuv420p[v0]",
    f"[0:a]atrim=0:{HOOK_END},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a0]",
    f"[1:v]trim={BP_IN}:{BP_OUT},setpts=PTS-STARTPTS,fps=24,format=yuv420p[bpv]",
    f"[2:v]fps=24,format=rgba,fade=t=in:st=0:d=0.12:alpha=1,fade=t=out:st=0.98:d=0.12:alpha=1,setpts=PTS-STARTPTS+{24.55-BP_IN}/TB[bg1]",
    f"[3:v]fps=24,format=rgba,fade=t=in:st=0.05:d=0.25:alpha=1,fade=t=out:st=0.95:d=0.12:alpha=1,setpts=PTS-STARTPTS+{24.55-BP_IN}/TB[tx1]",
    "[bpv][bg1]overlay=eof_action=pass:format=auto[p1];[p1][tx1]overlay=eof_action=pass:format=auto,format=yuv420p[v1]",
    f"[1:a]atrim={BP_IN}:{BP_OUT},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,afade=t=out:st={BP_OUT-BP_IN-0.25}:d=0.25[a1]",
    f"[{ei}:v]trim=0:{ENDL},setpts=PTS-STARTPTS,fps=24,format=yuv420p,fade=t=out:st={ENDL-0.5}:d=0.5[ve]",
    "[v0][v1][4:v][5:v][6:v]"+''.join(f'[{7+k}:v]' for k in range(ns))+f"[ve]concat=n={6+ns}:v=1:a=0[v]",
    f"[{ai}:a]aformat=sample_rates=48000:channel_layouts=stereo[a2]",
    "[a0][a1][a2]concat=n=3:v=0:a=1[a]"]
out=f'{S}/out/W3_Blueprint_Nov_{FMT}.mp4'
run(['ffmpeg','-loglevel','error','-y']+inputs+['-filter_complex',';'.join(fc),'-map','[v]','-map','[a]','-r','24','-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',out])
print('final',FMT,out,flush=True)
