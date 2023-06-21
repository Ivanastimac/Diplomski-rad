import copy as cp
from PIL import Image
from collections import deque

QOI_OP_INDEX = 0x00  
QOI_OP_DIFF = 0x40  
QOI_OP_LUMA = 0x80 
QOI_OP_RUN = 0xc0  
QOI_OP_RGB = 0xfe  
QOI_OP_RGBA = 0xff  
QOI_MASK_2 = 0xc0  


QOI_MAGIC = ord('q') << 24 | ord('o') << 16 | ord('i') << 8 | ord('f')

class Pixel:
  def __init__(self, r=0, g=0, b=0, a=255):
    self.r = r
    self.g = g
    self.b = b
    self.a = a
    
  def __eq__(self, other): 
      if not isinstance(other, Pixel):
          return NotImplemented

      return self.r == other.r and self.g == other.g and \
          self.b == other.b and self.a == other.a
    
def hash_f(px):
    return (px.r * 3 + px.g * 5 + px.b * 7 + px.a * 11)

def write_32_bits(value, bytes_array):
    bytes_array.append((0xff000000 & value) >> 24)
    bytes_array.append((0x00ff0000 & value) >> 16)
    bytes_array.append((0x0000ff00 & value) >> 8)
    bytes_array.append((0x000000ff & value))
    
def read_32_bits(bytes_array):
    b1, b2, b3, b4 = bytes_array
    return b1 << 24 | b2 << 16 | b3 << 8 | b4


def encode(pixels):
    h = pixels.size[1]
    w = pixels.size[0]
    
    total_size = w * h
    run = 0
    index = [Pixel() for _ in range(64)]
    bytes_array = bytearray()
    
    write_32_bits(QOI_MAGIC, bytes_array)
    write_32_bits(w, bytes_array)
    write_32_bits(h, bytes_array)
    
    channels = 4 if pixels.mode == 'RGBA' else 3
    
    bytes_array.append(4) if channels == 4 else bytes_array.append(3)
    bytes_array.append(0)
    
    px_prev = Pixel()
    px = Pixel()
    
    for h_i in range(h):
        for w_i in range(w):    
            pixel = pixels.getpixel((w_i,h_i))
            px.r = pixel[0]
            px.g = pixel[1]
            px.b = pixel[2]
            
            if channels == 4: px.a = pixel[3]
            
            if px == px_prev:
                run += 1
                if run == 62 or w_i * h_i >= total_size:
                    bytes_array.append(QOI_OP_RUN | (run - 1))
                    run = 0
            else:
                if run > 0:
                    bytes_array.append(QOI_OP_RUN | (run - 1))
                    run = 0
                    
                index_pos = hash_f(px) % 64
                
                if (index[index_pos] == px):
                    bytes_array.append(QOI_OP_INDEX | index_pos)
                else:
                    index[index_pos] = cp.copy(px)
                    
                    if px.a == px_prev.a:
                        vr = px.r - px_prev.r
                        vg = px.g - px_prev.g
                        vb = px.b - px_prev.b
                        
                        vg_r = vr - vg
                        vg_b = vb - vg
    
                        if vr > -3 and vr < 2 and vg > -3 and vg < 2 and vb > -3 and vb < 2:
                            bytes_array.append(QOI_OP_DIFF | (vr + 2) << 4 | (vg + 2) << 2 | (vb + 2))
                        elif vg_r > -9 and vg_r < 8 and vg > -33 and vg < 32 and vg_b > -9 and vg_b < 8:
                            bytes_array.append(QOI_OP_LUMA | (vg + 32))
                            bytes_array.append((vg_r + 8) << 4 | (vg_b +  8))
                        else:
                            bytes_array.append(QOI_OP_RGB)
                            bytes_array.append(px.r)
                            bytes_array.append(px.g)
                            bytes_array.append(px.b)
                    else:
                        bytes_array.append(QOI_OP_RGBA)
                        bytes_array.append(px.r)
                        bytes_array.append(px.g)
                        bytes_array.append(px.b)
                        bytes_array.append(px.a)
                        
            px_prev = cp.copy(px)
    
    for i in range(7):
        bytes_array.append(0)
    bytes_array.append(1)
    
    return bytes_array 


def decode(bytes_array):
    run = 0
    index = [Pixel() for _ in range(64)]
    
    qoi_magic = read_32_bits(bytes_array[:4])
    del bytes_array[:4]
    w = read_32_bits(bytes_array[:4])
    del bytes_array[:4]
    h = read_32_bits(bytes_array[:4])
    del bytes_array[:4]
    channels = bytes_array.pop(0)
    colorspace = bytes_array.pop(0)
    
    px = Pixel()
    pixels = []
    
    bytes_array = deque(bytes_array)
    
    for i in range(0, w * h * channels, channels):
        if run > 0:
            run -= 1
        elif len(bytes_array) > 8:
            b1 = bytes_array.popleft()
            if b1 == QOI_OP_RGB:
                px.r = bytes_array.popleft()
                px.g = bytes_array.popleft()
                px.b = bytes_array.popleft()
            elif b1 == QOI_OP_RGBA:
                px.r = bytes_array.popleft()
                px.g = bytes_array.popleft()
                px.b = bytes_array.popleft()
                px.a = bytes_array.popleft()
            elif (b1 & QOI_MASK_2) == QOI_OP_INDEX:
                px = cp.copy(index[b1])
            elif (b1 & QOI_MASK_2) == QOI_OP_DIFF:
                px.r += ((b1 >> 4) & 0x03) - 2
                px.g += ((b1 >> 2) & 0x03) - 2
                px.b += (b1 & 0x03) - 2
            elif (b1 & QOI_MASK_2) == QOI_OP_LUMA:
                b2 = bytes_array.popleft()
                vg = (b1 & 0x3f) - 32
                px.r +=  vg - 8 + ((b2 >> 4) & 0x0f)
                px.g += vg
                px.b += vg - 8 + (b2 & 0x0f)
            elif (b1 & QOI_MASK_2) == QOI_OP_RUN:
                run = (b1 & 0x3f) 
            
        index[hash_f(px) % 64] = cp.copy(px)
            
        pixels.append(px.r)
        pixels.append(px.g)
        pixels.append(px.b)
        if channels == 4: pixels.append(px.a)
        
        
    mode = 'RGBA' if channels == 4 else 'RGB'
        
    return pixels, (w, h), mode

def create_image_from_pixels(decoded, size, mode):
    img_qoi = Image.new(mode, size)
    
    if mode == 'RGBA':
        for i in range(len(decoded) // 4):
            x = i % size[0]
            y = i // size[0]
            r, g, b, a = decoded[i*4:(i+1)*4]
            img_qoi.putpixel((x, y), (r, g, b, a))
    else:
        for i in range(len(decoded) // 3):
            x = i % size[0]
            y = i // size[0]
            r, g, b = decoded[i*3:(i+1)*3]
            img_qoi.putpixel((x, y), (r, g, b))
            
    return img_qoi