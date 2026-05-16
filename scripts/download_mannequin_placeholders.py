#!/usr/bin/env python3
"""Download 6 demo mannequin JPEGs from built-in Unsplash URLs — no FASHN API Key."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import requests  # noqa: E402

from fitentropy.mannequin_assets import MANNEQUIN_DIR, all_presets, placeholder_url  # noqa: E402


def main() -> int:
    MANNEQUIN_DIR.mkdir(parents=True, exist_ok=True)
    from fitentropy.mannequin_assets import asset_basename

    for gender, body_type in all_presets():
        url = placeholder_url(gender, body_type)
        out = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.jpg"
        print(f"GET {out.name} …")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"  saved {len(r.content)} bytes → {out}")
    print("Done. Offline demo ready under assets/mannequins/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
