import socket
from MySocket import MySocket
import sys
import threading

HOST = ''
PORT = 12345


class Client(MySocket):
    def __init__(self, ):
        super(Client, self).__init__()
        self.connect((HOST, PORT))

    def send_message(self, data='__join', new_port=None):
        self.send(data.encode('ascii'))
        self.listen_message()

    def listen_message(self):
        while True:
            d, addr = self.recvfrom(1024)
            if d or addr:
                self.user_id = int(d.decode('ascii'))
                print(f'user_id: {self.user_id}')
                print(f'd: {d}')
                print(f'server: {addr} has sent message, need send file to port: {self.user_id}')
                self.open_file(sys.argv[1])

    def open_file(self, file_name):
        with open(file_name, 'rb') as f:
            self.send_file(f)

    def send_file(self, f):
        self.new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.new_sock.connect((HOST, self.user_id))
        data = f.read(1024)
        while data:
            self.new_sock.sendto(data, (HOST, self.user_id))
            data = f.read(1024)
        self.new_sock.sendto('end of streaming'.encode('ascii'), (HOST, self.user_id))
        print('file was sent')


if __name__ == '__main__':
    udp_client = Client()
    threads = []
    funcs = [udp_client.listen_message, udp_client.send_message]
    for func in funcs:
        x = threading.Thread(target=func)
        x.start()
        threads.append(x)

    for t in threads:
        t.join()



