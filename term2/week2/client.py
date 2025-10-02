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
    port = 5004

    # If a port is provided, try it (with a few retries). Otherwise scan a small range and connect to the first open port.
    if len(sys.argv) >= 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f'잘못된 포트값을 받았습니다: {sys.argv[1]}, 자동 검색 모드로 전환')

    def try_connect(p: int, retries: int = 3, delay: float = 0.5):
        import time
        for attempt in range(retries):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((host, p))
                s.settimeout(None)
                return s
            except (ConnectionRefusedError, OSError):
                time.sleep(delay)
        return None

    s = None
    if port is not None:
        s = try_connect(port)
        if s is None:
            print(f'포트 {port}에 연결할 수 없습니다.')
            return
    else:
        # scan ports 5000..5010
        for p in range(5000, 5011):
            s = try_connect(p, retries=1)
            if s:
                port = p
                break
        if s is None:
            print('서버를 자동으로 찾을 수 없습니다 (스캔 5000-5010). 서버가 실행 중인지 확인하세요.')
            return

    # we already have an open socket 's' connected to (host, port)
    with s:
        print(f'서버({host}:{port})에 연결되었습니다. 사용자명을 입력하세요.')
        threading.Thread(target=recv_loop, args=(s,), daemon=True).start()

        try:
            for line in sys.stdin:
                s.sendall(line.encode('utf-8', errors='ignore'))
        except (BrokenPipeError, OSError):
            pass


if __name__ == '__main__':
    main()
