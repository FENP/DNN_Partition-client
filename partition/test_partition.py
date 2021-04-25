import ctypes
import os
import pickle
import sys
from collections import defaultdict

def getLayers(dag_path):
    # 通过读取dag文件获得模型各层名称
    layerState = defaultdict(int)
    for line in open(dag_path, 'r'):
        name = line.split(' ', 1)[0]
        layerState[name] = 0
    return layerState

def getLayerState(T, layerState):
    # 根据切分结果更新层状态并打印
    for key in layerState.keys():
        layerState[key] = T.getStatus(bytes(key, 'utf-8'))
        print(key, ": ", layerState[key])

T = ctypes.cdll.LoadLibrary('./making_decision.so')
csv = ctypes.c_char_p(bytes("../../pytorchtool/parameters/inception/cpu.csv", 'utf-8'))
dag = ctypes.c_char_p(bytes("../../pytorchtool/parameters/inception/dag", 'utf-8'))
T.init_dag(csv, dag)
T.make_partition(ctypes.c_float(4.8))
print(os.getcwd())
layerState = getLayers("../../pytorchtool/parameters/inception/dag")
getLayerState(T, layerState)
T.display()