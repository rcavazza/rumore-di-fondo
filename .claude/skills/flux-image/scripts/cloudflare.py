#!/usr/bin/env python3
"""Generate images via Cloudflare Workers AI (FLUX and friends).

Same stdout contract as generate.py: one JSON object per line, so the caller
handles results identically no matter which backend produced them.

Credentials come from the environment and are never written to disk here:
    CLOUDFLARE_ACCOUNT_ID   32-char hex account id (visible in the dashboard URL)
    CLOUDFLARE_API_TOKEN    token with the Workers AI permission
"""

import argparse
import base64
import binascii
import json
import os
import re
import struct
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

API = "https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
DEFAULT_OUT = Path.home() / "Pictures" / "cloudflare-ai"
TIMEOUT = 180
CRLF = "\r\n"

# Each entry is (model path, request encoding). Workers AI is not uniform here
# and the published docs disagree with the live API, so these were probed
# directly: FLUX.2 rejects JSON and requires multipart form data, while
# FLUX.1 schnell takes JSON but 400s on any field beyond prompt/steps.
MODELS = {
    "flux-schnell":   ("@cf/black-forest-labs/flux-1-schnell", "json"),
    "flux2-klein-4b": ("@cf/black-forest-labs/flux-2-klein-4b", "multipart"),
    "flux2-klein-9b": ("@cf/black-forest-labs/flux-2-klein-9b", "multipart"),
    "flux2-dev":      ("@cf/black-forest-labs/flux-2-dev", "multipart"),
    "lucid-origin":   ("@cf/leonardo/lucid-origin", "json"),
    "phoenix":        ("@cf/leonardo/phoenix-1.0", "json"),
    "sdxl":           ("@cf/stabilityai/stable-diffusion-xl-base-1.0", "json"),
    "sdxl-lightning": ("@cf/bytedance/stable-diffusion-xl-lightning", "json"),
    "dreamshaper":    ("@cf/lykon/dreamshaper-8-lcm", "json"),
}

SCHNELL_FIELDS = {"prompt", "steps"}


def encode_multipart(fields):
    """Build form data by hand so the script stays dependency-free."""
    boundary = "----" + uuid.uuid4().hex
    parts = []
    for key, val in fields.items():
        parts.append("--" + boundary + CRLF)
        parts.append('Content-Disposition: form-data; name="' + key + '"' + CRLF + CRLF)
        parts.append(str(val) + CRLF)
    parts.append("--" + boundary + "--" + CRLF)
    return "".join(parts).encode(), "multipart/form-data; boundary=" + boundary


def slug(text, limit=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:limit].rstrip("-")) or "image"


def actual_size(data):
    """Real pixel dimensions, since a requested size is only ever a hint."""
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", data[16:24])
            return f"{w}x{h}"
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            if data[i + 1] in (0xC0, 0xC1, 0xC2, 0xC3):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return f"{w}x{h}"
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    except (struct.error, IndexError):
        pass
    return "unknown"


def credentials():
    """Return (account, token), or (None, None) if either is unset."""
    acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    return (acct, token) if acct and token else (None, None)


def fall_back_to_pollinations(args):
    """Run the keyless backend instead of dying on missing credentials.

    The caller asked for an image, not a configuration lecture. Producing a
    rougher one beats producing nothing, so long as we say which backend ran.
    """
    sibling = Path(__file__).with_name("generate.py")
    cmd = [sys.executable, str(sibling)] + list(args.prompt)
    if args.n and args.n > 1:
        cmd += ["--n", str(args.n)]
    if args.width:
        cmd += ["--width", str(args.width)]
    if args.height:
        cmd += ["--height", str(args.height)]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    print(json.dumps({
        "backend": "pollinations",
        "note": "CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN not set; "
                "used the keyless fallback, which is markedly lower quality",
    }), flush=True)
    return subprocess.call(cmd)


def call(acct, token, model, payload, encoding):
    """POST to Workers AI. Returns (bytes, source) or raises RuntimeError."""
    url = API.format(acct=acct, model=model)
    if encoding == "multipart":
        data, ctype = encode_multipart(payload)
    else:
        data, ctype = json.dumps(payload).encode(), "application/json"

    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": "Bearer " + token, "Content-Type": ctype},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read()
            got = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"{type(exc).__name__}: {exc}") from None

    # Some models stream raw image bytes, others wrap base64 in the standard
    # Cloudflare envelope. Handle both rather than guessing per model.
    if got.startswith("image/"):
        return body, "binary"

    try:
        doc = json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError(f"unexpected {got or 'unknown'} response ({len(body)} bytes)") from None

    if not doc.get("success", True):
        errs = "; ".join(str(e.get("message", e)) for e in doc.get("errors", [])) or "unknown error"
        raise RuntimeError("API error: " + errs)

    result = doc.get("result") or {}
    b64 = result.get("image") or (result.get("images") or [None])[0]
    if not b64:
        raise RuntimeError("no image in response: " + json.dumps(doc)[:300])
    try:
        return base64.b64decode(b64), "base64"
    except (binascii.Error, ValueError) as exc:
        raise RuntimeError(f"bad base64 payload: {exc}") from None


def main():
    p = argparse.ArgumentParser(description="Generate images with Cloudflare Workers AI.")
    p.add_argument("prompt", nargs="+")
    # klein-4b is the default because it is the only model whose free-tier budget
    # (~95 images/day) allows actual iteration. The better models cost 13-25x more
    # and run dry after a handful, so they are opt-in for a final render.
    p.add_argument("--model", default="flux2-klein-4b",
                   help="Alias (" + ", ".join(MODELS) + ") or a full @cf/... path.")
    p.add_argument("--encoding", choices=("json", "multipart"),
                   help="Override the request encoding for an unlisted model.")
    p.add_argument("--n", type=int, default=1, help="Variants per prompt.")
    p.add_argument("--steps", type=int, help="Diffusion steps. flux-schnell caps at 8.")
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--seed", type=int)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--list-models", action="store_true",
                   help="Query the available text-to-image models and exit.")
    args = p.parse_args()

    acct, token = credentials()
    if not acct:
        if args.list_models:
            sys.exit("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to list models.")
        return fall_back_to_pollinations(args)

    if args.list_models:
        url = ("https://api.cloudflare.com/client/v4/accounts/" + acct +
               "/ai/models/search?task=Text-to-Image&per_page=100")
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
        with urllib.request.urlopen(req, timeout=60) as resp:
            for m in json.loads(resp.read()).get("result", []):
                print(m.get("name", ""))
                print("    " + (m.get("description") or "").strip()[:110])
        return 0

    model, encoding = MODELS.get(args.model, (args.model, "json"))
    if args.encoding:
        encoding = args.encoding
    args.out.mkdir(parents=True, exist_ok=True)

    jobs = [(pr, i) for pr in args.prompt for i in range(args.n)]
    failures = 0

    for prompt, i in jobs:
        payload = {"prompt": prompt}
        for key, val in (("steps", args.steps), ("width", args.width),
                         ("height", args.height)):
            if val is not None:
                payload[key] = val
        if args.seed is not None:
            payload["seed"] = args.seed + i
        if "flux-1-schnell" in model:
            payload = {k: v for k, v in payload.items() if k in SCHNELL_FIELDS}

        try:
            data, source = call(acct, token, model, payload, encoding)
            if len(data) < 1024:
                raise RuntimeError(f"image too small to be real ({len(data)} bytes)")
        except RuntimeError as exc:
            failures += 1
            print(json.dumps({"ok": False, "prompt": prompt, "model": model,
                              "error": str(exc)}, ensure_ascii=False), flush=True)
            continue

        ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = args.out / f"{stamp}-{slug(prompt)}-{args.model}-{i}.{ext}"
        path.write_bytes(data)
        print(json.dumps({
            "ok": True, "path": str(path), "prompt": prompt, "model": model,
            "size": actual_size(data), "bytes": len(data), "encoding": source,
            "steps": payload.get("steps"),
        }, ensure_ascii=False), flush=True)

    return 1 if failures == len(jobs) else 0


if __name__ == "__main__":
    sys.exit(main())
