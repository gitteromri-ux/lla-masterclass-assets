from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
import json

P=Path(__file__).resolve().parent
ROOT=P/'source' if (P/'source').exists() else P.parent
P.mkdir(exist_ok=True)
W,H=1920,1080
WHITE=(247,250,255); BLUE=(169,207,245)
F=P/'source/fonts' if (P/'source/fonts').exists() else Path('/home/user/fonts')
yy,xx=np.mgrid[:H,:W]
records=[]

def base():
    a=np.exp(-2*((xx-960)/1000)**2-2*((yy-460)/680)**2)
    arr=np.zeros((H,W,3),dtype=np.uint8)
    for k,(b,l) in enumerate([(2,9),(6,19),(17,33)]):arr[:,:,k]=b+a*l
    return Image.fromarray(arr).convert('RGBA')

def logo(im,w=460,y=70,x=None):
    a=Image.open(ROOT/'sc/logo.png').convert('RGBA')
    a=a.crop(a.getbbox())
    a=a.resize((w,round(a.height*w/a.width)),Image.Resampling.LANCZOS)
    im.alpha_composite(a,((W-w)//2 if x is None else x,y))

def txt(im,s,y,size,col=WHITE,italic=False,x=960,center=True,family='InstrumentSerif'):
    name=f'{family}-{"Italic" if italic else "Regular"}.ttf'
    f=ImageFont.truetype(str(F/name),size)
    m=Image.new('L',(W,H));d=ImageDraw.Draw(m)
    if center:x-=d.textlength(s,font=f)/2
    d.text((x,y),s,font=f,fill=255,anchor='lt')
    bb=m.getbbox()
    assert bb and bb[0]>=100 and bb[2]<=1820 and bb[3]<=940,(s,bb)
    records.append({'text':s,'bounds':bb,'font_size':size})
    for r,o in [(32,.15),(9,.24)]:
        z=Image.new('RGBA',(W,H),(*col,0))
        z.putalpha(m.filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*o)))
        im.alpha_composite(z)
    arr=np.zeros((H,W,4),dtype=np.uint8)
    t=np.clip((np.arange(H)-bb[1])/max(1,bb[3]-bb[1]),0,1)
    for k in range(3):arr[:,:,k]=np.round(col[k]+(255-col[k])*(1-t[:,None])*.18)
    arr[:,:,3]=np.array(m)
    im.alpha_composite(Image.fromarray(arr))

def rule(im,y,w=590):
    a=Image.new('RGBA',(W,H));d=ImageDraw.Draw(a)
    for x in range((W-w)//2,(W+w)//2):
        alpha=round(150*(1-abs(x-W/2)/(w/2)))
        d.line((x,y,x,y+1),fill=(*BLUE,alpha))
    im.alpha_composite(a)

def save(im,n):
    im.convert('RGB').save(P/f'card-{n}.png')
    im.convert('RGB').resize((960,540),Image.Resampling.LANCZOS).save(P/f'card-{n}.jpg',quality=95)

# Reference-led typography; original approved portrait, no generated face.
im=base()
p=ImageOps.fit(Image.open(ROOT/'julie/julie-lifestyle.jpg').convert('RGBA'),(1390,1080),centering=(.48,.3))
im.alpha_composite(p,(530,0))
a=1-np.clip((xx-680)/590,0,1)
a=np.maximum(a,np.clip((yy-850)/230,0,.9))
overlay=np.zeros((H,W,4),dtype=np.uint8);overlay[:,:,:3]=(3,8,21);overlay[:,:,3]=(a*255).astype('uint8')
im.alpha_composite(Image.fromarray(overlay))
logo(im,450,70,150)
txt(im,'Longevity',340,146,italic=True,x=150,center=False)
txt(im,'Masterclass',500,146,italic=True,x=150,center=False)
txt(im,'of the Year',665,146,BLUE,True,x=150,center=False)
txt(im,'with Julie Gibson Clark',860,71,WHITE,True,x=155,center=False)
save(im,1)

# Clock visible as a physical object, but used on this card only.
im=Image.open(ROOT/'sc/clock_navy4k.jpg').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
shade=np.clip(.61+.22*((xx-960)/1000)**2+.14*((yy-540)/650)**2,0,.93)
ov=np.zeros((H,W,4),dtype=np.uint8);ov[:,:,:3]=(2,7,19);ov[:,:,3]=(shade*255).astype('uint8')
im.alpha_composite(Image.fromarray(ov));logo(im,460,70)
txt(im,'Learn to age slower',382,190,WHITE,True)
rule(im,610,760)
txt(im,'from the world’s',665,142,BLUE,True)
txt(im,'2nd slowest ager',798,142,BLUE,True)
save(im,2)

# Event hierarchy: VIP offer as header, then date and time.
im=base();logo(im,460,70)
txt(im,'90 Min VIP Masterclass',332,116)
txt(im,'+ Live Q&A Included',462,88,BLUE,True)
rule(im,612,620)
txt(im,'Saturday, Nov 14th',656,150)
txt(im,'12 PM ET · Live on Zoom',840,92,BLUE,True)
save(im,3)

# Duration is separate, explicitly VIP-qualified, with no scarcity copy.
im=base();logo(im,460,70)
txt(im,'VIP experience',340,91,BLUE,True)
txt(im,'90 minutes live',480,178)
rule(im,690,740)
txt(im,'Masterclass + live Q&A',772,130,BLUE,True)
save(im,4)

# Clean enrollment finish replaces the outdated dated source end card.
im=base();logo(im,460,70)
txt(im,'Enroll now',511,210)
rule(im,755,640)
txt(im,'Nov 14th · 12 PM ET',825,111,BLUE,True)
save(im,5)

(P/'text-bounds.json').write_text(json.dumps(records,indent=2))
sheet=Image.new('RGB',(1920,1620),(3,8,21))
for i in range(5):
    sheet.paste(Image.open(P/f'card-{i+1}.jpg'),((i%2)*960,(i//2)*540))
sheet.save(P/'Julie-Masterclass-Ending-Frames.jpg',quality=95)
phone=Image.new('RGB',(390,219*5),(3,8,21))
for i in range(5):
    phone.paste(Image.open(P/f'card-{i+1}.png').resize((390,219),Image.Resampling.LANCZOS),(0,219*i))
phone.save(P/'phone-proof.jpg',quality=95)
print('Five 1080p cards rendered; all text bounds validated.')
