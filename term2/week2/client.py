#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys


def recv_loop(sock: socket.socket) -> None:
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            sys.stdout.write(data.decode('utf-8', errors='ignore'))
            sys.stdout.flush()
    except OSError:
        pass


def main() -> None:
    host = '127.0.0.1'
    port = 5000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        threading.Thread(target=recv_loop, args=(s,), daemon=True).start()

        for line in sys.stdin:
            s.sendall(line.encode('utf-8', errors='ignore'))


if __name__ == '__main__':
    main()
