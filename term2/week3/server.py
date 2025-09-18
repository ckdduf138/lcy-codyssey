#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 HTTP 서버 구현 (과제용)
- 표준 라이브러리만 사용 (http.server, socketserver, urllib, json, datetime, os)
- 포트: 8080
- 클라이언트 접속 시 200 OK와 index.html 반환
- 서버 콘솔에 접속 시간과 클라이언트 IP 주소 출력
- 보너스: 클라이언트 IP 기반 지역 정보 조회 (외부 공개 API 사용, 실패해도 무시)
PEP 8 스타일 가이드를 준수하려고 노력했습니다.
문자열은 기본적으로 작은따옴표를 사용합니다.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import socket


INDEX_FILE_NAME = 'index.html'
HOST = '0.0.0.0'
PORT = 8080
ENABLE_GEO_LOOKUP = True  # 보너스 과제: IP → 위치 조회 (표준 라이브러리만 사용)


def ensure_index_file() -> None:
    """index.html 파일이 없으면 기본 예시 페이지를 생성합니다."""
    if os.path.exists(INDEX_FILE_NAME):
        return

    html = (
        '<!doctype html>'
        '<html lang="ko">'
        '<head>'
        '  <meta charset="utf-8">'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">'
        '  <title>우주 해적 소개</title>'
        '  <style>'
        '    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; '
        '           line-height: 1.6; padding: 2rem; max-width: 800px; margin: 0 auto; }'
        '    h1 { margin-bottom: .25rem; }'
        '    .sub { color: #666; margin-top: 0; }'
        '    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.25rem; }'
        '    code { background: #f3f4f6; padding: .15rem .35rem; border-radius: 6px; }'
        '  </style>'
        '</head>'
        '<body>'
        '  <h1>우주 해적 (Space Pirates)</h1>'
        '  <p class="sub">별과 별 사이를 누비는 전설의 약탈자들</p>'
        '  <div class="card">'
        '    <p>우주 해적은 항성계 간 항로를 따라가며 희귀 자원과 고급 테크를 노리는 집단을 말합니다. '
        '       이들은 은폐 필드, 저소음 추진기, 양자 통신 차단 장비 등 최첨단 장비를 사용하여 '
        '       상선과 연구 함선을 기습합니다.</p>'
        '    <ul>'
        '      <li><strong>주요 활동</strong>: 화물선 습격, 데이터 금고 탈취, 잔해 수거 및 암거래</li>'
        '      <li><strong>전술</strong>: 중력자 슬링샷을 활용한 급가속, 허위 조난 신호, 전자전(EW)</li>'
        '      <li><strong>선호 장비</strong>: 플라스마 커터, EMP 어레이, 자가 수복 드론</li>'
        '    </ul>'
        '    <p>하지만 모든 우주 해적이 악당은 아닙니다. 일부는 부패한 기업 카르텔에 맞서는 '
        '       의적 성향의 독립 세력으로 활동하기도 하죠.</p>'
        '  </div>'
        '  <p>이 페이지는 파이썬 표준 라이브러리 <code>http.server</code>로 제공됩니다.</p>'
        '</body>'
        '</html>'
    )

    with open(INDEX_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(html)


def geolocate_ip(ip: str) -> str:
    """외부 공개 API를 사용해 IP의 대략적 위치를 문자열로 반환합니다.
    실패하거나 사설망 IP인 경우 빈 문자열을 반환합니다.
    """
    # 사설망 대역은 조회하지 않습니다.
    private_prefixes = ('10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.2', '192.168.', '127.')
    if ip.startswith(private_prefixes):
        return ''

    try:
        # ip-api.com은 비인증 HTTP GET을 지원합니다(학습용 간단 API).
        url = f'http://ip-api.com/json/{ip}?fields=status,country,regionName,city,query'
        req = Request(url, headers={'User-Agent': 'python-stdlib-client'})
        with urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('status') == 'success':
            country = data.get('country') or ''
            region = data.get('regionName') or ''
            city = data.get('city') or ''
            parts = [p for p in (country, region, city) if p]
            return ' / '.join(parts)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, socket.timeout):
        return ''
    except Exception:
        # 예기치 못한 예외는 과제 목적상 조용히 무시합니다.
        return ''
    return ''


class SpacePirateHandler(BaseHTTPRequestHandler):
    """과제 요구사항에 맞춘 간단한 핸들러."""

    server_version = 'SpacePirateHTTP/1.0'

    def log_message(self, fmt: str, *args) -> None:
        """기본 noisy 로그를 억제하고, 과제 요구사항에 맞게 직접 출력합니다."""
        # 기본 구현은 무시합니다.
        return

    def _print_access_log(self) -> None:
        now = datetime.now().isoformat(timespec='seconds')
        client_ip = self.client_address[0]

        line = f'[접속] 시간={now}  IP={client_ip}'
        if ENABLE_GEO_LOOKUP:
            loc = geolocate_ip(client_ip)
            if loc:
                line += f'  위치={loc}'
        print(line, flush=True)

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler 요구 시그니처)
        """GET 요청 처리: / 또는 /index.html에 대해 페이지 반환."""
        self._print_access_log()

        if self.path in ('/', '/index.html'):
            # index.html 파일을 읽어 직접 전송
            try:
                with open(INDEX_FILE_NAME, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                # 파일이 없으면 500 에러
                msg = 'index.html not found on server.'
                body = msg.encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        else:
            # 기타 경로는 404
            msg = 'Not Found'
            body = msg.encode('utf-8')
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def run_server() -> None:
    """HTTP 서버를 시작합니다."""
    ensure_index_file()
    address = (HOST, PORT)
    with HTTPServer(address, SpacePirateHandler) as httpd:
        print(f'Serving on http://{HOST}:{PORT} ...', flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped by KeyboardInterrupt.', flush=True)


if __name__ == '__main__':
    run_server()
