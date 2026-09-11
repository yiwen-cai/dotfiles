# Himalaya Proxy & Network Troubleshooting

## Symptom: TLS handshake EOF / Connection reset on mail ports

When a system-wide TUN proxy (Clash Verge, Mihomo, Surge, etc.) is active, TLS handshakes to IMAP 993 / SMTP 465·587 may fail with:

```
tls handshake eof
Connection reset by peer (os error 54)
invalid peer certificate: Other(OtherError("invalid2.invalid"))
```

TCP connects succeed (`nc -zv imap.gmail.com 993`), but TLS negotiation breaks immediately.

## Root cause

TUN stacks (especially gvisor) sometimes intercept or mishandle TLS handshakes on non-HTTP ports. The proxy's own mixed-port (e.g. 7897) may also be affected for those same ports once TUN is enabled, even though 443 works fine.

## Diagnostic checklist

1. **Verify proxy itself works for 443**
   ```bash
   curl -x socks5h://127.0.0.1:7897 https://www.google.com
   ```
   If this fails, the proxy node is down — fix that first.

2. **Verify direct (TUN) TLS fails**
   ```bash
   openssl s_client -connect imap.gmail.com:993 -servername imap.gmail.com </dev/null
   ```
   Expect `write:errno=54` or `no peer certificate` when TUN is the culprit.

3. **Verify proxy TLS for the same port**
   ```bash
   openssl s_client -connect imap.gmail.com:993 -servername imap.gmail.com -proxy 127.0.0.1:7897 </dev/null
   ```
   - If this **succeeds** → Himalaya can't natively use the proxy; use a local forwarder (see Workaround A).
   - If this **also fails** → TUN is interfering with the proxy's outbound 993 too; need a different bypass (see Workaround B).

## Workaround A: Local HTTP-CONNECT forwarder (preferred when proxy 443 OK, 993 broken via TUN)

Use the `scripts/http-connect-forward.py` helper. It listens on a local privileged port and tunnels through the HTTP CONNECT proxy.

```bash
# IMAP
sudo ~/.local/bin/http-connect-forward -p 993 -t imap.gmail.com -P 993
# SMTP (SMTPS)
sudo ~/.local/bin/http-connect-forward -p 465 -t smtp.gmail.com -P 465
```

Then edit `/etc/hosts`:
```
127.0.0.1 imap.gmail.com
127.0.0.1 smtp.gmail.com
```

And keep Himalaya config pointing to the real host/port:
```toml
backend.host = "imap.gmail.com"
backend.port = 993
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 465
```

Himalaya's rustls SNI will be `imap.gmail.com` (correct), but the TCP connection lands on the local forwarder, which tunnels through the working HTTP CONNECT proxy.

> ⚠️ `/etc/hosts` changes affect all applications. Remove the entries when done, or use a dedicated local DNS resolver like `dnsmasq` for selective overrides.

## Workaround B: Disable TUN, use System Proxy only

In Clash Verge / Mihomo:
- Turn off **TUN Mode**
- Keep **System Proxy** enabled

Then explicitly proxy mail traffic from a purpose-built script rather than relying on macOS system proxy inheritance. IMAP/SMTP libraries and many CLI tools do **not** automatically honor system proxy settings; use an HTTP CONNECT or SOCKS-aware client.

For Gmail sending, copy/adapt `scripts/gmail-send.py` to `~/.local/bin/gmail-send` and verify first:

```bash
~/.local/bin/gmail-send --check
~/.local/bin/gmail-send --to user@example.com --subject "test" --body "hello"
```

Default assumptions in the helper:
- Gmail app password is available from `pass show email/gmail`
- Clash/Mihomo mixed-port is `127.0.0.1:7897`
- SMTP uses SMTPS `smtp.gmail.com:465`

If `--check` reports `UNEXPECTED_EOF_WHILE_READING`, TUN may still be enabled or the selected proxy node is blocking mail ports; switch TUN off and/or try another node.

## Workaround C: proxychains-ng (Linux only; macOS arm64e caveat)

On macOS, Homebrew's `proxychains-ng` dylib is `arm64`, but system binaries are often `arm64e`. `dyld` refuses to inject the dylib:

```
dyld: terminating because inserted dylib '…libproxychains4.dylib' could not be loaded:
  mach-o file, but is an incompatible architecture (have 'arm64', need 'arm64e')
```

**Do not rely on proxychains-ng on Apple Silicon macOS** unless you rebuild it with matching architecture or use a Rosetta x86_64 binary chain.

## Workaround D: SOCKS5 forwarder (when HTTP CONNECT unavailable)

If the proxy only exposes SOCKS5 (no HTTP CONNECT), use `scripts/socks5-forward.py` instead. Same setup, different tunnel protocol.

```bash
sudo ~/.local/bin/socks5-forward -p 993 -t imap.gmail.com -P 993
```

## Pitfalls

- **Privileged ports (<1024)** require `sudo` on macOS/Linux. Non-privileged ports + `/etc/hosts` don't work because the port is part of the application config, not DNS.
- **Certificate SNI mismatch**: If Himalaya connects to `127.0.0.1:10993`, rustls sends SNI `127.0.0.1`. Gmail returns a cert for `imap.gmail.com` → verification fails with `invalid2.invalid`. Always ensure the Himalaya `backend.host` matches the certificate CN, or use `/etc/hosts` so the hostname resolves to localhost.
- **Duplicate emails risk**: On Gmail, if `folder.aliases.sent` is wrong, `himalaya message send` fails *after* SMTP delivery. Retrying re-sends the email. Always set `folder.aliases.sent = "[Gmail]/Sent Mail"`.
