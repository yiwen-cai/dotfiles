# Electron Download Mirror Configuration

## Problem

Hermes Desktop build fails at the `electron` package postinstall step with:

```
RequestError: socket hang up
```

or similar network timeout when downloading `electron-v*.zip` from GitHub releases.

## Verification

Test direct GitHub release access from terminal:

```bash
curl -I --max-time 20 \
  https://github.com/electron/electron/releases/download/v37.6.0/electron-v37.6.0-darwin-arm64.zip
```

Expected: `HTTP/2 302` or `HTTP/1.1 302` redirect to `release-assets.githubusercontent.com`.

If this times out, the terminal process is not routing through your proxy/TUN.

## Solutions

### 1. Use npmmirror (Recommended for CN)

```bash
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
hermes desktop
```

Or persist via npm config:
```bash
npm config set electron_mirror https://npmmirror.com/mirrors/electron/
```

### 2. Ensure TUN/Proxy Covers Terminal

If using a system TUN proxy, verify terminal traffic is captured. Some TUN modes only proxy browser traffic, not terminal `curl`/`npm`.

Check with:
```bash
curl -s https://api.ip.sb/geoip
```

### 3. Use HTTP_PROXY Environment Variable

```bash
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
hermes desktop
```

## Note on npm Registry vs Electron Mirror

- `npm config set registry` — controls npm package downloads (tarballs from registry)
- `ELECTRON_MIRROR` — controls Electron binary downloads (large zip files from GitHub releases)

These are independent. A working npm registry does not imply working Electron downloads.
