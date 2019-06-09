import numpy as np
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
    filled_len = round(bar_len * count / float(total))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    if percents == 100:
        sys.stdout.write('[ %s ] %s%s %s\r' % (bar, percents, '%', suffix))
        # sys.stdout.flush() 
        sys.stdout.write( "\n" + suffix + ' finished\n' )
    else:
        sys.stdout.write('[ %s ] %s%s %s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush() 


# scan the folder
def list_folder(folder):
    tmp = []
    for root, dirs, files in os.walk(os.path.abspath(folder)):
        for file in files:
            tmp.append(os.path.join(root, file))
    return tmp

# generator that returns images
def image_generator(files):
    index = 0
    for file in files:
        name, ext = os.path.splitext(os.path.basename(file))
        raw = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        yield raw, name, ext, file

def tiler( files, file_name, tile_size ):

    filecount = len(files)
    count = int(math.sqrt(filecount) + .5)


    size = count * tile_size

    img = np.full((count * tile_size, count * tile_size, 3), 0, dtype=np.uint8)
    print( "tile size:{} tile count:{} ^ 2 image size:{}".format( tile_size, count, img.shape ) )
    
    uid = 0
    gen = image_generator(files)
    for src, n, e, f in gen:
        
        x = int(uid % count) * tile_size
        y = int(uid / count) * tile_size

        progress( uid, len( files ) - 1, "tiling" )
        uid += 1

        # paste img inside cell with aspect ratio
        w = src.shape[1]
        h = src.shape[0]

        d = tile_size
        dw = tile_size
        dh = tile_size
        if w >= h:
            dh = int( d * (h/w) )
            y = int( y + (tile_size-dh) / 2 )
        else:
            dw = int( d * (w/h) )
            x = int( x + (tile_size-dw) / 2 )
            
        src = cv2.resize(src, (dw, dh))
        try:
            img[y:(y+dh), x:(x+dw)] = src
        except:
            continue
            
    cv2.imwrite( file_name, img )

if __name__ == "__main__":

    
    folder = "insects"
    files_list = list_folder(folder)
    tiler( files_list, "tiles.png", 512 )

