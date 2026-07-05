#!/usr/bin/env python3
"""Send Gmail through a local HTTP CONNECT proxy.

Class-level helper for cases where IMAP/SMTP CLI clients do not honor system proxy
or TUN mode breaks Gmail mail ports. Copy/adapt to ~/.local/bin/gmail-send.

Defaults assume Clash/Mihomo mixed-port on 127.0.0.1:7897 and a Gmail app
password stored at `pass show email/gmail`.
"""
from __future__ import annotations

import argparse
import mimetypes
import socket
import ssl
import subprocess
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable

DEFAULT_FROM = "drinklessmilktea@gmail.com"
DEFAULT_NAME = "Drink Less Milk Tea"
DEFAULT_PASSWORD_CMD = "pass show email/gmail"
DEFAULT_PROXY_HOST = "127.0.0.1"
DEFAULT_PROXY_PORT = 7897
DEFAULT_SMTP_HOST = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 465


def die(message: str, code: int = 1) -> None:
    print(f"gmail-send: error: {message}", file=sys.stderr)
    raise SystemExit(code)


def split_addresses(values: Iterable[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        result.extend(part.strip() for part in value.split(",") if part.strip())
    return result


def run_password_cmd(cmd: str) -> str:
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        die(f"password command failed: {cmd}" + (f": {detail}" if detail else ""))
    password = out.strip()
    if not password:
        die(f"password command returned empty output: {cmd}")
    return password


def http_connect(proxy_host: str, proxy_port: int, target_host: str, target_port: int, timeout: float) -> socket.socket:
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    request = (
        f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
        f"Host: {target_host}:{target_port}\r\n"
        "Proxy-Connection: Keep-Alive\r\n"
        "\r\n"
    ).encode("ascii")
    sock.sendall(request)
    data = b""
    while b"\r\n\r\n" not in data and len(data) < 65536:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    first_line = data.split(b"\r\n", 1)[0]
    if not first_line.startswith(b"HTTP/") or b" 200 " not in first_line:
        sock.close()
        die(f"HTTP CONNECT failed: {data.decode('utf-8', 'replace').strip()}")
    return sock


def build_message(args: argparse.Namespace) -> tuple[EmailMessage, list[str]]:
    to_addrs = split_addresses(args.to)
    cc_addrs = split_addresses(args.cc)
    bcc_addrs = split_addresses(args.bcc)
    recipients = to_addrs + cc_addrs + bcc_addrs
    if not recipients:
        die("at least one recipient is required: --to/--cc/--bcc")
    if not args.subject:
        die("subject is required: --subject")

    body_sources = [args.body is not None, args.body_file is not None, args.stdin]
    if sum(bool(x) for x in body_sources) > 1:
        die("use only one of --body, --body-file, or --stdin")
    if args.body_file:
        body = Path(args.body_file).read_text(encoding=args.encoding)
    elif args.stdin:
        body = sys.stdin.read()
    else:
        body = args.body or ""

    msg = EmailMessage()
    msg["From"] = f"{args.name} <{args.sender}>" if args.name else args.sender
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    if args.reply_to:
        msg["Reply-To"] = args.reply_to
    msg["Subject"] = args.subject
    msg.set_content(body)

    for attachment in args.attach or []:
        path = Path(attachment).expanduser()
        if not path.is_file():
            die(f"attachment not found or not a file: {attachment}")
        ctype, encoding = mimetypes.guess_type(str(path))
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
    return msg, recipients


def smtp_over_connected_ssl(raw_sock: socket.socket, host: str, timeout: float):
    import smtplib

    ctx = ssl.create_default_context()
    tls_sock = ctx.wrap_socket(raw_sock, server_hostname=host)
    tls_sock.settimeout(timeout)
    smtp = smtplib.SMTP_SSL(timeout=timeout)
    smtp.sock = tls_sock
    smtp.file = tls_sock.makefile("rb")
    code, msg = smtp.getreply()
    if code != 220:
        smtp.close()
        die(f"unexpected SMTP banner: {code} {msg!r}")
    return smtp


def check(args: argparse.Namespace) -> None:
    print(f"Checking proxy {args.proxy_host}:{args.proxy_port} -> {args.smtp_host}:{args.smtp_port} ...")
    raw = http_connect(args.proxy_host, args.proxy_port, args.smtp_host, args.smtp_port, args.timeout)
    ctx = ssl.create_default_context()
    try:
        tls_sock = ctx.wrap_socket(raw, server_hostname=args.smtp_host)
        print(f"TLS OK: {tls_sock.version()} / {tls_sock.cipher()[0]}")
        print(f"Certificate subject: {tls_sock.getpeercert().get('subject')}")
        tls_sock.close()
    except Exception as exc:
        die(f"TLS check failed: {exc}")


def send(args: argparse.Namespace) -> None:
    msg, recipients = build_message(args)
    password = args.password or run_password_cmd(args.password_cmd)
    raw = http_connect(args.proxy_host, args.proxy_port, args.smtp_host, args.smtp_port, args.timeout)
    smtp = smtp_over_connected_ssl(raw, args.smtp_host, args.timeout)
    try:
        smtp.ehlo()
        smtp.login(args.sender, password)
        smtp.send_message(msg, from_addr=args.sender, to_addrs=recipients)
    finally:
        try:
            smtp.quit()
        except Exception:
            smtp.close()
    print(f"Sent email to {', '.join(recipients)}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Send Gmail via local HTTP CONNECT proxy")
    p.add_argument("--to", action="append")
    p.add_argument("--cc", action="append")
    p.add_argument("--bcc", action="append")
    p.add_argument("--subject")
    p.add_argument("--body")
    p.add_argument("--body-file")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--attach", action="append")
    p.add_argument("--sender", default=DEFAULT_FROM)
    p.add_argument("--name", default=DEFAULT_NAME)
    p.add_argument("--reply-to")
    p.add_argument("--password-cmd", default=DEFAULT_PASSWORD_CMD)
    p.add_argument("--password")
    p.add_argument("--proxy-host", default=DEFAULT_PROXY_HOST)
    p.add_argument("--proxy-port", type=int, default=DEFAULT_PROXY_PORT)
    p.add_argument("--smtp-host", default=DEFAULT_SMTP_HOST)
    p.add_argument("--smtp-port", type=int, default=DEFAULT_SMTP_PORT)
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--check", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check:
        check(args)
    else:
        send(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
