from imagecodecs import (brotli_encode, brotli_decode)
from PIL import Image
import numpy as np
import sys
import time

img = Image.open('./../images/bird.png') 

old_stdout = sys.stdout
log_file = open(str('./results/bird/brotli_results_bird_test.txt'), 'w')
sys.stdout = log_file

print('Brotli encode')
begin = time.time()
encoded = brotli_encode(np.asarray(img))
end = time.time()

print('Vrijeme trajanje kodiranja slike: ' + str(end - begin) + '\n') 

print('Brotli decode')
begin = time.time()
decoded = brotli_decode(encoded)
end = time.time()

print('Vrijeme trajanja dekodiranja slike: ' + str(end - begin) + '\n')

data1 = bytearray(np.asarray(img))
print("Velicina originalne slike (asarray): %d" % sys.getsizeof(data1))

data2 = bytearray(np.asarray(encoded))
print("Velicina komprimirane slike (asarray): %d" % sys.getsizeof(data2))

data3 = bytearray(np.asarray(decoded))
print("Velicina rezultantne slike (asarray): %d\n" % sys.getsizeof(data3))

print("Postotak kompresije: %.2f\n" % ((1 - sys.getsizeof(data2)/sys.getsizeof(data1)) * 100)) 

