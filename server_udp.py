import tempfile
import socket
from MySocket import MySocket
import threading
from queue import Queue
import os
from time import sleep

HOST = ''
PORT = 12345


class Server(MySocket):
    def __init__(self, ):
        super(Server, self).__init__()
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((HOST, PORT))

    def listen_message(self):
        """Слушаем порт, ждем приветственное сообщение для установления соединения"""
        while True:
            print(f'server is listening init-msg on port {PORT}')
            d, addr = self.recvfrom(1024)
            if d or addr:
                user_id = addr
                print(f'user {user_id} have sent message: {d}')
                if d.decode() == '__join':
                    threading.Thread(target=self.open_new_socket, args=(user_id,)).start()

    def create_threads(self, port):
        """Создаем новые треды для получения данных и записи в файл"""
        threads = []
        q = Queue()
        event = threading.Event()
        file_name = tempfile.NamedTemporaryFile(suffix='_recv_audio.wav', dir=os.getcwd()).name
        funcs: list = [
            {'target': self.write_buffer, 'args': (q, event)},
            {'target': self.write_file, 'args': (file_name, q, event)}
        ]
        for func in funcs:
            x = threading.Thread(target=func['target'], args=(func['args']))
            x.start()
            threads.append(x)

        for t in threads:
            t.join()

    def open_new_socket(self, port):
        """Открываем новый сокет"""
        self.new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.new_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.new_sock.bind((HOST, 0))
        new_port = self.new_sock.getsockname()[1]
        print(f'Have opened new socket on port {new_port}')
        self.send_message(port, new_port)

    def send_message(self, data, new_port):
        """Отправляем клиенту номер порта, на котором будет приниматься файл"""
        self.sendto(str(new_port).encode('ascii'), data)
        self.create_threads(new_port)

    def write_buffer(self, q, event):
        """Пишем данные в буфер"""
        d, addr = self.new_sock.recvfrom(1024)
        while d:
            if d == b'end of streaming':
                print('end of streaming')
                event.set()
                return
            q.put(d)
            d, addr = self.new_sock.recvfrom(1024)

    def write_file(self, file_name, q, event):
        """Записываем из буфера в файл"""
        event.wait()
        with open(file_name, 'wb') as f:
            while not q.empty():
                f.write(q.get())
            print(f'File {file_name} downloaded')


if __name__ == "__main__":
    udp_serv = Server()
    udp_serv.listen_message()
