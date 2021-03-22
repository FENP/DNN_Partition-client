import ctypes
import os
import pickle
import sys

#os.chdir("./Desktop")

T = ctypes.cdll.LoadLibrary('./making_decision.so')
csv = ctypes.c_char_p(bytes("./gpu.csv", 'utf-8'))
dag = ctypes.c_char_p(bytes("./dag", 'utf-8'))
T.init_dag(csv, dag)
T.make_partition(ctypes.c_float(3))
print(T.getStatus(b"features.1"))
print(T.getStatus(b"features.2"))
print(T.getStatus(b"classifier.1"))
T.display()