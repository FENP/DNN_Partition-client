import sys
sys.path.append('..')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from learning import collaborativeIntelligence

__HOST = 'localhost'
__PORT = 9090

tsocket = TSocket.TSocket(__HOST, __PORT)
transport = TTransport.TBufferedTransport(tsocket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = collaborativeIntelligence.Client(protocol)

# Connect!
transport.open()

print(client.inference({'layer1': 1, 'layer2': 2}))