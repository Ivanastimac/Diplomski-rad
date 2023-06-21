from imagecodecs import (bz2_encode, bz2_decode)
from PIL import Image
import numpy as np
import sys
import time

img = Image.open('./../images/bird.png') 

old_stdout = sys.stdout
log_file = open(str('./results/bird/bz2_results_bird_test.txt'), 'w')
sys.stdout = log_file

print('bz2 encode')
begin = time.time()
polje = np.asarray(img)
encoded = bz2_encode(np.asarray(img))
end = time.time()

print('Vrijeme trajanje kodiranja slike: ' + str(end - begin) + '\n')

print('bz2 decode')
begin = time.time()
decoded = bz2_decode(encoded)
end = time.time()

print('Vrijeme trajanja dekodiranja slike: ' + str(end - begin) + '\n')

data1 = bytearray(np.asarray(img))
print("Velicina originalne slike (asarray): %d" % sys.getsizeof(data1))

data2 = bytearray(np.asarray(encoded))
print("Velicina komprimirane slike (asarray): %d" % sys.getsizeof(data2))

data3 = bytearray(np.asarray(decoded))
print("Velicina rezultantne slike (asarray): %d\n" % sys.getsizeof(data3))

print("Postotak kompresije: %.2f\n" % ((1 - sys.getsizeof(data2)/sys.getsizeof(data1)) * 100)) 
