import sys
import os
import time
import ctypes
import pickle
import logging
import torch

sys.path.append('..')
import pytorchtool

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from collections import defaultdict
from torchvision import models, transforms
from PIL import Image

from classes import class_names
from dnnpartition import collaborativeIntelligence

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def measureBandWidth():
    # 从trace文件中读取
    return 4.5

def startClient(host, port):
    tsocket = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(tsocket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = collaborativeIntelligence.Client(protocol)
    # 连接服务端
    transport.open()
    return transport, client

def closeClient(transport):
    transport.close()

def readImage(path_img):
    norm_mean = [0.485, 0.456, 0.406]
    norm_std = [0.229, 0.224, 0.225]
    inference_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(norm_mean, norm_std),
    ])

    # 转换为tensor
    img_tensor = inference_transform(Image.open(path_img).convert('RGB'))
    img_tensor.unsqueeze_(0)        # chw --> bchw
    
    return img_tensor

def getLayers(dag_path):
    # 通过读取dag文件获得模型各层名称
    layerState = defaultdict(int)
    for line in open(dag_path, 'r'):
        name = line.split(' ', 1)[0]
        layerState[name] = 0
    return layerState

def updateLayerState(T, layerState):
    # 根据切分结果更新层状态
    for key in layerState.keys():
        layerState[key] = T.getStatus(bytes(key, 'utf-8'))

class model:
    def __init__(self, model_name, use_gpu=False):
        self.model_name = model_name
        self.use_gpu = use_gpu

        if self.model_name in 'inception':
            self.model_name = 'inception'
            self.path = "../pytorchtool/model_weight/inception_v3/inception_v3_google-1a9a5a14.pth"

            model = models.Inception3(aux_logits=False, transform_input=False, 
                                    init_weights=False)
            model.eval()
            self.model = model
            self.depth = 2
        elif self.model_name in 'alexnet':
            self.model_name = 'alexnet'
            self.path = "../pytorchtool/model_weight/alexnet/alexnet-owt-4df8aa71.pth"
            
            model = models.alexnet(False)
            model.eval()
            self.model = model
            self.depth = -1 
        else:
            print("Wrong model name")

        if self.use_gpu:
            self.model = self.model.to(0)
    
    def setInput(self, path_img):
        self.x = readImage(path_img)
        if self.use_gpu:
            self.x = self.x.cuda()

    def inference(self):
        with torch.no_grad():
            outputs = self.model(self.x)    

    def loadWeight(self):
        state_dict_read = torch.load(self.path)

        self.model.load_state_dict(state_dict_read, strict=False)

    def getModel(self):
        return self.model
    
    def getInput(self):
        return self.x

def main():
    torch.randn(4).to(0)

    # 初始化模型
    name = "alex"
    m = model(name, use_gpu=False)
    m.loadWeight()

    # 先进行一次推理
    m.setInput('../pytorchtool/zebra.jpg')
    output = m.inference()

    # 切分模型
    cModel = pytorchtool.Surgery(m.model, 0, depth = m.depth)

    # 0: 本地执行; 1: 计算卸载 2: 边缘执行
    choice = 1
    csv_path = '../pytorchtool/parameters/' + m.model_name + '/cpu.csv'
    dag_path = '../pytorchtool/parameters/' + m.model_name + '/dag'
    layerState = getLayers(dag_path)

    T = ctypes.cdll.LoadLibrary('./partition/making_decision.so')
    csv = ctypes.c_char_p(bytes(csv_path, 'utf-8'))
    dag = ctypes.c_char_p(bytes(dag_path, 'utf-8'))
    T.init_dag(csv, dag)
    print("DAG初始化完成")

    # 连接服务端
    transport, client = startClient('192.168.1.121', 9090)

    for i in range(1, 20):
        print("**********第", str(i), "次推理**********")

        start = time.time()

        if choice != 1:
            if choice == 0:
                bandWidth = 0
            else:
                bandWidth = 10000
        else:
            bandWidth = measureBandWidth()
        # 读取数据
        start_data = time.time()
        m.setInput('../pytorchtool/zebra.jpg')
        print("读取数据用时", time.time() - start_data)
        print("网络带宽: " + str(bandWidth) + "MB/s")
        # 进行切分决策
        start_dec = time.time()
        T.make_partition(ctypes.c_float(bandWidth))
        print("切分决策用时", time.time() - start_dec)
        # 更新层状态
        updateLayerState(T, layerState)
        cModel.setLayerState(layerState)
        # print(layerState)
        # 传输层状态
        client.partition(layerState)
        # 本地执行
        start_in = time.time()
        output = cModel(m.x)
        middleResult = cModel.getMiddleResult()
        # print(middleResult)
        if not middleResult:  
            result = output
        else:   # 中间结果不为空才进行计算卸载
            # 传输中间结果获得推理结果
            middleResult = {k: pickle.dumps(v) for k, v in middleResult.items()}
            start_sin = time.time()
            result = pickle.loads(client.inference(middleResult))
            print("服务端时间", time.time() - start_sin)

        # 打印最终结果
        print("result: " + class_names[torch.argmax(result, 1)[0]])
        end = time.time()
        print("推理用时", end - start_in)
        print("总用时", end - start)


if __name__ == "__main__":
    logging.basicConfig(filename='./log',format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', 
        level = logging.DEBUG,filemode='a',datefmt='%Y-%m-%d%I:%M:%S %p')
    main()