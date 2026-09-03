#!/usr/bin/env python3
"""Generate images via the Pollinations keyless endpoint.

Prints one JSON object per line to stdout: {"ok": bool, "path": str, ...}
so the caller can pick up the saved file paths without parsing prose.
"""

import argparse
import json
import re
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "https://image.pollinations.ai/prompt/"
DEFAULT_OUT = Path.home() / "Pictures" / "pollinations"

# Pollinations throttles anonymous traffic by holding the connection open
# rather than returning 429, so a slow response is normal, not a hang.
# Measured: ~5s for the first image, ~45s when requests queue up.
TIMEOUT = 180


def actual_size(data):
    """Real pixel dimensions of the returned image.

    Pollinations often ignores the requested width/height and serves something
    smaller, so reporting what we asked for would be a lie.
    """
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", data[16:24])
            return f"{w}x{h}"
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return f"{w}x{h}"
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    except (struct.error, IndexError):
        pass
    return "unknown"


def slug(text, limit=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:limit].rstrip("-")) or "image"


def build_url(prompt, args, seed):
    params = {"width": args.width, "height": args.height, "seed": seed}
    if args.model:
        params["model"] = args.model
    if args.nologo:
        params["nologo"] = "true"
    if args.enhance:
        params["enhance"] = "true"
    if args.private:
        params["private"] = "true"
    if args.image:
        params["image"] = args.image
    return BASE + urllib.parse.quote(prompt, safe="") + "?" + urllib.parse.urlencode(params)


def fetch(url, attempts=3):
    """Return (bytes, content_type). Retries transient failures with backoff."""
    last = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read(), resp.headers.get("Content-Type", "")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last = exc
            code = getattr(exc, "code", None)
            # 4xx other than 429 means the request itself is wrong; retrying won't help.
            if code and code != 429 and 400 <= code < 500:
                break
            if attempt < attempts - 1:
                time.sleep(8 * (attempt + 1))
    raise RuntimeError(f"{type(last).__name__}: {last}")


def generate(prompt, args, seed, index, total):
    url = build_url(prompt, args, seed)
    try:
        data, ctype = fetch(url)
    except RuntimeError as exc:
        return {"ok": False, "prompt": prompt, "seed": seed, "error": str(exc), "url": url}

    # A short non-image body means the service returned an error page, not art.
    if not ctype.startswith("image/") or len(data) < 1024:
        return {
            "ok": False, "prompt": prompt, "seed": seed, "url": url,
            "error": f"expected an image, got {ctype or 'unknown'} ({len(data)} bytes)",
        }

    ext = "png" if "png" in ctype else "jpg"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{stamp}-{slug(prompt)}-{seed}.{ext}"
    path = args.out / name
    path.write_bytes(data)
    got = actual_size(data)
    result = {
        "ok": True, "path": str(path), "prompt": prompt, "seed": seed,
        "model": args.model or "default", "size": got,
        "requested_size": f"{args.width}x{args.height}", "bytes": len(data), "url": url,
    }
    if got not in ("unknown", result["requested_size"]):
        result["note"] = "service ignored the requested size"
    return result


def main():
    p = argparse.ArgumentParser(description="Generate images with Pollinations (no API key).")
    p.add_argument("prompt", nargs="+", help="One or more prompts; each produces --n images.")
    p.add_argument("--n", type=int, default=1, help="Variants per prompt (default 1).")
    p.add_argument("--width", type=int, default=1024)
    p.add_argument("--height", type=int, default=1024)
    p.add_argument("--seed", type=int, help="Fixed seed. Variants increment from it.")
    p.add_argument("--model", help="e.g. flux, turbo. Omit to let the service choose.")
    p.add_argument("--image", help="Source image URL for image-to-image.")
    p.add_argument("--nologo", action="store_true", default=True)
    p.add_argument("--logo", dest="nologo", action="store_false", help="Keep the watermark.")
    p.add_argument("--enhance", action="store_true", help="Let the service expand the prompt.")
    p.add_argument("--private", action="store_true", help="Keep out of the public feed.")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    jobs = [(pr, (args.seed if args.seed is not None else int(time.time() * 1000) % 2**31) + i)
            for pr in args.prompt for i in range(args.n)]

    failures = 0
    for i, (prompt, seed) in enumerate(jobs):
        result = generate(prompt, args, seed, i, len(jobs))
        failures += not result["ok"]
        print(json.dumps(result, ensure_ascii=False), flush=True)

    return 1 if failures == len(jobs) else 0


if __name__ == "__main__":
    sys.exit(main())
