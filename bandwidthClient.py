import iperf3

def measureBandWidth(server_hostname='127.0.0.1'):
    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = server_hostname
    client.port = 5201
    result = client.run()
    return result.sent_MB_s, result.received_MB_s

if __name__ == "__main__":
    BW = measureBandWidth('192.168.1.121')
    print("upload speed: " + str(BW[0]) + " MB/S")
    print("download speed: " + str(BW[1]) + " MB/S")