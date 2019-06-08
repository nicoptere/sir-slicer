import numpy as np
import glob
import sys
import math
import os

# this allows for very large image manipulation
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
# before importing CV2

import cv2

# credits of that cool bar to https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def progress(count, total, suffix=''):
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total-1)))
    percents = round(100.0 * count / float(total-1), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    if percents == 100:
        sys.stdout.write('progress finished\n' )
    else:
        sys.stdout.write('[ %s ] %s%s %s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush() 


# generator to scan the folder

def list_folder(folder):

    tmp = []
    for root, dirs, files in os.walk(os.path.abspath(folder)):
        for file in files:
            tmp.append(os.path.join(root, file))
    return tmp



def image_folder(files, max=-1):
    index = 0
    for file in files:

        name, ext = os.path.splitext(os.path.basename(file))
        if max != -1 and index >= max:
            break
        raw = cv2.imread(file, cv2.IMREAD_UNCHANGED)

        if raw is None:
            print("broken:", file)
            break
        index += 1

        yield raw, name, ext, file

def tiler( folder, file_name, tile_width, tile_height ):

    files = list_folder(folder)
    filecount = len(files)
    count = int(math.sqrt(filecount) + .5)

    width   = tile_width #512
    height  = tile_height #int(width * (tile_shape[0]/tile_shape[1]) )

    max = -1  # count * count

    size = count * width

    img = np.full((count * height, count * width, 3), 0, dtype=np.uint8)
    print( "tile width:{} tile height:{} tile count:{} ^ 2 image size:{}".format( width, height, count, img.shape ) )
    
    uid = 0
    gen = image_folder(files, max)
    for src, n, e, f in gen:
        
        x = int(uid % count) * width
        y = int(uid / count) * height

        progress( uid, len( files ), "tiled" )
        if uid >= count * count:
            break
        uid += 1

        # if uid % 100 == 0:
        #     print( "tiled: ", uid, "/", len( files ) )
            
        # paste with aspect ratio
        w = src.shape[1]
        h = src.shape[0]
        d = width
        dw = width
        dh = width
        if w >= h:
            dh = int( d * (h/w) )
            y = int( y + (height-dh) / 2 )
        else:
            dw = int( d * (w/h) )
            x = int( x + (width-dw) / 2 )

        src = cv2.resize(src, (dw, dh))
        try:
            img[y:(y+dh), x:(x+dw)] = src
        except:
            print(uid, n)
            continue
            
    cv2.imwrite( file_name, img, [int(cv2.IMWRITE_JPEG_QUALITY), 80] )

if __name__ == "__main__":


    tiler( "<folder>", "tiles.jpg", tile_width, tile_height )

