#!/usr/bin/env python3
"""Generate 12-frame 360 mannequin assets via FASHN model-create (optional)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fitentropy.fashn_client import fashn_configured  # noqa: E402
from fitentropy.mannequin_assets import (  # noqa: E402
    MANNEQUIN_DIR,
    asset_basename,
    generate_mannequin_view_asset,
)

ANGLES = list(range(0, 360, 30))  # 12 frames: 0°, 30°, … 330°


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate 360 frame folder for one preset")
    parser.add_argument("--only", metavar="GENDER,BODY", required=True, help="e.g. 女,标准")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not fashn_configured():
        print("Set FASHN_API_KEY in .env first.", file=sys.stderr)
        return 1

    gender, body = [x.strip() for x in args.only.split(",", 1)]
    stem = asset_basename(gender, body)
    out_dir = MANNEQUIN_DIR / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    for deg in ANGLES:
        name = f"frame_{deg:03d}.jpg"
        path = out_dir / name
        if path.is_file() and not args.force:
            print(f"skip {name}")
            continue
        print(f"generating {name} …")
        # Reuse view generator with custom prompt via direct FASHN call would be better;
        # for now generate side/back/front variants in sequence.
        view = "front" if deg in (0, 330) else "side" if 60 <= deg <= 240 else "back"
        src = generate_mannequin_view_asset(gender, body, view, force=args.force)
        path.write_bytes(src.read_bytes())
        time.sleep(1)

    print(f"Done → {out_dir}/frame_*.jpg ({len(ANGLES)} frames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
