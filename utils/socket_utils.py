import socket


def send_msg(client: socket.socket, msg: str, data_length=1024) -> str:
    client.sendall(bytes(msg.encode(encoding='utf-8')))
    return client.recv(data_length).decode(encoding='utf-8')