from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL.ExifTags import TAGS
import os, sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--dir", help='Specify a folder path. For example, `--dir "C:\Users\heber\Pictures"`. Note that a "processed" folder will be created and be used to store processed files.', required=True)
args = parser.parse_args()


processeddir=os.path.join(args.dir, "processed")

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

for file in progressbar(os.listdir(args.dir)):
    try:
        if not os.path.exists(processeddir):
            os.mkdir(processeddir)
#         if os.path.exists(os.path.join(processeddir, file)):
#             continue

        img = Image.open(os.path.join(args.dir, file))
        font = ImageFont.truetype("retro.ttf", int(img.size[0]/30))
        exifs={}
        for (k,v) in img._getexif().items():
            exifs[TAGS.get(k)]=v

        iso=exifs["ISOSpeedRatings"]
        focallen=int(exifs["FocalLength"])
        shutter=exifs["ExposureTime"]
        shottime=exifs["DateTimeDigitized"].replace(":"," ")
        fnum=str(exifs["FNumber"]).replace(".0","")
        if shutter<0.3: 
            shutter="1/"+str(int(1/shutter))
        else:
            shutter=str(shutter)+'"'
        borderwidth=int(min(img.size)*0.03)
        textheight=int(img.size[0]*0.04)
        newim = Image.new(mode = "RGB", size=(int(img.size[0])+borderwidth*2, int(img.size[1])+borderwidth+textheight))
        newim.paste(img, (borderwidth, borderwidth))
        draw = ImageDraw.Draw(newim)
        draw.text((borderwidth+img.size[0]*0.01, img.size[1]+textheight*0.5+borderwidth*0.5),f"{focallen}mm {shutter}  F{fnum}  ISO {iso}",(204, 255, 51),font=font)
        draw.text((borderwidth+img.size[0]*0.70, img.size[1]+textheight*0.5+borderwidth*0.5),f"{shottime}",(204, 255, 51),font=font)
        draw.text((borderwidth+img.size[0]*0.50, img.size[1]+textheight*0.5+borderwidth*0.5),"LindoHe",(255, 102, 102),font=font)
        newim.save(os.path.join(processeddir, file), quality=95)
    except: pass
    
    