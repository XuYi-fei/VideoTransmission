import socket


def send_msg(client: socket.socket, msg: str, data_length=1024) -> str:
    client.sendall(bytes(msg.encode(encoding='utf-8')))
    return client.recv(data_length).decode(encoding='utf-8')


def send_msg_no_recv(client: socket.socket, msg: str, data_length=1024):
    client.sendall(bytes(msg.encode(encoding='utf-8')))


def send_bytes(client: socket.socket, msg: bytes, data_length=1024) -> str:
    client.sendall(msg)
    return client.recv(data_length).decode(encoding='utf-8')
