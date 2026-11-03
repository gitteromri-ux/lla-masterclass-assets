import subprocess, sys, os, numpy as np, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=os.path.dirname(os.path.abspath(__file__)); REPO='/home/user/lla-masterclass-assets/ugc-bp-nov'; U='/home/user/gitteromri-ux/lla-julie-ugc-ads'
FULL='/home/user/lla-masterclass-assets/video/julie-masterclass-film-full-1080p-masterclass-edit-v2.mp4'
FMT=sys.argv[1]; H=1920 if FMT=='9x16' else 1080; OFF=0 if FMT=='9x16' else 409
FJ=f'/home/user/lla-blueprint-nov-adjusted/film2/LLA_Julie_Film_75s_BP79_{FMT}.mp4'
BG=f'{U}/hookbuild/'+('cardbg9.png' if FMT=='9x16' else 'cardbg1b.png')
FREG=f'{REPO}/fonts/PlayfairDisplay-Regular.ttf'; FIT=f'{REPO}/fonts/PlayfairDisplay-Italic.ttf'
WHITE=(250,248,245); BLUE=(158,190,235); RULE=(120,135,170)
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode: print('FAIL',' '.join(c)[:300],r.stderr[-1200:]); sys.exit(1)
def wrap(f,text,maxw):
    if '\n' in text: return text.split('\n')
    if f.getlength(text)<=maxw: return [text]
    ws=text.split(); best=None
    for k in range(1,len(ws)):
        a,b=' '.join(ws[:k]),' '.join(ws[k:]); w=max(f.getlength(a),f.getlength(b))
        if w<=maxw and (best is None or w<best[0]): best=(w,a,b)
    return [best[1],best[2]] if best else [text]
def overlay(big,sub,path,band=False,cy=None,bs=None,ss=None,small=None):
    W=1080; bs0,ss0,cy0,maxw=(96,70,962,900) if FMT=='9x16' else (74,54,540,860)
    bs=bs or bs0; ss=ss or ss0; cy=cy or cy0
    fb=ImageFont.truetype(FREG,bs); fs=ImageFont.truetype(FIT,ss)
    lines=[(t,fb,WHITE) for t in wrap(fb,big,maxw)]+([(t,fs,BLUE) for t in wrap(fs,sub,maxw)] if sub else [])
    hs=[int(f.size*1.18) for _,f,_ in lines]; tot=sum(hs)+int(bs*0.45)+3
    im=Image.new('RGBA',(W,H),(0,0,0,0))
    if band:
        b=Image.new('RGBA',(W,H),(0,0,0,0)); d0=ImageDraw.Draw(b); pad=int(bs*0.9)
        d0.rectangle([0,cy-tot//2-pad,W,cy+tot//2+pad],fill=(5,13,34,165)); b=b.filter(ImageFilter.GaussianBlur(28)); im=Image.alpha_composite(im,b)
    d=ImageDraw.Draw(im); y=cy-tot//2
    for (t,f,c),h in zip(lines,hs):
        w=f.getlength(t); d.text(((W-w)/2,y),t,font=f,fill=c+(255,)); y+=h
    y+=int(bs*0.45); d.rectangle([W//2-70,y,W//2+70,y+2],fill=RULE+(255,))
    if small:
        fsm=ImageFont.truetype(FIT,int(ss*0.62)); w=fsm.getlength(small); d.text(((W-w)/2,y+14),small,font=fsm,fill=BLUE+(255,))
    im.save(path); return path
def card(big,sub,path,bs=None):
    im=Image.open(BG).convert('RGBA'); d=ImageDraw.Draw(im)
    bs=bs or (120 if FMT=='9x16' else 90)
    fb=ImageFont.truetype(FREG,bs); fs=ImageFont.truetype(FIT,80 if FMT=='9x16' else 60)
    bl=wrap(fb,big,940); y=(790-OFF) if FMT=='9x16' else 381
    y-= (len(bl)-1)*int(bs*0.6)
    for t in bl:
        b=fb.getbbox(t); w=b[2]-b[0]; d.text(((1080-w)//2-b[0],y-b[1]),t,font=fb,fill=WHITE+(255,)); y+=int(bs*1.2)
    y+=int(bs*0.35); b=fs.getbbox(sub); w=b[2]-b[0]; d.text(((1080-w)//2-b[0],y-b[1]),sub,font=fs,fill=BLUE+(255,)); y+=int(fs.size*1.5)
    d.rectangle([470,y,610,y+2],fill=(69,81,113,255)); im.convert('RGB').save(path); return path
CROP="scale=-2:1920,crop=1080:1920" if FMT=='9x16' else "crop=1080:1080:420:0"
def beat_footage(src,a,b,txt,out,dur,seek=True):
    run(['ffmpeg','-loglevel','error','-y','-ss',str(a),'-to',str(b),'-i',src,'-loop','1','-t',str(dur),'-i',txt,'-filter_complex',f"[0:v]{CROP},fps=24,format=yuv420p[f];[1:v]format=rgba,fade=t=in:st=0:d=0.15:alpha=1[t];[f][t]overlay=format=auto,format=yuv420p",'-t',str(dur),'-r','24','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',out])
def beat_still(png,out,dur):
    run(['ffmpeg','-loglevel','error','-y','-loop','1','-t',str(dur),'-i',png,'-vf','fps=24,format=yuv420p','-r','24','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',out])
D=[2.2,2.2,2.2,2.3,3.2,3.6]
b1=card('The Longevity\nBlueprint.','by Longevity Life Academy.',f'{S}/e1_{FMT}.png',bs=136 if FMT=='9x16' else 100); beat_still(b1,f'{S}/eb1_{FMT}.mp4',D[0])
t2=overlay('18 weeks.\n18 live sessions.','Live online, in a small group.',f'{S}/e2_{FMT}.png')
run(['ffmpeg','-loglevel','error','-y','-i',f'{S}/zoomgrid_{FMT}.mp4','-loop','1','-t',str(D[1]),'-i',t2,'-filter_complex',"[1:v]format=rgba,fade=t=in:st=0:d=0.15:alpha=1[t];[0:v][t]overlay=format=auto,format=yuv420p",'-t',str(D[1]),'-r','24','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',f'{S}/eb2_{FMT}.mp4'])
b3=card('Get your longevity\nprotocol.','In only 18 weeks.',f'{S}/e3_{FMT}.png',bs=120 if FMT=='9x16' else 90); beat_still(b3,f'{S}/eb3_{FMT}.mp4',D[2])
t4=overlay('Free Abbott Lingo CGM.','Included. Shipped to you.',f'{S}/e4_{FMT}.png',band=True); beat_footage(FULL,121.3,123.9,t4,f'{S}/eb4_{FMT}.mp4',D[3])
t5=overlay('Free VIP masterclass access.',"With Julie Gibson Clark, the world's second slowest ager.",f'{S}/e5_{FMT}.png',band=True,cy=(900 if FMT=='9x16' else 470),bs=(92 if FMT=='9x16' else 70),ss=(62 if FMT=='9x16' else 48))
im=Image.open(t5).convert('RGBA'); d=ImageDraw.Draw(im)
fd=ImageFont.truetype(FREG,150 if FMT=='9x16' else 96); txt='November 14'; w=fd.getlength(txt); yd=(1430 if FMT=='9x16' else 860)
b=Image.new('RGBA',im.size,(0,0,0,0)); d0=ImageDraw.Draw(b); d0.rectangle([0,yd-70,1080,yd+fd.size+60],fill=(5,13,34,170)); b=b.filter(ImageFilter.GaussianBlur(26)); im=Image.alpha_composite(im,b); d=ImageDraw.Draw(im)
d.text(((1080-w)/2,yd),txt,font=fd,fill=WHITE+(255,)); im.save(t5)
run(['ffmpeg','-loglevel','error','-y','-i',f'{S}/zoomfull_{FMT}.mp4','-loop','1','-t',str(D[4]),'-i',t5,'-filter_complex',"[1:v]format=rgba,fade=t=in:st=0:d=0.15:alpha=1[t];[0:v][t]overlay=format=auto,format=yuv420p",'-t',str(D[4]),'-r','24','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',f'{S}/eb5_{FMT}.mp4'])
# end card with the price line
FJ1='/home/user/lla-blueprint-nov-adjusted/film2/LLA_Julie_Film_75s_BP79_1x1.mp4'
if FMT=='9x16':
    t6=overlay('55% off trial · $79 a month.',None,f'{S}/e6_{FMT}.png',cy=1515,bs=72,ss=46,small='Month one.')
    run(['ffmpeg','-loglevel','error','-y','-ss','61.04','-to','64.3','-i',FJ,'-ss','61.04','-to','64.3','-i',FJ1,'-loop','1','-t',str(D[5]),'-i',t6,'-filter_complex',
         "[0:v]fps=24,gblur=sigma=70,format=yuv420p,tpad=stop_mode=clone:stop_duration=0.4[bg];[1:v]fps=24,format=yuv420p,tpad=stop_mode=clone:stop_duration=0.4[pc];[bg][pc]overlay=0:400[f];[2:v]format=rgba,fade=t=in:st=0.5:d=0.3:alpha=1[t];[f][t]overlay=format=auto,format=yuv420p",
         '-t',str(D[5]),'-r','24','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',f'{S}/eb6_{FMT}.mp4'])
else:
    t6=overlay('55% off trial · $79 a month.',None,f'{S}/e6_{FMT}.png',cy=975,bs=54,ss=36,small='Month one.')
    run(['ffmpeg','-loglevel','error','-y','-ss','61.04','-to','64.3','-i',FJ1,'-loop','1','-t',str(D[5]),'-i',t6,'-filter_complex',"[0:v]fps=24,format=yuv420p,tpad=stop_mode=clone:stop_duration=0.4[f];[1:v]format=rgba,fade=t=in:st=0.5:d=0.3:alpha=1[t];[f][t]overlay=format=auto,format=yuv420p",'-t',str(D[5]),'-r','24','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',f'{S}/eb6_{FMT}.mp4'])
with open(f'{S}/elist_{FMT}.txt','w') as f:
    for i in range(1,7): f.write(f"file 'eb{i}_{FMT}.mp4'\n")
run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',f'{S}/elist_{FMT}.txt','-c','copy',f'{S}/ending_{FMT}.mp4'])
EL=sum(D)
# audio: film2 music 45.83 -> 45.83+EL continuous, 0.6 s fade-out, 0.4 s fade-in
SR=48000
r=subprocess.run(['ffmpeg','-v','error','-ss','45.83','-t',f'{EL:.4f}','-i',FJ,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
x=np.frombuffer(r,np.float32).reshape(-1,2).copy(); N=int(EL*SR); x=np.vstack([x,np.zeros((max(0,N-len(x)),2),np.float32)])[:N]
fi=int(0.4*SR); fo=int(0.6*SR); x[:fi]*=np.linspace(0,1,fi)[:,None]; x[-fo:]*=np.linspace(1,0,fo)[:,None]
with wave.open(f'{S}/ending_{FMT}.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())
print('ending',FMT,'ok',EL)
