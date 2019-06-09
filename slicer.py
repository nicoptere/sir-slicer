
import numpy as np
import shutil

import os
# this allows for very large image manipulation
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
# before importing CV2

import cv2

# unused : resize an image given a width with respect to the aspect ratio
def resize(image, name, width, quality=100 ):
    img = cv2.imread(image)
    shape = img.shape
    height = int(width * (shape[0]/shape[1]) )
    img = cv2.resize( img, (width, height) )
    cv2.imwrite( name +".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality ] )

def emptydir(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): 
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def getZoomLevel(x, tile_size=256):
    counter = 0
    while x > tile_size:
        counter += 1
        x  =  x  >>  1
    return counter

def main(image, folder_name = "out", file_format={"format":"png"}, tile_size=256):
    
    # reads input image
    img = cv2.imread(image)

    # sanity check
    if folder_name[-1] != "/":
        folder_name += "/"
    os.makedirs( folder_name, exist_ok=True )
    emptydir(folder_name)
    
    # file format
    extension = file_format["format"].lower()
    # default jpeg quality
    quality = 100
    if "quality" in file_format:
        quality = int( file_format["quality"] )

    # deterrmines the final image size
    shape = img.shape
    w = shape[1]
    h = shape[0]
    size = max( w,h )
    offx = ( size - w ) // 2
    offy = ( size - h ) // 2

    # create a buffer image to slice
    ctx = np.zeros( size ** 2 * 3, dtype=np.uint8 )
    ctx = ctx.reshape( (size, size, 3) )
    ctx[offy:offy+h, offx:offx+w] = img
        
    print( "new image size: {} ^ 2".format( size  ) )

    # finds the max number of zoom levels 
    levels = getZoomLevel(size, tile_size)

    # slice each level into folders "tick tick" 👌
    zoom = levels
    while zoom > 0:

        # creates a X folder
        src = folder_name + str( zoom )+"/"
        os.makedirs( src, exist_ok=True )

        # determines the tile count 
        tile_count = 2 ** zoom

        # determines how much to crop from the buffer
        crop_size = int( size / tile_count )

        print( "zoom: {}, \ttiles: {}, \tcrop size:{}".format(zoom, tile_count, crop_size ) )

        # creates a buffer for the tile
        tmp = np.zeros( tile_size ** 2 * 3, dtype=np.uint8 )
        tmp.reshape( (tile_size, tile_size, 3))

        for x in range( tile_count ):
                
            folder = src + str( x ) +"/"
            os.makedirs( folder, exist_ok=True )

            print( "\t column: {} of {} at zoom {}".format(x, tile_count, zoom) )
            for y in range( tile_count ):
        
                #  finds the X / Y coordinates of the top left corner
                dx = int( x * crop_size )
                dy = int( y * crop_size )

                # copies the cropped area into the tile buffer
                tmp = ctx[dy:dy+crop_size, dx:dx+crop_size]
                tmp = cv2.resize( tmp, (tile_size, tile_size) )

                # skip empty tiles (don't save)
                if np.max(tmp) == 0:
                    continue

                # save tile
                if extension == "jpeg" or extension == "jpg":
                    cv2.imwrite( folder + str(y) +"."+ extension, tmp, 
                    [int(cv2.IMWRITE_JPEG_QUALITY), quality] )
                else:
                    cv2.imwrite( folder + str(y) +"."+ extension, tmp )

        zoom -= 1

    # adds the zoom level 0 tile
    src = folder_name+"0/0/"
    os.makedirs( src, exist_ok=True )
    ctx = cv2.resize( ctx, (tile_size, tile_size) )
    
    # save tile
    if extension == "jpeg" or extension == "jpg":
        cv2.imwrite( src + "0." +extension, ctx, 
        [int(cv2.IMWRITE_JPEG_QUALITY),quality] )
    else:
        cv2.imwrite( src + "0." + extension, ctx )

    #copies html page and assets
    os.makedirs( folder_name + "js", exist_ok=True)
    shutil.copyfile( "./js/leaflet.css", folder_name + "js/leaflet.css" )
    shutil.copyfile( "./js/leaflet.js", folder_name + "js/leaflet.js" )
    
    # sets the max zoom and file extnesion values in the index
    template = open( "template.html", "r" )
    lines = template.readlines()
    tmp = []
    for line in lines:
        if "{{zoom}}" in line:
            line = line.replace( "{{zoom}}", str( levels ) )
        if "{{extension}}" in line:
            line = line.replace( "{{extension}}", extension  )
        tmp.append( line )
    index = open( folder_name + "index.html", "w" )
    index.writelines(tmp)
    index.close()

    # done



if __name__ == "__main__":

    main("Venus--Magellan_Composite.jpg", "tiles", {"format":"jpg", "quality":80} )
    
