#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys
from typing import Optional


class ChatServer:
    """멀티스레드 TCP/IP 채팅 서버 (브로드캐스트 + 귓속말)."""

    def __init__(self, host: str = '0.0.0.0', port: int = 5000) -> None:
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: dict[socket.socket, str] = {}          # sock -> username
        self.user_socks: dict[str, socket.socket] = {}       # username -> sock
        self.clients_lock = threading.Lock()
        self.alive = False

    def start(self) -> None:
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()
        self.alive = True
        print(f'서버가 시작되었습니다. {self.host}:{self.port}')

        try:
            while self.alive:
                client_sock, addr = self.server_sock.accept()
                client_sock.settimeout(None)
                threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, addr),
                    daemon=True
                ).start()
        finally:
            self.stop()

    def stop(self) -> None:
        self.alive = False
        with self.clients_lock:
            for sock in list(self.clients.keys()):
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()
            self.clients.clear()
            self.user_socks.clear()
        try:
            self.server_sock.close()
        except OSError:
            pass
        print('서버가 종료되었습니다.')

    def _handle_client(self, client_sock: socket.socket, addr: tuple) -> None:
        try:
            # 사용자명 요청 및 검증
            self._send_line(client_sock, '사용자명을 입력하세요: ')
            username = self._recv_line(client_sock)
            if username is None:
                client_sock.close()
                return
            username = username.strip()

            if not username:
                self._send_line(client_sock, '유효하지 않은 사용자명입니다. 연결을 종료합니다.')
                client_sock.close()
                return

            with self.clients_lock:
                if username in self.user_socks:
                    self._send_line(client_sock, '이미 사용 중인 사용자명입니다. 연결을 종료합니다.')
                    client_sock.close()
                    return
                self.clients[client_sock] = username
                self.user_socks[username] = client_sock

            # 입장 안내
            self._broadcast(f'{username}님이 입장하셨습니다.', sender=None)
            self._send_line(
                client_sock,
                '채팅에 참여하였습니다. 종료: /종료, 귓속말: /w 대상 내용 또는 /귓 대상 내용'
            )

            # 메시지 루프
            while True:
                line = self._recv_line(client_sock)
                if line is None:
                    break

                text = line.rstrip('\n')
                if text == '/종료':
                    self._send_line(client_sock, '연결을 종료합니다. 안녕히 가세요.')
                    break

                # 귓속말 명령 처리: /w 대상 내용  또는  /귓 대상 내용
                if text.startswith('/w ') or text.startswith('/귓 '):
                    self._handle_whisper(sender_sock=client_sock, raw=text)
                    continue

                if text.strip():
                    # 일반 메시지 브로드캐스트
                    self._broadcast(f'{username}> {text}', sender=client_sock)

        except ConnectionError:
            pass
        finally:
            self._cleanup_client(client_sock)

    def _handle_whisper(self, sender_sock: socket.socket, raw: str) -> None:
        """'/w 대상 내용' 또는 '/귓 대상 내용'을 파싱해 개인 메시지 전송."""
        sender_name = self._get_username(sender_sock)
        if sender_name is None:
            return

        # 접두사 제거
        if raw.startswith('/w '):
            payload = raw[3:]
        elif raw.startswith('/귓 '):
            payload = raw[3:]
        else:
            payload = raw

        # 대상과 본문 분리: 첫 토큰 = 대상, 나머지 = 메시지
        parts = payload.split(' ', 1)
        if len(parts) != 2:
            self._send_line(sender_sock, '형식: /w 대상 내용  또는  /귓 대상 내용')
            return

        target_name, message = parts[0].strip(), parts[1].strip()
        if not target_name or not message:
            self._send_line(sender_sock, '형식: /w 대상 내용  또는  /귓 대상 내용')
            return

        with self.clients_lock:
            target_sock = self.user_socks.get(target_name)

        if target_sock is None:
            self._send_line(sender_sock, f'대상 사용자를 찾을 수 없습니다: {target_name}')
            return

        # 수신자에게: "(귓속말) 보낸이> 내용"
        self._send_line(target_sock, f'(귓속말) {sender_name}> {message}')
        # 보낸이에게도 확인용 메시지 출력
        self._send_line(sender_sock, f'(귓속말 전송됨) {sender_name} → {target_name}: {message}')

    def _broadcast(self, message: str, sender: Optional[socket.socket]) -> None:
        data = (message + '\n').encode('utf-8', errors='ignore')
        to_remove = []
        with self.clients_lock:
            for sock in self.clients.keys():
                if sender is not None and sock is sender:
                    continue
                try:
                    sock.sendall(data)
                except OSError:
                    to_remove.append(sock)
            for sock in to_remove:
                name = self.clients.pop(sock, None)
                if name:
                    self.user_socks.pop(name, None)
                try:
                    sock.close()
                except OSError:
                    pass
                if name:
                    ghost = f'{name}님이 퇴장하셨습니다.'
                    ghost_data = (ghost + '\n').encode('utf-8', errors='ignore')
                    for other in self.clients.keys():
                        try:
                            other.sendall(ghost_data)
                        except OSError:
                            pass

    def _send_line(self, sock: socket.socket, text: str) -> None:
        data = (text + '\n').encode('utf-8', errors='ignore')
        try:
            sock.sendall(data)
        except OSError:
            pass

    def _recv_line(self, sock: socket.socket) -> Optional[str]:
        chunks = []
        try:
            while True:
                buf = sock.recv(1024)
                if not buf:
                    return None
                chunks.append(buf)
                if b'\n' in buf:
                    break
            raw = b''.join(chunks)
            line = raw.split(b'\n', 1)[0].decode('utf-8', errors='ignore')
            return line + '\n'
        except OSError:
            return None

    def _get_username(self, sock: socket.socket) -> Optional[str]:
        with self.clients_lock:
            return self.clients.get(sock)

    def _cleanup_client(self, client_sock: socket.socket) -> None:
        leaving_name = None
        with self.clients_lock:
            leaving_name = self.clients.pop(client_sock, None)
            if leaving_name:
                self.user_socks.pop(leaving_name, None)
        if leaving_name:
            self._broadcast(f'{leaving_name}님이 퇴장하셨습니다.', sender=None)
        try:
            client_sock.close()
        except OSError:
            pass


def main() -> None:
    # Allow port override via CLI: `python server.py 5001`
    start_port = 5000
    if len(sys.argv) >= 2:
        try:
            start_port = int(sys.argv[1])
        except ValueError:
            print(f'잘못된 포트값을 받았습니다: {sys.argv[1]}, 기본 {start_port} 사용')

    # Try a range of ports to avoid EADDRINUSE (useful on macOS where some services
    # may occupy port 5000). Tries start_port .. start_port+9.
    for port in range(start_port, start_port + 10):
        server = ChatServer(host='0.0.0.0', port=port)
        try:
            server.start()
            return
        except OSError as e:
            # errno differs by platform; inspect message for EADDRINUSE fallback
            msg = str(e)
            if 'Address already in use' in msg or getattr(e, 'errno', None) == 98 or getattr(e, 'errno', None) == 48:
                print(f'포트 {port} 사용 중, 다음 포트를 시도합니다...')
                continue
            else:
                raise
        except KeyboardInterrupt:
            print('\nKeyboardInterrupt 감지, 서버를 종료합니다.')
            server.stop()
            return


if __name__ == '__main__':
    main()
