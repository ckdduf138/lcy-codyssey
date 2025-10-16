#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
import getpass
from email.message import EmailMessage
from pathlib import Path
import mimetypes
import argparse

NAVER_SMTP_HOST = 'smtp.naver.com'
PORT_SSL = 465

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Naver SMTP로 메일을 보냅니다(표준 라이브러리만 사용).'
    )
    parser.add_argument('--from', dest='sender', required=True,
                        help='보내는 사람 Naver 이메일 주소')
    parser.add_argument('--to', dest='recipients', required=True, nargs='+',
                        help='받는 사람 이메일 주소(여러 명 가능)')
    parser.add_argument('--subject', required=True, help='메일 제목')
    parser.add_argument('--body', required=True, help='메일 본문 텍스트')
    parser.add_argument('--attach', nargs='*', default=[],
                        help='첨부 파일 경로(선택 사항)')
    return parser.parse_args()

def guess_mime_type(path: Path) -> tuple[str, str]:
    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        return 'application', 'octet-stream'
    main, sub = mime_type.split('/', 1)
    return main, sub

def build_message(sender: str,
                  recipients: list[str],
                  subject: str,
                  body: str,
                  attachments: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg.set_content(body)

    for file_path in attachments:
        path = Path(file_path).expanduser().resolve()
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f'첨부 파일을 찾을 수 없습니다: {path}')
        main, sub = guess_mime_type(path)
        with path.open('rb') as fp:
            data = fp.read()
        msg.add_attachment(data, maintype=main, subtype=sub, filename=path.name)

    return msg

def send_mail_naver(sender: str, password: str,
                    recipients: list[str], msg: EmailMessage) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(NAVER_SMTP_HOST, PORT_SSL, context=context, timeout=30) as smtp:
        # 네이버는 보통 이메일 전체 주소로 로그인
        smtp.login(sender, password)
        smtp.send_message(msg, from_addr=sender, to_addrs=recipients)

def main() -> None:
    args = parse_args()
    sender = args.sender
    recipients = args.recipients
    subject = args.subject
    body = args.body
    attachments = args.attach

    password = getpass.getpass('네이버 앱 비밀번호(메일/캘린더용 16자리)를 입력하세요: ')

    try:
        msg = build_message(sender, recipients, subject, body, attachments)
        send_mail_naver(sender, password, recipients, msg)
        print('메일 전송 완료!')

    except smtplib.SMTPAuthenticationError as e:
        print('인증 실패: 이메일 주소 또는 앱 비밀번호를 확인하세요.')
        print(f'상세: code={getattr(e, "smtp_code", None)}, msg={getattr(e, "smtp_error", None)}')
    except smtplib.SMTPResponseException as e:
        print(f'SMTP 오류: code={e.smtp_code}, msg={e.smtp_error}')
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f'오류 발생: {e}')

if __name__ == '__main__':
    main()
