import socket
import threading
import pickle
import iperf3
import ctypes
import time

IP="127.0.0.1"
PORT=8081

def measureBandWidth(server_hostname='127.0.0.1'):
    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = server_hostname
    client.port = 5201
    result = client.run()
    return result.sent_MB_s

def readImage():
    return b'Hello World'

def sendData(client, inputData):
    # client.send(len(str).to_bytes(length=6, byteorder='big'))
	client.sendall(inputData)

def receiveData(client):
    data = client.recv(1024)
    end2 = time.time()
    print("data: " + str(data))
    print("total time: " + str(end2 - start))
    client.close()

if __name__ == "__main__":
    #D = ctypes.cdll.LoadLibrary('./test.so')
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

    image = readImage()
    start = time.time()
    BW = measureBandWidth()
    print("upload speed: " + str(BW) + " MB/S")
    end1 = time.time()
    print("measure time: " + str(end1 - start))
    sendData(client, image)

    t = threading.Thread(target=receiveData, name='receiveData', args=(client,))
    t.start()