#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KBS 헤드라인 + 날씨(RSS) 크롤러 (보너스 포함, 오류 수정판)
- BeautifulSoup에서 'xml' 파서가 없을 경우 html.parser로 자동 폴백
- .find_text 사용 제거 → 안전한 텍스트 추출 유틸 사용
"""

from __future__ import annotations

import sys
import time
from typing import List, Tuple
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


KBS_HOME = 'https://news.kbs.co.kr'
KMA_MID_RSS = 'https://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId={stn_id}'

DEFAULT_TIMEOUT = 8.0
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}


@dataclass
class FetchResult:
    url: str
    status: int
    elapsed: float
    text: str


def fetch_text(url: str) -> FetchResult:
    t0 = time.perf_counter()
    resp = requests.get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    elapsed = time.perf_counter() - t0
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return FetchResult(url=url, status=resp.status_code, elapsed=elapsed, text=resp.text)


def parse_kbs_headlines(html: str) -> List[str]:
    """KBS 메인 페이지 HTML에서 헤드라인 텍스트를 추출한다."""
    soup = BeautifulSoup(html, 'html.parser')

    candidates: List[str] = []

    # 구조 변화에 대비한 다중 셀렉터
    selectors = [
        'div#headline a, div#headline h3 a, div#headline h2 a',
        'div.news_list a.tit, ul.news-list a.tit, div.list a.tit',
        'a.card-tit, a.news-tit, h3.news-tit a',
        'section a[title], article a[title]',
        # 일반 기사 링크 중 제목 길이가 충분한 것
        'article a, li a, h3 a, h2 a'
    ]

    seen = set()
    for sel in selectors:
        for a in soup.select(sel):
            text = (a.get_text(strip=True) or '').strip()
            href = a.get('href') or ''
            # 제목 후보 필터링
            if len(text) < 6:
                continue
            # 외부 링크/앵커만인 경우 제외
            if href.startswith('#'):
                continue
            if text in seen:
                continue
            seen.add(text)
            candidates.append(text)
        if len(candidates) >= 15:
            break

    return candidates[:15]


def _soup(xml_text: str) -> BeautifulSoup:
    """가능하면 'xml' 파서를, 없으면 'html.parser'를 사용한다."""
    try:
        return BeautifulSoup(xml_text, 'xml')
    except Exception:
        return BeautifulSoup(xml_text, 'html.parser')


def _txt(tag) -> str:
    """None 안전 텍스트 추출."""
    return (tag.get_text(strip=True) if tag else '').strip()


def parse_kma_midterm(xml_text: str, max_locations: int = 3, per_location: int = 2) -> Tuple[str, List[Tuple[str, List[Tuple[str, str, str, str]]]]]:
    """기상청 중기예보 RSS(XML)에서 요약과 일부 지역의 예보를 추출한다.

    반환:
        (제목, [(도시, [(예보시각, 날씨, 최저, 최고), ...]) , ...])
    """
    soup = _soup(xml_text)

    channel_title = _txt(soup.find('title')) or '기상청 중기예보'
    summary = _txt(soup.find('wf'))  # 참고: 현재 출력은 요약하지 않음(필요시 사용)

    locations_out: List[Tuple[str, List[Tuple[str, str, str, str]]]] = []

    for loc in soup.find_all('location')[:max_locations]:
        city = _txt(loc.find('city'))
        if not city:
            continue
        data_rows: List[Tuple[str, str, str, str]] = []
        for d in loc.find_all('data')[:per_location]:
            tm = _txt(d.find('tmEf'))
            wf = _txt(d.find('wf'))
            tmn = _txt(d.find('tmn'))
            tmx = _txt(d.find('tmx'))
            if tm and wf:
                data_rows.append((tm, wf, tmn, tmx))
        if data_rows:
            locations_out.append((city, data_rows))

    return channel_title, locations_out


def print_weather_summary(title_line: str, locations: List[Tuple[str, List[Tuple[str, str, str, str]]]]) -> None:
    print(f'[{title_line}]')
    if not locations:
        print('(표시할 예보가 없습니다)')
        return
    for city, rows in locations:
        print(f'- {city}')
        for (tm, wf, tmn, tmx) in rows:
            tmin = f'{tmn}°C' if tmn else '-'
            tmax = f'{tmx}°C' if tmx else '-'
            print(f'  · {tm} | {wf} | 최저 {tmin} / 최고 {tmax}')


def main() -> None:
    # 1) KBS 헤드라인
    try:
        kbs = fetch_text(KBS_HOME)
    except requests.RequestException as exc:
        print('KBS 메인 페이지 요청 실패:', exc, file=sys.stderr)
        sys.exit(1)

    headlines = parse_kbs_headlines(kbs.text)
    print('[KBS 헤드라인] (총 {}건, {:.3f}s)'.format(len(headlines), kbs.elapsed))
    for i, title in enumerate(headlines, 1):
        print('{:02d}. {}'.format(i, title))

    print()

    # 2) 보너스: 기상청 중기예보 RSS (전국 108)
    try:
        rss = fetch_text(KMA_MID_RSS.format(stn_id='108'))
    except requests.RequestException as exc:
        print('기상청 중기예보 RSS 요청 실패:', exc, file=sys.stderr)
        return

    title_line, locations = parse_kma_midterm(rss.text, max_locations=3, per_location=2)
    print_weather_summary(title_line, locations)


if __name__ == '__main__':
    main()
