from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL.ExifTags import TAGS
import os, sys
from multiprocessing import Pool,cpu_count
import argparse


def progressbar(it, prefix="", size=60, file=sys.stdout, count=1):
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

def processone(packedarg):
    file, processeddir, args=packedarg
    try:
        if not os.path.exists(processeddir):
            os.mkdir(processeddir)

        img = Image.open(os.path.join(args.dir, file))
        exifs={}
        for (k,v) in img._getexif().items():
            exifs[TAGS.get(k)]=v

        file=exifs["DateTimeDigitized"].replace(":","")+".JPG"
        # if os.path.exists(os.path.join(processeddir, file)):
        #     return

        font = ImageFont.truetype("retro2.ttf", int(img.size[0]/80))
        monofont = ImageFont.truetype("mono.ttf", int(img.size[0]/60))
        

        iso=exifs["ISOSpeedRatings"]
        try:
            focallen="%3.0f"%(exifs["FocalLength"][0]/exifs["FocalLength"][1])
            shutter=exifs["ExposureTime"][0]/exifs["ExposureTime"][1]
            fnum=exifs["FNumber"][0]/exifs["FNumber"][1]
        except:
            focallen="%3.0f"%(exifs["FocalLength"])
            shutter=exifs["ExposureTime"]
            fnum=exifs["FNumber"]
        
        shottime=exifs["DateTimeDigitized"].replace(":"," ")
        
        if fnum>9:
            fnum="%-3.0f"%(fnum)
        else:
            fnum="%1.1f"%(fnum)

        if shutter<0.3: 
            shuttertext="S/"
            shutter="1/%-4.0f"%(1/shutter)
        elif shutter<10:
            shuttertext="S "
            shutter="%-.1f\""%shutter
        else:
            shuttertext="S "
            shutter="%-.0f\""%shutter
        #shutter=" "*(4-len(shutter))+shutter

        borderwidth=int(min(img.size)*0.03)
        textheight=int(min(img.size)*0.03)
        newim = Image.new(mode = "RGB", size=(int(img.size[0])+borderwidth*2, int(img.size[1])+borderwidth+textheight), color=(20,20,20))

        newim.paste(img, (borderwidth, borderwidth))
        draw = ImageDraw.Draw(newim)

        digital_text_y=img.size[1]+textheight*0.5+borderwidth*0.6
        mono_text_y=img.size[1]+textheight*0.5+borderwidth*0.8
        # draw.text((borderwidth+img.size[0]*0.06, mono_text_y),f"mm {shuttertext}      f/     ISO",(204, 255, 51),font=monofont)
        draw.text((borderwidth+img.size[0]*0.01, digital_text_y),f"{focallen}mm",(232, 190, 90),font=font)
        draw.text((borderwidth+img.size[0]*0.11, digital_text_y),f"{shutter}S",  (232, 190, 90),font=font)
        draw.text((borderwidth+img.size[0]*0.25, digital_text_y),f"f{fnum}",     (232, 190, 90),font=font)
        draw.text((borderwidth+img.size[0]*0.35, digital_text_y),f"ISO {iso}",   (232, 190, 90),font=font)
        # draw.text((borderwidth+img.size[0]*0.65, mono_text_y),f"DATE",(204, 255, 51),font=monofont)
        draw.text((borderwidth+img.size[0]*0.70, digital_text_y),f"{shottime}",(255, 102, 102),font=font)
        draw.text((borderwidth+img.size[0]*0.50, digital_text_y),args.author,(204, 255, 51),font=font)
        newim.save(os.path.join(processeddir, file), quality=args.quality)
    except Exception as e: 
        print(e)
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir",help='''Specify folder path. For example, --dir "C:\\Users\\heber\\Pictures".
                        Note that a "processed" folder will be created and be used to store processed files.''',required=True)
    parser.add_argument("--author",help='''Who you are.''',default="Twitter Lind")
    parser.add_argument("--quality",help='''Quality of JPEG''',default=95, type=int)
    args = parser.parse_args()
    processeddir=os.path.join(args.dir, f"author_{args.author}")
    packedargs=[]
    for file in os.listdir(args.dir):
        packedargs.append((file, processeddir, args))
    with Pool(processes=cpu_count(), maxtasksperchild=1) as po:
        res=po.imap(processone, packedargs)
        for _ in progressbar(res, count=len(packedargs)):
            pass
    
    
