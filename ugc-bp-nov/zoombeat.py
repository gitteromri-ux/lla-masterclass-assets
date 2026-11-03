import subprocess, sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
S=os.path.dirname(os.path.abspath(__file__)); REPO='/home/user/lla-masterclass-assets/ugc-bp-nov'
FREG=f'{REPO}/fonts/PlayfairDisplay-Regular.ttf'; FIT=f'{REPO}/fonts/PlayfairDisplay-Italic.ttf'
WHITE=(250,248,245); BLUE=(158,190,235); RULE=(120,135,170); BG='0x050d22'
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode: print('FAIL',' '.join(c)[:300],r.stderr[-1200:]); sys.exit(1)
# 1. slow the 2.35 s grid shot to 4.5 s at 24 fps (motion-interpolated)
if not os.path.exists(f'{S}/zoom_slow.mp4'):
    run(['ffmpeg','-loglevel','error','-y','-i',f'{S}/zoom12_src.mp4','-vf',"setpts=1.915*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1",'-t','4.5','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',f'{S}/zoom_slow.mp4'])
XS=[(0,628),(634,1285),(1291,1920)]; YS=[(0,353),(357,724),(729,1080)]
tiles=[(x0,y0,x1-x0,y1-y0) for (y0,y1) in YS for (x0,x1) in XS]
TW,TH=538,303
def grid(fmt,positions,out):
    n=len(positions); fc=[f"[0:v]split={n}"+''.join(f'[s{i}]' for i in range(n))]
    H=1920 if fmt=='9x16' else 1080
    fc.append(f"color=c={BG}:s=1080x{H}:r=24:d=4.5[bg]")
    cur='bg'
    for i,(ti,(px,py)) in enumerate(positions):
        x,y,w,h=tiles[ti]
        fc.append(f"[s{i}]crop={w}:{h}:{x}:{y},scale={TW}:{TH}[t{i}]")
        fc.append(f"[{cur}][t{i}]overlay={px}:{py}:shortest=1[g{i}]"); cur=f'g{i}'
    run(['ffmpeg','-loglevel','error','-y','-i',f'{S}/zoom_slow.mp4','-filter_complex',';'.join(fc),'-map',f'[{cur}]','-t','4.5','-r','24','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',out])
pos916=[(0,(0,0)),(1,(542,0)),(2,(0,307)),(3,(542,307)),(4,(0,1310)),(5,(542,1310)),(6,(0,1613)),(7,(542,1613))]
pos11=[(0,(0,0)),(1,(542,0)),(4,(0,777)),(5,(542,777))]
grid('9x16',pos916,f'{S}/zoomgrid_9x16.mp4'); grid('1x1',pos11,f'{S}/zoomgrid_1x1.mp4')
# 2. text overlays in the film style
def wrap(f,text,maxw):
    if f.getlength(text)<=maxw: return [text]
    ws=text.split(); best=None
    for k in range(1,len(ws)):
        a,b=' '.join(ws[:k]),' '.join(ws[k:]); w=max(f.getlength(a),f.getlength(b))
        if w<=maxw and (best is None or w<best[0]): best=(w,a,b)
    return [best[1],best[2]] if best else [text]
def overlay(fmt,big,sub,path):
    W=1080; H=1920 if fmt=='9x16' else 1080
    bs,ss,cy,maxw=(96,70,962,900) if fmt=='9x16' else (74,54,540,860)
    fb=ImageFont.truetype(FREG,bs); fs=ImageFont.truetype(FIT,ss)
    lines=[(t,fb,WHITE) for t in wrap(fb,big,maxw)]+[(sub,fs,BLUE)]
    hs=[int(f.size*1.18) for _,f,_ in lines]; tot=sum(hs)+int(bs*0.45)+3
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); y=cy-tot//2
    for (t,f,c),h in zip(lines,hs):
        w=f.getlength(t); d.text(((W-w)/2,y),t,font=f,fill=c+(255,)); y+=h
    y+=int(bs*0.45); d.rectangle([W//2-70,y,W//2+70,y+2],fill=RULE+(255,))
    im.save(path)
for fmt in ('9x16','1x1'):
    overlay(fmt,'18 live sessions over 18 weeks.','Live online, in a small group.',f'{S}/z1_{fmt}.png')
    overlay(fmt,'VIP masterclass with Julie Gibson Clark.','November 14. Included free.',f'{S}/z2_{fmt}.png')
    overlay(fmt,'Over 50% off your first month.','Start for $79.',f'{S}/z3_{fmt}.png')
    # composite beat: grid + z1 (0-2.25) + z2 (2.25-4.5)
    run(['ffmpeg','-loglevel','error','-y','-i',f'{S}/zoomgrid_{fmt}.mp4','-loop','1','-t','2.25','-i',f'{S}/z1_{fmt}.png','-loop','1','-t','2.3','-i',f'{S}/z2_{fmt}.png','-filter_complex',
         "[1:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st=2.1:d=0.15:alpha=1[a];[2:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1,setpts=PTS+2.25/TB[b];[0:v][a]overlay=eof_action=pass:format=auto[x];[x][b]overlay=eof_action=pass:format=auto,format=yuv420p",
         '-r','24','-t','4.5','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',f'{S}/zoombeat_{fmt}.mp4'])
    print('beat',fmt,'ok')
