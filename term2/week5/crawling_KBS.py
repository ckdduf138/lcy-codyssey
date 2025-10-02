#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawling_KBS.py

Assignment summary
------------------
- Visit Naver (https://www.naver.com) and check the difference between
  contents when logged in vs not logged in.
- Preselect content visible only after login (e.g., Naver Mail subjects).
- Install Selenium and a web driver to control a browser.
- Use Selenium to log in to Naver, then crawl the selected content.
- Store crawled items in list objects and print them.
- Save the final source code as crawling_KBS.py.

Environment & constraints
-------------------------
- Python 3.x.
- Follow PEP 8 (https://peps.python.org/pep-0008/).
- Use single quotes for strings by default. Use double quotes only when
  single quotes appear inside.
- Keep spaces around '=' in assignments like 'foo = (0,)'.
- Indentation uses spaces.
- Function names: lowercase with underscores.
- Class names: CapWords.
- Do not use third-party libraries *except* Selenium (explicitly required)
  and 'requests' if needed (allowed by the assignment). This script only
  uses Selenium.
- All code should run without warnings. (Network and site changes may
  still cause runtime exceptions; defensive error handling is included.)

Important notes
---------------
- Naver may apply additional security (captcha/2FA). If automated login
  is blocked, the script falls back to a 'manual-login' mode: it will
  pause on the login page and wait until you finish logging in yourself.
- For stable results, install a ChromeDriver version that matches your
  Chrome browser.
- This script was written to be robust against moderate DOM changes, but
  selectors may require updates if Naver changes its UI.

How to run
----------
1) Install Selenium (and a driver that matches your browser):
   - macOS / Linux (example with ChromeDriver on PATH):
       pip install selenium
       # Place chromedriver on PATH, or specify an absolute path below.
   - Windows (PowerShell):
       py -m pip install selenium
       # Place chromedriver.exe on PATH, or specify path below.

2) Run the script:
   python3 crawling_KBS.py
   # or on Windows
   py crawling_KBS.py

3) When prompted, choose 'auto' to attempt automated login with
   credentials, or 'manual' to log in yourself in the browser window.
   In manual mode, complete the login in the opened browser and the
   script will continue automatically when it detects that you're logged in.

What is crawled
---------------
- Public (not logged in): Top headlines (best-effort) on the main page.
- After login: Naver Mail inbox subjects (first ~20).

Output
------
- Two Python lists printed to stdout:
  - public_news
  - mail_subjects

Author: (your name here)
"""

from __future__ import annotations

import getpass
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


NAVER_HOME = 'https://www.naver.com/'
NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL = 'https://mail.naver.com/'


@dataclass
class CrawlResult:
    public_news: List[str]
    mail_subjects: List[str]


class NaverCrawler:
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)

    def open_home(self) -> None:
        self.driver.get(NAVER_HOME)

    def collect_public_news(self, max_items: int = 15) -> List[str]:
        """
        Best-effort extraction of public news-like headlines on the Naver home
        while not logged in. The DOM changes frequently; we try several fallbacks.
        """
        headlines = []
        self.open_home()
        time.sleep(1.2)

        # Strategy 1: Newsstand headlines block (common on Naver home)
        candidates = []
        try:
            # Try several likely containers
            possible_sections = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[id*="news"] , [class*="news"], section'
            )
            for sec in possible_sections:
                links = sec.find_elements(By.TAG_NAME, 'a')
                for a in links:
                    txt = (a.text or '').strip()
                    if 6 <= len(txt) <= 90 and '뉴스' not in txt and '구독' not in txt:
                        candidates.append(txt)
        except Exception:
            candidates = []

        # Strategy 2: General anchors in the main content area
        if not candidates:
            try:
                main = self.driver.find_element(By.TAG_NAME, 'main')
                links = main.find_elements(By.TAG_NAME, 'a')
                for a in links:
                    txt = (a.text or '').strip()
                    if 6 <= len(txt) <= 90:
                        candidates.append(txt)
            except Exception:
                pass

        # Deduplicate while preserving order
        seen = set()
        for t in candidates:
            if t in seen:
                continue
            seen.add(t)
            headlines.append(t)
            if len(headlines) >= max_items:
                break

        return headlines

    def _field(self, by: By, value: str) -> Optional[str]:
        try:
            el = self.driver.find_element(by, value)
            return el.get_attribute('value')
        except NoSuchElementException:
            return None

    def is_logged_in(self) -> bool:
        """
        Heuristic to detect login state:
        - presence of user/profile/menu elements,
        - visiting mail page without redirect to login.
        """
        try:
            # Quick check on home: presence of '메일' unread badge or profile area.
            self.driver.get(NAVER_HOME)
            time.sleep(0.8)
            page = self.driver.page_source
            if '메일' in page and ('안읽음' in page or '새 메일' in page):
                return True
        except Exception:
            pass

        # Stronger check: try open mail and see if it stays
        self.driver.get(NAVER_MAIL)
        time.sleep(1.5)
        return 'mail.naver.com' in self.driver.current_url and 'login' not in self.driver.current_url

    def manual_login(self) -> None:
        """
        Open login page and wait until user completes login manually.
        """
        self.driver.get(NAVER_LOGIN)
        print('[INFO] Please complete Naver login in the browser window...')
        for _ in range(60):
            if self.is_logged_in():
                print('[OK] Login detected.')
                return
            time.sleep(2)
        raise TimeoutException('Login not detected within time limit.')

    def auto_login(self, user_id: str, password: str) -> None:
        """
        Attempt automated login via the classic id/pw form.
        If captcha or additional verification appears, user must complete it manually.
        """
        self.driver.get(NAVER_LOGIN)
        try:
            id_box = self.wait.until(EC.presence_of_element_located((By.ID, 'id')))
        except TimeoutException as exc:
            raise TimeoutException('Could not find the ID input. UI may have changed.') from exc

        pw_box = self.driver.find_element(By.ID, 'pw')

        id_box.clear()
        id_box.send_keys(user_id)
        pw_box.clear()
        pw_box.send_keys(password)
        pw_box.send_keys(Keys.RETURN)

        # Wait for either mail page or home to load after login
        for _ in range(20):
            if self.is_logged_in():
                print('[OK] Login successful (detected).')
                return
            time.sleep(1.0)

        # If we reach here, require manual completion (captcha/2FA)
        print('[WARN] Automated login not confirmed. Complete any verification in the browser.')
        self.manual_login()

    def collect_mail_subjects(self, max_items: int = 20) -> List[str]:
        """
        Navigate to Naver Mail and collect subjects from the inbox list.
        Attempts multiple selectors for robustness.
        """
        subjects = []
        self.driver.get(NAVER_MAIL)

        # Wait for mailbox to render or for a recognizable element
        time.sleep(2.0)

        selector_candidates = [
            # Old/various UIs
            'strong.mail_title',
            'span.mail_title',
            'span.subject',
            'a.mail_title_link',
            'div.subject a',
            'div.mTitle a',
            'a[aria-label*="메일 제목"]',
        ]

        elements = []
        for sel in selector_candidates:
            try:
                found = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if found:
                    elements = found
                    break
            except Exception:
                continue

        # Fallback: any anchor cells within list rows
        if not elements:
            try:
                rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr, li')
                for row in rows:
                    links = row.find_elements(By.TAG_NAME, 'a')
                    for a in links:
                        t = (a.text or '').strip()
                        if 1 < len(t) <= 120 and not t.startswith('['):
                            elements.append(a)
                # Keep elements as-is; will trim below
            except Exception:
                elements = []

        for el in elements:
            txt = (el.text or '').strip()
            if txt and txt not in subjects:
                subjects.append(txt)
            if len(subjects) >= max_items:
                break

        return subjects


def build_chrome(headless: bool = False, driver_path: Optional[str] = None) -> webdriver.Chrome:
    """
    Initialize a Chrome WebDriver. If driver_path is None, Selenium will try to
    find 'chromedriver' on PATH.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1366,900')

    if driver_path:
        driver = webdriver.Chrome(driver_path, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    return driver


def main() -> None:
    print('=== Naver crawling assignment (Selenium) ===')
    print('Mode:')
    print("  - Type 'auto'   to try automated login with credentials.")
    print("  - Type 'manual' to log in yourself in the opened browser.")
    mode = input('Choose login mode [auto/manual] (default: manual): ').strip().lower() or 'manual'

    headless_input = input('Headless mode? [y/N]: ').strip().lower()
    headless = headless_input == 'y'

    driver = build_chrome(headless=headless)

    try:
        crawler = NaverCrawler(driver)

        # 1) Not logged in: collect public headlines
        crawler.open_home()
        public_news = crawler.collect_public_news(max_items=15)

        # 2) Login
        if mode == 'auto':
            user_id = input('Naver ID: ').strip()
            password = getpass.getpass('Naver Password (input hidden): ')
            crawler.auto_login(user_id=user_id, password=password)
        else:
            crawler.manual_login()

        # 3) After login: collect mail subjects
        mail_subjects = crawler.collect_mail_subjects(max_items=20)

        # 4) Print results
        result = CrawlResult(public_news=public_news, mail_subjects=mail_subjects)

        print('\n# public_news')
        print(result.public_news)

        print('\n# mail_subjects (login-only content)')
        print(result.mail_subjects)

    finally:
        # Give user a moment to see the browser if not headless
        if not headless:
            time.sleep(2.0)
        driver.quit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted by user.', file=sys.stderr)
        sys.exit(130)
