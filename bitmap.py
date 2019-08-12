#autor: Gerrit Jan Molenaar
#creation date: some time in the past(2019-08-06)
#breif:

import numpy as np
import pandas as pd
import math
from array import array
import logging


logger = logging.Logger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Bitmap():
    def __init__(self, file_dir):
        '''
            a bitmap image

            file_dir <-- dir and name of the bitmap file

            returns <-- Bitmap class object
        '''
        logger.info("creating bitmap")
        self.encoding = "utf-8"

        self.file_dir = file_dir
        try:
            self.file = open(self.file_dir, "r+b")
        except Exception as e:
            logger.error(e)

        self.headertypes = {"BITMAPCOREHEADER":12, "OS22XBITMAPHEADER":64,
                           "OS22XBITMAPHEADER":16, "BITMAPINFOHEADER":40,
                           "BITMAPV2INFOHEADER":52, "BITMAPV3INFOHEADER":56,
                           "BITMAPV4HEADER":108, "BITMAPV5HEADER": 124}

        self.signature = ""             # 2 bytes
        self.file_size = 0              # 4 bytes
        self.reserverd1 = ""            # 2 bytes
        self.reserverd2 = ""            # 2 bytes
        self.pixel_array_offset = 0     # 4 bytes
        self.info_header = 0            # 4 bytes
        self.width = 0                  # 2 or 4 bytes
        self.height = 0                 # 2 or 4 bytes
        self.color_planes = 0           # 2 bytes
        self.bpp = 0                    # 2 bytes
        self.compression = 0            # 4 bytes
        self.image_size = 0             # 4 bytes
        self.horizontal_resolution = 0  # 4 bytes
        self.vertical_resolution = 0    # 4 bytes
        self.color_pallet = 0           # 4 bytes
        self.important_colors = 0       # 4 bytes
        self.units = 0                  # 2 bytes
        self.reserved3 = 0              # 2 bytes
        self.recording = 0              # 2 bytes
        self.rendering = 0              # 2 bytes
        self.size1 = 0                  # 2 bytes
        self.size2 = 0                  # 4 bytes
        self.color_encoding = 0         # 4 bytes
        self.identifier = 0             # 4 bytes
        self.alpha_channel = 0          # 4 bytes
        self.color_space = 0            # 4 bytes
        self.color_space_endpoint = 0   # 36 bytes
        self.red_gamma = 0              # 4 bytes
        self.green_gamma = 0            # 4 bytes
        self.blue_gamma = 0             # 4 bytes
        self.red_channel = 0            # 4 bytes
        self.green_channel = 0          # 4 bytes
        self.blue_channel = 0           # 4 bytes
        self.ICC_color = 0              # 16 bytes

        self.array = None

        self.x = 0

        self.red_offset = 0
        self.green_offset = 0
        self.blue_offset = 0
        self.alpha_offset = 0
        self.x_offset = 0

        self.row_size = 0
        self.padding = 0

    def __del__(self):
        self.file.close()

    def __str__(self):
        return ("signature:            " + str(self.signature) + "\n"
        + "file size:            " + str(self.file_size) + "\n"
        +"reserverd 1:          " + str(self.reserverd1) + "\n"
        +"reserverd 2:          " + str(self.reserverd2) + "\n"
        +"pixel array offset:   " + str(self.pixel_array_offset) + "\n"
        +"info header:          " + str(self.info_header) + "\n"
        +"width:                " + str(self.width) + "\n"
        +"height:               " + str(self.height) + "\n"
        +"color planes:         " + str(self.color_planes) + "\n"
        +"bpp:                  " + str(self.bpp) + "\n"
        +"compression:          " + str(self.compression) + "\n"
        +"image size:           " + str(self.image_size) + "\n"
        +"horizontal resolution " + str(self.horizontal_resolution) + "\n"
        +"vertical resolution   " + str(self.vertical_resolution) + "\n"
        +"color pallet          " + str(self.color_pallet) + "\n"
        +"important colors      " + str(self.important_colors) + "\n"
        +"units:                " + str(self.units) + "\n"
        +"reserved3:            " + str(self.reserved3) + "\n"
        +"recording:            " + str(self.recording) + "\n"
        +"rendering:            " + str(self.rendering) + "\n"
        +"size1:                " + str(self.size1) + "\n"
        +"size2:                " + str(self.size2) + "\n"
        +"color encoding:       " + str(self.color_encoding) + "\n"
        +"identifier:           " + str(self.identifier) + "\n"
        +"alpha channel:        " + str(self.alpha_channel) + "\n"
        +"color space:          " + str(self.color_space) + "\n"
        +"color space endpoint: " + str(self.color_space_endpoint) + "\n"
        +"red gamma:            " + str(self.red_gamma) + "\n"
        +"green gamma:          " + str(self.green_gamma) + "\n"
        +"blue gamma:           " + str(self.blue_gamma) + "\n"
        +"red channel:          " + str(self.red_channel) + "\n"
        +"green channel:        " + str(self.green_channel) + "\n"
        +"blue channel:         " + str(self.blue_channel) + "\n"
        +"ICC color:            " + str(self.ICC_color) + "\n"
        +"red offset:           " + str(self.red_offset) + "\n"
        +"green offset:         " + str(self.green_offset) + "\n"
        +"blue offset:          " + str(self.blue_offset) + "\n"
        +"alpha offset:         " + str(self.alpha_offset) + "\n"
        +"x offset:             " + str(self.x_offset) + "\n"
        +"row size:             " + str(self.row_size) + "\n"
        +"padding:              " + str(self.padding) + "\n")

    def open_file(self, path,  method):
        '''
            opens the bitmap file (read or/and write)

            path = dir and name of file
            method <-- see open
            
        '''
        
        self.file.close()
        
        self.file_dir = path
        try:
            self.file = open(self.file_dir, method)
        except Exception as e:
            logger.error(e)

    def read(self, what=None):
        '''
            reads the file, if what is specifed it reads that part only
        '''
        logger.info(f"reading bitmap file, name: {self.file_dir}")
     
        if what == None:
            self.file.seek(0)
            self.header('read')
            self.information_header('read')
            self.pixel_array('read')

        elif what == "header":
            self.file.seek(0)
            self.header('read')

        elif what == "info":
            self.file.seek(14)
            self.information_header('read')

        elif what == "pixels":
            if self.info_header > 0:
                self.file.seek(14 + self.info_header)
                self.pixel_array('read')

            else:
                raise Exception("needs information header to read pixel array")
        else:
            raise Exception("invlaid what. (header, info, pixels)")
     
        logger.info(f"finished reading file")

    def header(self, rw):
        '''
            reads the bitmap header.

            rw <-- "read" or "write"

            -signature
            -file size
            -reserverd 1
            -reserverd 2
            -pixel array offset
        '''
        if rw == "read":
            logger.debug("reading header")
            # all bitmaps have this, first part of file
            self.signature = self.file.read(2).decode(self.encoding)
            self.file_size = int.from_bytes(self.file.read(4),"little")
            self.reserverd1 = self.file.read(2).decode(self.encoding)
            self.reserverd2 = self.file.read(2).decode(self.encoding)
            self.pixel_array_offset = int.from_bytes(self.file.read(4),"little")

        elif rw == "write":
            logger.debug("writing header")
            
            self.file.write(self.signature.encode(self.encoding))
            self.file.write(self.file_size.to_bytes(4,"little"))
            self.file.write(self.reserverd1.encode(self.encoding))
            self.file.write(self.reserverd2.encode(self.encoding))
            self.file.write(self.pixel_array_offset.to_bytes(4, "little"))
            
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")

    def information_header(self, rw):
        '''
            reads/writes the bitmap information header, and figure out
            wich infomration header to use

            rw <-- "read" or "write"

            -info header
        '''
        logger.debug("figure out which infoheader it is")
        # bitmap information header
        if rw == "read":
            self.info_header = int.from_bytes(self.file.read(4), "little")
        elif rw == "write":
            self.file.write(self.info_header.to_bytes(4, "little"))
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")

        if(self.info_header == 12):
            self.bitmapcoreheader(rw)

        elif(self.info_header == 16):
            self.bitmapinfoheader(rw)
            self.OS22xbitmapheader(rw)

        elif(self.info_header == 40):
            self.bitmapinfoheader(rw)

        elif(self.info_header == 52):
            self.bitmapinfoheader(rw)
            self.bitmapV2infoheader(rw)

        elif(self.info_header == 56):
            self.bitmapinfoheader(rw)
            self.bitmapV2infoheader(rw)
            self.bitmapV3infoheader(rw)

        elif(self.info_header == 64):
            self.bitmapinfoheader(rw)
            self.OS22xbitmapheader(rw)

        elif(self.info_header == 108):
            self.bitmapinfoheader(rw)
            self.bitmapV2infoheader(rw)
            self.bitmapV3infoheader(rw)
            self.bitmapV4infoheader(rw)

        elif(self.info_header == 124):
            self.bitmapinfoheader(rw)
            self.bitmapV2infoheader(rw)
            self.bitmapV3infoheader(rw)
            self.bitmapV4infoheader(rw)
            self.bitmapV5infoheader(rw)

        else:
            logger.error(f"this infoheader is not supported, {self.info_header}")
            raise Exception(f"this infoheader is not supported, {self.info_header}")


    def bitmapcoreheader(self, rw):
        '''

            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading V1 info header")
            #old version of V1 info header
            self.width = int.from_bytes(self.file.read(2),"little")
            self.height = int.from_bytes(self.file.read(2),"little")
            self.color_planes = int.from_bytes(self.file.read(2),"little")
            self.bpp = int.from_bytes(self.file.read(2),"little")
        elif rw == "write":
            logger.debug("writing V1 info header")
            self.file.write(self.width.to_bytes(2, "little"))
            self.file.write(self.height.to_bytes(2, "little"))
            self.file.write(self.color_planes.to_bytes(2, "little"))
            self.file.write(self.bpp.to_bytes(2, "little"))
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")


    def bitmapinfoheader(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading bitmap info header")
            # Version 1 info header all other versions add onto this

            self.width = int.from_bytes(self.file.read(4),"little")
            self.height = int.from_bytes(self.file.read(4),"little")
            self.color_planes = int.from_bytes(self.file.read(2),"little")
            self.bpp = int.from_bytes(self.file.read(2),"little")
            self.compression = int.from_bytes(self.file.read(4),"little")
            self.image_size = int.from_bytes(self.file.read(4),"little")
            self.horizontal_resolution = int.from_bytes(self.file.read(4),"little")
            self.vertical_resolution = int.from_bytes(self.file.read(4),"little")
            self.color_palette = int.from_bytes(self.file.read(4),"little")
            self.important_colors = int.from_bytes(self.file.read(4),"little")

        elif rw == "write":
            logger.debug("writing bitmap info header")
            self.file.write(self.width.to_bytes(4, "little"))
            self.file.write(self.height.to_bytes(4, "little"))
            self.file.write(self.color_planes.to_bytes(2, "little"))
            self.file.write(self.bpp.to_bytes(2, "little"))
            self.file.write(self.compression.to_bytes(4, "little"))
            self.file.write(self.image_size.to_bytes(4, "little"))
            self.file.write(self.horizontal_resolution.to_bytes(4, "little"))
            self.file.write(self.vertical_resolution.to_bytes(4, "little"))
            self.file.write(self.color_palette.to_bytes(4, "little"))
            self.file.write(self.important_colors.to_bytes(4, "little"))
            
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")



    def OS22xbitmapheader(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading OS22xbitmap")
            self.units = int.from_bytes(self.file.read(2),"little")
            self.reserved3 = int.from_bytes(self.file.read(2),"little")
            self.recording = int.from_bytes(self.file.read(2),"little")
            self.rendering = int.from_bytes(self.file.read(2),"little")
            self.Size1 = int.from_bytes(self.file.read(2),"little")
            self.Size2 = int.from_bytes(self.file.read(4),"little")
            self.color_encoding = int.from_bytes(self.file.read(4),"little")
            self.identifier = int.from_bytes(self.file.read(4),"little")
            
        elif rw == "write":
            logger.debug("writing OS22xbitmap")
            self.file.write(self.units.to_bytes(2, "little"))
            self.file.write(self.reserved3.to_bytes(2, "little"))
            self.file.write(self.recording.to_bytes(2, "little"))
            self.file.write(self.rendering.to_bytes(2, "little"))
            self.file.write(self.Size1.to_bytes(2, "little"))
            self.file.write(self.Size2.to_bytes(4, "little"))
            self.file.write(self.color_encoding.to_bytes(4, "little"))
            self.file.write(self.identifier.to_bytes(4, "little"))

        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")
            

    def bitmapV2infoheader(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading bitmap V2 header")
            # adds RGB bit mask
            self.red_channel = int.from_bytes(self.file.read(4),"little")
            self.green_channel = int.from_bytes(self.file.read(4),"little")
            self.blue_channel = int.from_bytes(self.file.read(4),"little")

        elif rw == "write":
            logger.debug("writing bitmap V2 header")
            self.file.write(self.red_channel.to_bytes(4, "little"))
            self.file.write(self.green_channel.to_bytes(4, "little"))
            self.file.write(self.blue_channel.to_bytes(4, "little"))

        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")

    def bitmapV3infoheader(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading bitmap V3 header")
            # adds alpha channel bit mask
            self.alpha_channel = int.from_bytes(self.file.read(4),"little")

        elif rw == "write":
            logger.debug("writing bitmap V3 header")
            self.file.write(self.alpha_channel.to_bytes(4, "little"))
            
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")
        

    def bitmapV4infoheader(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading bitmap V4 header")
            # adds colour space type and Gamma correction
            self.color_space = int.from_bytes(self.file.read(4),"little")
            self.color_space_endpoint = int.from_bytes(self.file.read(36),"little")
            self.red_gamma = int.from_bytes(self.file.read(4),"little")
            self.green_gamma = int.from_bytes(self.file.read(4),"little")
            self.blue_gamma = int.from_bytes(self.file.read(4),"little")

        elif rw == "write":
            logger.debug("writing bitmap V4 header")
            self.file.write(self.color_space.to_bytes(4, "little"))
            self.file.write(self.color_space_endpoint.to_bytes(36, "little"))
            self.file.write(self.red_gamma.to_bytes(4, "little"))
            self.file.write(self.green_gamma.to_bytes(4, "little"))
            self.file.write(self.blue_gamma.to_bytes(4, "little"))
            
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")

    def bitmapV5infoheader(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        if rw == "read":
            logger.debug("reading bitmap V5 header")
            # adds ICC colour profiles
            self.ICC_color = int.from_bytes(self.file.read(16),"little")

        elif rw == "write":
            logger.debug("reading bitmap V5 header")
            self.file.write(self.ICC_color.to_bytes(16, "little"))
            
        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")

    def pixel_array(self, rw):
        '''
            rw <-- "read" or "write"
        '''
        bytesPerPixel = self.bpp // 8

        if rw == "read":
            logger.debug("reading pixel Array")
            
            self.row_size = int(math.ceil(self.bpp * self.width / 32) * 4)
            self.padding = int(self.row_size - (bytesPerPixel * self.width))

            self.red_offset = math.ceil(math.log((pow(2, math.ceil(math.log(
                self.red_channel,2))) - self.red_channel), 2)) if self.red_channel > 0 else 0
            
            self.green_offset = math.ceil(math.log((pow(2, math.ceil(math.log(
                self.green_channel,2))) - self.green_channel), 2))if self.green_channel > 0 else 0
            
            self.blue_offset = math.ceil(math.log((pow(2, math.ceil(math.log(
                self.blue_channel,2))) - self.blue_channel), 2))if self.blue_channel > 0 else 0
            
            self.alpha_offset = math.ceil(math.log((pow(2, math.ceil(math.log(
                self.alpha_channel,2))) - self.alpha_channel), 2))if self.alpha_channel > 0 else 0
            
            self.x_offset = math.ceil(math.log((pow(2, math.ceil(math.log(
                self.x,2))) - self.x), 2))if self.x > 0 else 0
            
            self.array = np.empty(
                (self.height,(self.row_size - self.padding)//bytesPerPixel, 5),
                dtype=np.int32)
            
            self.x = ~ (self.red_channel |
                   self.green_channel |
                   self.blue_channel |
                   self.alpha_channel) # not used bits

            # reading the value

            channels = [self.red_channel,self.green_channel,self.blue_channel,self.alpha_channel,self.x]
            offsets =[self.red_offset,self.green_offset,self.blue_offset,self.alpha_offset,self.x_offset]

            try:
                for row in range(self.height):
                    for pixel in range(self.width):
                        if (row) * self.row_size - pixel > self.padding:
                            pixel_bytes = int.from_bytes(self.file.read(bytesPerPixel), "little")
                            for channel, offset, i in zip(channels, offsets, range(4)):
                                self.array[row][pixel][i] = (pixel_bytes & channel) >> offset
                        else:
                            # skiping padding
                            self.file.seek(1, 1)
            except Exception as e:
                logger.debug(f"row {row}")
                logger.debug(f"pixel {pixel}")
                logger.debug(f"i {i}")
                logger.debug(f"pixel_bytes {pixel_bytes}")
                logger.debug(f"channel {channel}")
                logger.debug(f"offset {offset}")

                logger.error(e)
                raise Exception(e)

        elif rw == "write":

            logger.debug("writing pixel Array")

            channels = [self.red_channel,self.green_channel,self.blue_channel,self.alpha_channel,self.x]
            offsets =[self.red_offset,self.green_offset,self.blue_offset,self.alpha_offset,self.x_offset]

            for row in range(self.height):
                for pixel in range(self.width):
                    if (row) * self.row_size - pixel > self.padding:
                        pixel_bytes = 0
                        for channel, offset, i in zip(channels, offsets, range(5)):
                            pixel_bytes += self.array[row][pixel][i] << offset

                        self.file.write(pixel_bytes.astype(np.int32))
                    else:
                        # skiping padding
                        self.file.write(b"0")
            

        else:
            logger.error("rw <-- not 'read' or 'write' ")
            raise Exception("rw <-- not 'read' or 'write' ")
        


    def write(self, what=None):
        '''
            saves the file, if what is specifed it saves that part only
        '''

        if what == None:
            self.header("write")
            self.information_header("write")
            self.pixel_array("write")

        elif what == "header":
            self.header("write")

        elif what == "info":
            self.information_header("write")

        elif what == "pixels":
            self.pixel_array("write")

        else:
                raise Exception("invlaid what. (header, info, pixels)")



if __name__ == "__main__":
    img = Bitmap("./nature32noicc.bmp")
    img.read()
    print(img)
    print(img.array[0][0])

    img.open_file("./test.bmp", "w+b")
    img.write()
    
    img2 = Bitmap("./test.bmp")
    img2.read()

    print(img2)
    print(img2.array[0][0])
    

    

