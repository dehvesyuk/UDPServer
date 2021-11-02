import socket


class MySocket(socket.socket):
    def __init__(self):
        super(MySocket, self).__init__(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

    def listen_message(self):
        raise NotImplementedError

    def send_message(self, data, new_port):
        raise NotImplementedError
