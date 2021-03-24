import os
print(os.getcwd())

import sys
sys.path.append('..')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import pickle
import numpy as np
from io import BytesIO

from learning import collaborativeIntelligence

__HOST = 'localhost'
__PORT = 9090

class CollaborativeIntelligenceHandler(object):
    def partition(self, init):
        print(init)
    def inference(self, np_bytes):
        #load_bytes = BytesIO(np_bytes)
        #loaded_np = np.load(load_bytes, allow_pickle=True)
        loaded_np = pickle.loads(np_bytes)
        print(loaded_np)
        return 619


if __name__ == '__main__':
    handler = CollaborativeIntelligenceHandler()

    processor = collaborativeIntelligence.Processor(handler)
    transport = TSocket.TServerSocket(__HOST, __PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    rpcServer = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print('Starting the rpc server at', __HOST,':', __PORT)
    rpcServer.serve()
