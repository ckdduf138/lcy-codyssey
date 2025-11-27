#!/usr/bin/env python3

"""
send_mail.py

Send HTML emails to recipients specified in a CSV file.

Constraints:
- Python 3.x standard library only.
- CSV header: "이름,이메일" (Korean) or common English variants (Name, Email).
- Supports two modes: one email to many recipients (bulk), or one email per
  recipient (individual). Default is individual for better privacy/deliverability.
- Includes Naver SMTP support (smtp.naver.com:587) and a custom SMTP option.

Usage examples:
  Individual (recommended):
    python3 send_mail.py \
      --csv mail_target_list.csv \
      --subject 'From Mars: Status Update' \
      --html-file message.html \
      --provider naver \
      --username your_naver_id@naver.com \
      --sender your_naver_id@naver.com

  Bulk:
    python3 send_mail.py --csv mail_target_list.csv \
      --subject 'From Mars: Status Update' \
      --html-file message.html --mode bulk \
      --provider naver --username id@naver.com --sender id@naver.com

Credentials:
- Prefer environment variables for non-interactive use:
    export SMTP_USERNAME='id@naver.com'
    export SMTP_PASSWORD='app_password_or_password'
    export SMTP_SENDER='id@naver.com'
  CLI flags override env vars. If password is not provided, you'll be prompted.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import smtplib
import ssl
from getpass import getpass
from typing import Dict, Iterable, List, Optional, Tuple

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid


NAVER_SMTP_HOST = 'smtp.naver.com'
NAVER_SMTP_PORT = 587


def load_targets(csv_path: str) -> List[Tuple[str, str]]:
    """Load recipients from a CSV file.

    Accepts headers in Korean ('이름', '이메일') and common English variants
    ('name', 'email', 'e-mail', 'mail'). Ignores rows without a valid email.
    Reads with 'utf-8-sig' to handle BOM from spreadsheet tools.
    """
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError('CSV has no header row.')

        field_map: Dict[str, str] = {}
        for original in reader.fieldnames:
            key = (original or '').strip().lower()
            if key in ('이름', 'name'):
                field_map['name'] = original
            if key in ('이메일', 'email', 'e-mail', 'mail'):
                field_map['email'] = original

        if 'email' not in field_map:
            raise ValueError('CSV header must include 이메일 or Email column.')

        name_key = field_map.get('name')
        email_key = field_map['email']

        recipients: List[Tuple[str, str]] = []
        for row in reader:
            raw_email = (row.get(email_key) or '').strip()
            raw_name = (row.get(name_key) or '').strip() if name_key else ''
            if not raw_email:
                continue
            recipients.append((raw_name, raw_email))

        if not recipients:
            raise ValueError('No valid recipients found in CSV.')

        return recipients


def read_html_body(html_path: str) -> str:
    """Read HTML body from a file."""
    with open(html_path, 'r', encoding='utf-8') as html_file:
        return html_file.read()


def html_to_plaintext(html_content: str) -> str:
    """Create a basic plaintext fallback from HTML.

    This is a naive conversion suitable as an alternative MIME part.
    """
    text = re.sub(r'<\s*br\s*/?\s*>', '\n', html_content, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/?p\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def personalize_html(html_template: str, recipient_name: str) -> str:
    """Inject simple variables into the HTML template.

    Supported placeholders:
      {{name}} -> recipient's name (falls back to empty string)
    """
    safe_name = recipient_name or ''
    return html_template.replace('{{name}}', safe_name)


def build_message(
    subject: str,
    sender_email: str,
    to_header: str,
    html_content: str,
) -> MIMEMultipart:
    """Build a MIME message with plain and HTML alternatives."""
    message = MIMEMultipart('alternative')
    message['Subject'] = str(Header(subject, 'utf-8'))
    message['From'] = sender_email
    message['To'] = to_header
    message['Message-ID'] = make_msgid()

    plain = html_to_plaintext(html_content)
    part_text = MIMEText(plain, 'plain', 'utf-8')
    part_html = MIMEText(html_content, 'html', 'utf-8')
    message.attach(part_text)
    message.attach(part_html)
    return message


def open_smtp(provider: str, host: Optional[str], port: Optional[int]) -> smtplib.SMTP:
    """Open and return an authenticated SMTP connection (STARTTLS when applicable)."""
    if provider == 'naver':
        smtp_host = NAVER_SMTP_HOST
        smtp_port = NAVER_SMTP_PORT
    else:
        if not host or not port:
            raise ValueError('Custom provider requires --smtp-host and --smtp-port.')
        smtp_host = host
        smtp_port = int(port)

    server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
    server.ehlo()
    if smtp_port in (587, 25):
        context = ssl.create_default_context()
        server.starttls(context=context)
        server.ehlo()
    return server


def send_bulk(
    server: smtplib.SMTP,
    username: str,
    password: str,
    sender_email: str,
    recipients: List[Tuple[str, str]],
    subject: str,
    html_template: str,
) -> Tuple[int, int]:
    """Send a single email addressed to all recipients (visible in To header).

    Returns a tuple of (sent_count, failed_count).
    """
    server.login(username, password)

    to_addrs = [email for _, email in recipients]
    to_header = ', '.join(to_addrs)
    message = build_message(subject, sender_email, to_header, html_template)

    try:
        server.sendmail(sender_email, to_addrs, message.as_string())
        return len(to_addrs), 0
    except smtplib.SMTPException:
        return 0, len(to_addrs)


def send_individual(
    server: smtplib.SMTP,
    username: str,
    password: str,
    sender_email: str,
    recipients: List[Tuple[str, str]],
    subject: str,
    html_template: str,
) -> Tuple[int, int]:
    """Send one personalized email per recipient.

    Returns a tuple of (sent_count, failed_count).
    """
    server.login(username, password)

    sent = 0
    failed = 0
    for name, email_addr in recipients:
        personalized_html = personalize_html(html_template, name)
        to_header = formataddr((str(Header(name, 'utf-8')) if name else '', email_addr))
        message = build_message(subject, sender_email, to_header, personalized_html)

        try:
            server.sendmail(sender_email, [email_addr], message.as_string())
            sent += 1
        except smtplib.SMTPException:
            failed += 1

    return sent, failed


def resolve_credentials(
    username_arg: Optional[str],
    sender_arg: Optional[str],
    password_arg: Optional[str],
    prompt_if_missing: bool,
) -> Tuple[str, str, str]:
    """Resolve SMTP username, password, and sender email from args/env/prompt."""
    username = username_arg or os.environ.get('SMTP_USERNAME') or ''
    sender = sender_arg or os.environ.get('SMTP_SENDER') or username
    password = password_arg or os.environ.get('SMTP_PASSWORD') or ''

    if not username:
        raise ValueError('SMTP username is required (flag or SMTP_USERNAME env).')
    if not sender:
        raise ValueError('Sender email is required (flag or SMTP_SENDER env).')
    if not password and prompt_if_missing:
        password = getpass('SMTP password: ')
    if not password:
        raise ValueError('SMTP password is required (flag/env or prompt).')

    return username, password, sender


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Send HTML emails to recipients listed in a CSV file.'
    )
    parser.add_argument('--csv', required=True, help='Path to CSV file (utf-8).')
    parser.add_argument('--subject', required=True, help='Email subject.')
    parser.add_argument('--html-file', required=True, help='Path to HTML body.')
    parser.add_argument(
        '--mode', choices=('individual', 'bulk'), default='individual',
        help='Send one email per recipient (individual) or one to all (bulk).'
    )
    parser.add_argument(
        '--provider', choices=('naver', 'custom'), default='naver',
        help='SMTP provider. Use custom to specify host/port.'
    )
    parser.add_argument('--smtp-host', help='Custom SMTP host (with --provider custom).')
    parser.add_argument('--smtp-port', type=int, help='Custom SMTP port (with --provider custom).')
    parser.add_argument('--username', help='SMTP username (or env SMTP_USERNAME).')
    parser.add_argument('--sender', help='Sender email (or env SMTP_SENDER).')
    parser.add_argument('--password', help='SMTP password (or env SMTP_PASSWORD).')
    parser.add_argument(
        '--no-prompt', action='store_true',
        help='Do not prompt for password; require --password or env.'
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()

    recipients = load_targets(args.csv)
    html_template = read_html_body(args.html_file)

    username, password, sender_email = resolve_credentials(
        username_arg=args.username,
        sender_arg=args.sender,
        password_arg=args.password,
        prompt_if_missing=not args.no_prompt,
    )

    server = open_smtp(args.provider, args.smtp_host, args.smtp_port)
    try:
        if args.mode == 'bulk':
            sent, failed = send_bulk(
                server=server,
                username=username,
                password=password,
                sender_email=sender_email,
                recipients=recipients,
                subject=args.subject,
                html_template=html_template,
            )
        else:
            sent, failed = send_individual(
                server=server,
                username=username,
                password=password,
                sender_email=sender_email,
                recipients=recipients,
                subject=args.subject,
                html_template=html_template,
            )

        print(f'Sent: {sent}, Failed: {failed}')
    finally:
        try:
            server.quit()
        except Exception:
            pass


if __name__ == '__main__':
    main()


