import subprocess, sys, json, os
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-user-lla-masterclass-assets/1157ef48-d484-5238-a277-e1ca7493a270/scratchpad/nov'
U='/home/user/gitteromri-ux/lla-julie-ugc-ads'
REPO='/home/user/lla-masterclass-assets/ugc-bp-nov'
FMT=sys.argv[1]
H={'9x16':1920,'1x1':1080}[FMT]; CAP_Y={'9x16':1290,'1x1':780}[FMT]
W3=f'{U}/claude-fixes/final/ad5-woman46-h3__{FMT}__75.mp4'
BP=f'{U}/blueprint/w46__{FMT}.mp4'
BG=f'{U}/hookbuild/'+('cardbg9.png' if FMT=='9x16' else 'cardbg1b.png')
FREG=f'{REPO}/fonts/PlayfairDisplay-Regular.ttf'; FIT=f'{REPO}/fonts/PlayfairDisplay-Italic.ttf'
WHITE=(250,248,245); BLUE=(158,190,235)
CROP="crop=1080:1080:0:330," if FMT=='1x1' else ""
HOOK_END=21.8; BP_IN=22.65; BP_OUT=51.917
LENS={1:13.0,2:11.4,3:14.7}
META=[m for m in json.load(open(f'{REPO}/caps/caps.json')) if m['fmt']==FMT]
os.makedirs(f'{S}/cards',exist_ok=True); os.makedirs(f'{S}/out',exist_ok=True)

def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print('FAIL',' '.join(cmd)[:300],r.stderr[-1500:]); sys.exit(1)

def fit(path,text,maxw,start):
    s=start
    while s>30:
        f=ImageFont.truetype(path,s)
        if f.getlength(text)<=maxw: return f
        s-=2
    return ImageFont.truetype(path,30)

def wrap2(path,text,maxw,size):
    f=ImageFont.truetype(path,size)
    if f.getlength(text)<=maxw: return [text],f
    ws=text.split(); best=None
    for k in range(1,len(ws)):
        a,b=' '.join(ws[:k]),' '.join(ws[k:])
        w=max(f.getlength(a),f.getlength(b))
        if w<=maxw and (best is None or w<best[0]): best=(w,a,b)
    if best: return [best[1],best[2]],f
    return None,f
def card(name,l1,l2=None):
    im=Image.open(BG).convert('RGB'); d=ImageDraw.Draw(im); Wd,Hd=im.size
    big={'9x16':104,'1x1':80}[FMT]; small={'9x16':74,'1x1':56}[FMT]
    s=big
    while True:
        L1,f1=wrap2(FREG,l1,960,s)
        if L1: break
        s-=4
    lines=[(t,f1,WHITE) for t in L1]
    if l2:
        s2=small
        while True:
            L2,f2=wrap2(FIT,l2,900,s2)
            if L2: break
            s2-=4
        lines+=[(t,f2,BLUE) for t in L2]
    tot=sum(f.size*1.22 for _,f,_ in lines)
    y=Hd//2-tot//2+(0 if FMT=='1x1' else 10)
    for t,f,c in lines:
        w=f.getlength(t); d.text(((Wd-w)/2,y),t,font=f,fill=c); y+=f.size*1.22
    p=f'{S}/cards/{name}_{FMT}.png'; im.save(p); return p

C={}
C['bp']=card('bp','The Longevity Blueprint.','18 weeks. Live on Zoom.')
C['proto']=card('proto','Your own protocol.','Built on your numbers.')
C['weeks']=card('weeks','In only 18 weeks.')
C['vip']=card('vip','VIP masterclass access.','Included free.')
C['julie']=card('julie','Julie Gibson Clark VIP masterclass.','November 14. Included free.')
C['price']=card('price','Over 50% off your first month.','$79.')
C['mbg']=card('mbg','14-day money-back guarantee.')

def cut_src(name,a,b):
    p=f'{S}/{name}_{FMT}.mp4'
    if not os.path.exists(p):
        run(['ffmpeg','-loglevel','error','-y','-ss',str(a),'-to',str(b),'-i',BP,'-an','-r','24','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',p])
    return p
cgm=cut_src('cgm',58.5,60.4); zoom=cut_src('zoom',51.917,53.9); jt=cut_src('jt',33.3,35.4); end=cut_src('end',77.958,81.5)

# overlays per clip: (start,len,kind,src)  kind: 'v' footage hard cut, 'c' card with alpha fade
OV={1:[(6.4,2.4,'c',C['proto']),(10.5,2.4,'c',C['weeks'])],
    2:[(0.10,1.9,'v',cgm),(3.9,2.3,'c',C['vip']),(8.1,3.2,'v',zoom)],
    3:[(0.10,2.1,'v',jt),(2.25,2.35,'c',C['julie']),(5.6,2.5,'c',C['price']),(9.8,2.6,'c',C['mbg'])]}
def hidden(i,m): return any(m['s']<st+ln+0.3 and m['e']>st-0.3 for st,ln,k,f in OV[i])

# stage 1: offer clips (gen chunks concatenated)
for i in (1,2,3):
    L=LENS[i]
    inputs=['-i',f'{S}/gen/h{i}a.mp4','-i',f'{S}/gen/h{i}b.mp4','-i',f'{S}/gen/h{i}c.mp4']
    fc=["[0:v]trim=0:5,setpts=PTS-STARTPTS[a];[1:v]trim=0:5,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[cat]",
        f"[cat]trim=0:{L},setpts=PTS-STARTPTS,{CROP}scale=1080:{H},fps=24,format=yuv420p[b0]",
        "[0:a]atrim=0:5,asetpts=PTS-STARTPTS[x];[1:a]atrim=0:5,asetpts=PTS-STARTPTS[y];[2:a]asetpts=PTS-STARTPTS[z];[x][y][z]concat=n=3:v=0:a=1[acat]",
        f"[acat]atrim=0:{L},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[ao]"]
    n=1; cur='b0'
    for st,ln,k,f in OV[i]:
        idx=inputs.count('-i')
        if k=='v':
            inputs+=['-i',f]
            fc.append(f"[{idx}:v]trim=0:{ln},setpts=PTS-STARTPTS+{st}/TB,{CROP if False else ''}scale=1080:{H},fps=24,format=yuv420p[k{n}]")
        else:
            inputs+=['-loop','1','-t',str(ln),'-i',f]
            fc.append(f"[{idx}:v]fps=24,format=rgba,fade=t=in:st=0:d=0.25:alpha=1,fade=t=out:st={ln-0.25}:d=0.25:alpha=1,setpts=PTS-STARTPTS+{st}/TB[k{n}]")
        fc.append(f"[{cur}][k{n}]overlay=eof_action=pass[b{n}]"); cur=f'b{n}'; n+=1
    for m in META:
        if m['clip']!=i or hidden(i,m): continue
        idx=inputs.count('-i'); inputs+=['-loop','1','-t',f"{m['e']+0.05}",'-i',f"{REPO}/caps/cap_{FMT}_{m['i']:02d}.png"]
        fc.append(f"[{cur}][{idx}:v]overlay=x=(W-w)/2:y={CAP_Y}:eof_action=pass:enable='between(t,{m['s']},{m['e']})'[b{n}]"); cur=f'b{n}'; n+=1
    run(['ffmpeg','-loglevel','error','-y']+inputs+['-filter_complex',';'.join(fc),'-map',f'[{cur}]','-map','[ao]','-r','24','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',f'{S}/c{i}_{FMT}.mp4'])
    print('clip',i,'ok',flush=True)

# music bed from W3 end cards
if not os.path.exists(f'{S}/music_{FMT}.wav'):
    run(['ffmpeg','-loglevel','error','-y','-ss','63','-to','70','-i',W3,'-vn','-ac','2','-ar','48000',f'{S}/seg.wav'])
    ins=[]; 
    for k in range(8): ins+=['-i',f'{S}/seg.wav']
    ch='[0][1]acrossfade=d=0.8:c1=tri:c2=tri[x1]'+''.join(f';[x{k-1}][{k}]acrossfade=d=0.8:c1=tri:c2=tri[x{k}]' for k in range(2,8))
    run(['ffmpeg','-loglevel','error','-y']+ins+['-filter_complex',ch,'-map','[x7]',f'{S}/music_{FMT}.wav'])

# stage 2
total=LENS[1]+LENS[2]+LENS[3]+3.0
inputs=['-i',W3,'-i',BP,'-loop','1','-t','1.3','-i',C['bp'],'-i',f'{S}/c1_{FMT}.mp4','-i',f'{S}/c2_{FMT}.mp4','-i',f'{S}/c3_{FMT}.mp4','-i',end,'-i',f'{S}/music_{FMT}.wav']
fc=[f"[0:v]trim=0:{HOOK_END},setpts=PTS-STARTPTS,fps=24,format=yuv420p[v0]",
    f"[0:a]atrim=0:{HOOK_END},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a0]",
    f"[1:v]trim={BP_IN}:{BP_OUT},setpts=PTS-STARTPTS,fps=24,format=yuv420p[bpv]",
    f"[2:v]fps=24,format=rgba,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st=1.1:d=0.2:alpha=1,setpts=PTS-STARTPTS+{24.6-BP_IN}/TB[bc]",
    "[bpv][bc]overlay=eof_action=pass[v1]",
    f"[1:a]atrim={BP_IN}:{BP_OUT},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a1]",
    "[6:v]trim=0:3.0,setpts=PTS-STARTPTS,fps=24,format=yuv420p,fade=t=out:st=2.5:d=0.5[v6]",
    "[v0][v1][3:v][4:v][5:v][v6]concat=n=6:v=1:a=0[v]",
    "[3:a]volume=-4.5dB[s1];[4:a]volume=-4.5dB[s2];[5:a]volume=-4.5dB[s3]",
    "anullsrc=r=48000:cl=stereo,atrim=0:3.0[sil]",
    "[s1][s2][s3][sil]concat=n=4:v=0:a=1[spk]",
    f"[7:a]atrim=0:{total},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=0.28,afade=t=in:st=0:d=0.6,afade=t=out:st={total-1.2}:d=1.2[mus]",
    "[spk][mus]amix=inputs=2:duration=first:normalize=0[off]",
    "[a0][a1][off]concat=n=3:v=0:a=1[a]"]
out=f'{S}/out/W3_Blueprint_Nov_{FMT}.mp4'
run(['ffmpeg','-loglevel','error','-y']+inputs+['-filter_complex',';'.join(fc),'-map','[v]','-map','[a]','-r','24','-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',out])
print('final',FMT,out,flush=True)
