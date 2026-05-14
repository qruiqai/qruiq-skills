#!/usr/bin/env python3
"""Generate an icon via OpenRouter's image-generation chat API.

Reads OPENROUTER_API_KEY from env. Writes a PNG to --output. Prints a JSON
summary on stdout so the caller can parse it.

If the primary model 404s (e.g. the user picked an ID that doesn't exist on
OpenRouter), this falls back to openai/gpt-image-1 and reports which model
actually produced the result via the `fallback_used` flag.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FALLBACK_MODEL = "openai/gpt-image-1"


def call_openrouter(api_key: str, model: str, prompt: str, timeout: int) -> dict:
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image"],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://claude.ai/code",
            "X-Title": "icon-generator skill",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_image_b64(payload: dict) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError(f"no choices in response: {payload}")
    message = choices[0].get("message") or {}
    images = message.get("images") or []
    if not images:
        raise RuntimeError(
            f"no images returned. message content: {message.get('content')!r}"
        )
    url = images[0].get("image_url", {}).get("url", "")
    m = re.match(r"^data:image/[^;]+;base64,(.+)$", url, re.DOTALL)
    if not m:
        raise RuntimeError(f"image_url is not a base64 data URI: {url[:80]}…")
    return m.group(1)


def is_model_not_found(err: urllib.error.HTTPError) -> bool:
    if err.code == 404:
        return True
    try:
        body = err.read().decode("utf-8", errors="replace")
    except Exception:
        return False
    return any(s in body.lower() for s in ("model not found", "no allowed providers", "no endpoints"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--output", required=True, help="Path to write PNG")
    ap.add_argument("--model", default="openai/gpt-5.4-image-2")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--no-fallback", action="store_true")
    args = ap.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": "OPENROUTER_API_KEY not set"}))
        return 2

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    model_used = args.model
    fallback_used = False
    try:
        payload = call_openrouter(api_key, args.model, args.prompt, args.timeout)
    except urllib.error.HTTPError as e:
        if not args.no_fallback and is_model_not_found(e) and args.model != FALLBACK_MODEL:
            model_used = FALLBACK_MODEL
            fallback_used = True
            payload = call_openrouter(api_key, FALLBACK_MODEL, args.prompt, args.timeout)
        else:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
            print(json.dumps({"error": f"HTTP {e.code}", "body": err_body}))
            return 1

    try:
        b64 = extract_image_b64(payload)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    out_path.write_bytes(base64.b64decode(b64))
    print(
        json.dumps(
            {
                "path": str(out_path),
                "model_requested": args.model,
                "model_used": model_used,
                "fallback_used": fallback_used,
                "bytes": out_path.stat().st_size,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
