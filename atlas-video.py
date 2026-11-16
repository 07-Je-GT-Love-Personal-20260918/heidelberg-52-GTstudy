"""Render the silent, captioned atlas intro. Needs Pillow and imageio-ffmpeg.
Run: python atlas-video.py /path/to/a/CJK-font.ttc
The result is committed; regular website builds do not need this toolchain.
"""
import json
import math
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
ROUTES = json.loads((ROOT/'content/atlas.json').read_text(encoding='utf8'))
FONT = sys.argv[1]
fonts = {n: ImageFont.truetype(FONT,n) for n in (20,23,26,32,55)}
W,H,FPS = 960,540,24
colors=['#84ccff','#8de0be','#cbb6ff','#ffce88']
base=Image.new('RGB',(W,H),'#13283e')
g=ImageDraw.Draw(base)
for x in range(0,W,48):g.line((x,0,x,H),fill='#203950')
for y in range(0,H,48):g.line((0,y,W,y),fill='#203950')
def lines(text,length):
    return [text[i:i+length] for i in range(0,len(text),length)]

with subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'atlas-intro.mp4')],stdin=subprocess.PIPE) as ffmpeg:
    for frame in range(32*FPS):
        part,t=divmod(frame,8*FPS)
        route,accent=ROUTES[part],colors[part]
        im=base.copy()
        d=ImageDraw.Draw(im)
        d.text((52,34),f'GTSTUDY FIELD ATLAS   ·   {part+1:02}/04',font=fonts[20],fill=accent)
        d.text((52,85),route['title'],font=fonts[55],fill='#f6fbff')
        d.text((54,165),route['era'],font=fonts[23],fill='#d0e1f1')
        for j,caption in enumerate(lines(route['answer'],33)):
            d.text((54,226+j*35),caption,font=fonts[26],fill='#eff7fb')
        x0,x1=68,892
        d.line((x0,383,x1,383),fill='#557185',width=3)
        progress=min(1,t/(5.7*FPS))
        d.line((x0,383,int(x0+(x1-x0)*progress),383),fill=accent,width=4)
        for j,label in enumerate(route['flow']):
            x=68+j*280
            d.ellipse((x-9,374,x+9,392),fill=accent if t>=j*FPS else '#7f98aa')
            for k,line in enumerate(lines(label,12)):
                d.text((x-8,407+28*k),line,font=fonts[20],fill='#f2fbff')
        d.rectangle((0,H-5,math.ceil((frame+1)/(32*FPS)*W),H),fill=accent)
        ffmpeg.stdin.write(im.tobytes())
    ffmpeg.stdin.close()
    if ffmpeg.wait():raise SystemExit('ffmpeg encoding failed')
