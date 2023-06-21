from qoi_kod import *
from PIL import Image
import os.path as path
import time
import numpy as np
import sys

sys.path.append('.')
work_dir = ''

img = Image.open('./../images/bird.png') 
    
old_stdout = sys.stdout
log_file = open(str(work_dir + './results/bird/qoi_results_bird_1.txt'), 'w')
sys.stdout = log_file
    
print('QOI encode')
begin = time.time()
encoded = encode(img)
end = time.time()
    
print('Vrijeme trajanje kodiranja slike: ' + str(end - begin) + '\n')
    
with open(path.join(path.dirname(__file__), 'bird.qoi'), 'wb') as qoi:
    qoi.write(encoded)
    
data = bytearray(np.asarray(img))
print("Velicina originalne slike (asarray): %d" % sys.getsizeof(data))
print("Velicina kompresirane slike: %d" % sys.getsizeof(encoded))
print("Postotak kompresije: %.2f\n" % ((1 - sys.getsizeof(encoded)/sys.getsizeof(data)) * 100))  
    
print('QOI decode')
begin = time.time()
decoded = decode(encoded)
end = time.time()
    
print('Vrijeme trajanja dekodiranja slike: ' + str(end - begin) + '\n')
    
pixels, size, mode = decoded
    
img_qoi = create_image_from_pixels(pixels, size, mode)
data_qoi = bytearray(np.asarray(img_qoi))
print("Velicina rezultantne slike: %d" % sys.getsizeof(data_qoi))
img_qoi.save('bird_result.png')
    
sys.stdout = old_stdout
log_file.close()