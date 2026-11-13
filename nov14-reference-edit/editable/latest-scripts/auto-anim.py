# "Make longevity / automatic." card: 1.5s eased fade + 24px rise over the locked logo-only navy base.
import importlib.util,sys
from pathlib import Path
from PIL import Image
spec=importlib.util.spec_from_file_location('b','build.py');b=importlib.util.module_from_spec(spec)
src=Path('build.py').read_text().split('# Reference-led typography')[0]
exec(src,b.__dict__)
W,H=1920,1080
layer=Image.new('RGBA',(W,H),(0,0,0,0))
b.txt(layer,'Make longevity',382,164)
b.txt(layer,'automatic.',584,164,b.BLUE,True)
from PIL import ImageDraw
d=ImageDraw.Draw(layer)
for x in range(960-420,960+420):
    d.line((x,812,x,813),fill=(196,178,146,round(170*min(1,(420-abs(x-960))/60))))
base=Image.open('card-blank.png').convert('RGBA')
out=Path('auto-frames');out.mkdir(exist_ok=True)
N=45
for i in range(N+1):
    t=i/N; e=1-(1-t)**3
    f=base.copy()
    l=layer.copy(); a=l.getchannel('A').point(lambda v:int(v*e)); l.putalpha(a)
    s=Image.new('RGBA',(W,H),(0,0,0,0)); s.alpha_composite(l,(0,round(24*(1-e))))
    f.alpha_composite(s); f.convert('RGB').save(out/f'f{i:03d}.png')
f.convert('RGB').save('card-automatic.png'); f.convert('RGB').resize((960,540)).save('card-automatic.jpg',quality=95)
print('ok')
