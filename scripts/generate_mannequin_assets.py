#!/usr/bin/env python3
"""One-time: call FASHN model-create for 6 mannequin presets and save under assets/mannequins/."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fitentropy import config  # noqa: E402
from fitentropy.fashn_client import fashn_configured  # noqa: E402
from fitentropy.mannequin_assets import MANNEQUIN_DIR, all_presets, generate_mannequin_asset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate 6 static mannequin images via FASHN model-create")
    parser.add_argument("--only", metavar="GENDER,BODY", help="e.g. 女,高挑")
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--force", action="store_true", help="Regenerate even if file exists")
    args = parser.parse_args()

    if not fashn_configured():
        print("Set FASHN_API_KEY in .env first.", file=sys.stderr)
        return 1

    MANNEQUIN_DIR.mkdir(parents=True, exist_ok=True)

    targets = all_presets()
    if args.only:
        g, b = [x.strip() for x in args.only.split(",", 1)]
        targets = [(g, b)]

    for gender, body_type in targets:
        from fitentropy.mannequin_assets import asset_basename

        out = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.jpg"
        if out.is_file() and args.skip_existing and not args.force:
            print(f"skip (exists): {out.name}")
            continue

        print(f"generating {out.name} via FASHN model-create …")
        path = generate_mannequin_asset(gender, body_type, force=args.force)
        print(f"  saved: {path}")
        time.sleep(1)

    print("Done. Commit assets/mannequins/*.jpg for hackathon.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
