from qoi_kod import *
from PIL import Image
import numpy as np

img = Image.open('./../images/bird.png') 

encoded = encode(img)
decoded = decode(encoded)
pixels, size, mode = decoded

img_qoi = create_image_from_pixels(pixels, size, mode)

print(np.array_equal(img, img_qoi))

