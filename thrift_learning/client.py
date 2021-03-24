import sys
sys.path.append('..')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import numpy as np
from io import BytesIO
import pickle

from learning import collaborativeIntelligence

__HOST = 'localhost'
__PORT = 9090

tsocket = TSocket.TSocket(__HOST, __PORT)
transport = TTransport.TBufferedTransport(tsocket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = collaborativeIntelligence.Client(protocol)

# Connect!

transport.open()

client.partition({'layer1': 1, 'layer2': 2})

x = np.array([[0, 1], [2, 3]])
#np_bytes = BytesIO()
#np.save(np_bytes, x, allow_pickle=True)
#client.inference(np_bytes.getvalue())
client.inference(pickle.dumps(x))

#print(sys.getsizeof(np_bytes.getvalue()))

#print(sys.getsizeof(pickle.dumps(x)))