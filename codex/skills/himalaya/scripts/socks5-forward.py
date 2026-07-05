#!/usr/bin/env python3
"""Local TCP port forwarder through SOCKS5 proxy (127.0.0.1:7897).

Usage:
    sudo ~/.local/bin/socks5-forward -p 993 -t imap.gmail.com -P 993
"""
import socket, threading, sys, argparse

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 7897


def socks5_connect(proxy_sock, target_host, target_port):
    """Negotiate SOCKS5 and connect to target through proxy_sock."""
    proxy_sock.sendall(b'\x05\x01\x00')
    resp = proxy_sock.recv(2)
    if resp != b'\x05\x00':
        raise RuntimeError(f'SOCKS5 greeting failed: {resp!r}')
    hb = target_host.encode()
    req = b'\x05\x01\x00\x03' + bytes([len(hb)]) + hb + target_port.to_bytes(2, 'big')
    proxy_sock.sendall(req)
    resp = proxy_sock.recv(10)
    if len(resp) < 2 or resp[1] != 0:
        raise RuntimeError(f'SOCKS5 connect failed: {resp!r}')
    return proxy_sock


def forward(local_conn, target_host, target_port):
    try:
        proxy_sock = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=20)
        remote_sock = socks5_connect(proxy_sock, target_host, target_port)
        remote_sock.settimeout(None)

        def relay(src, dst):
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except Exception:
                    pass

        t = threading.Thread(target=relay, args=(remote_sock, local_conn))
        t.start()
        relay(local_conn, remote_sock)
        t.join(timeout=5)
    except Exception as e:
        print(f'[{target_host}:{target_port}] forward error: {e}', file=sys.stderr)
    finally:
        local_conn.close()
        try:
            remote_sock.close()
        except Exception:
            pass


def serve(listen_host, listen_port, target_host, target_port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((listen_host, listen_port))
    srv.listen(128)
    print(f'Forwarding {listen_host}:{listen_port} -> {target_host}:{target_port} via SOCKS5 {PROXY_HOST}:{PROXY_PORT}')
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=forward, args=(conn, target_host, target_port), daemon=True).start()


def main():
    parser = argparse.ArgumentParser(description='TCP port forwarder through SOCKS5 proxy')
    parser.add_argument('-l', '--listen', default='127.0.0.1', help='local bind address')
    parser.add_argument('-p', '--port', type=int, required=True, help='local listen port')
    parser.add_argument('-t', '--target', required=True, help='target host')
    parser.add_argument('-P', '--target-port', type=int, required=True, help='target port')
    args = parser.parse_args()
    serve(args.listen, args.port, args.target, args.target_port)


if __name__ == '__main__':
    main()
