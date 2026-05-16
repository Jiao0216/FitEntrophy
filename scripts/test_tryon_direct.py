#!/usr/bin/env python3
"""Direct test of FASHN try-on: mannequin model + garment image → try-on result.

Bypasses the full pipeline (no LLM, no Bright Data scraping needed).
Uses local mannequin asset + a known garment image URL.
"""

import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fitentropy import config
from fitentropy.mannequin_assets import model_image_for_tryon, file_to_data_uri, resolve_asset_path
from fitentropy.tryon_service import _garment_to_data_uri


def test_tryon():
    # Check FASHN API key
    if not config.FASHN_API_KEY:
        print("ERROR: FASHN_API_KEY not set in .env")
        sys.exit(1)
    print(f"FASHN_API_KEY: {config.FASHN_API_KEY[:8]}...")

    # ── 1. Get model image (mannequin) ──
    gender = "女"
    body_type = "高挑"  # maps to "slim" → female_slim.png exists

    model_img, source_label = model_image_for_tryon(gender, body_type)
    print(f"\nModel image source: {source_label}")
    print(f"Model image type: {'data-uri' if model_img.startswith('data:') else 'URL'}")
    print(f"Model image length: {len(model_img)} chars")

    if not model_img:
        print("ERROR: No model image available!")
        sys.exit(1)

    # ── 2. Get garment image ──
    # Use a reliable Unsplash image of a garment (flat-lay top)
    garment_url = (
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c"
        "?auto=format&w=800&q=80"
    )
    print(f"\nGarment URL: {garment_url}")

    # Convert to data-uri (FASHN can't load most CDN URLs directly)
    print("Converting garment image to data-uri...")
    garment_data_uri = _garment_to_data_uri(garment_url)
    print(f"Garment image type: {'data-uri' if garment_data_uri.startswith('data:') else 'URL'}")
    print(f"Garment image length: {len(garment_data_uri)} chars")

    # ── 3. Call FASHN try-on ──
    from fitentropy.fashn_client import run_tryon_v16

    print("\nCalling FASHN try-on-v1.6...")
    print(f"  category: tops")
    print(f"  model: data-uri ({len(model_img)} chars)")
    print(f"  garment: data-uri ({len(garment_data_uri)} chars)")

    try:
        urls = run_tryon_v16(
            model_img,
            garment_data_uri,
            category="tops",
            garment_photo_type="auto",
            timeout=180.0,
        )
        if urls:
            print(f"\n✅ SUCCESS! Try-on result URL: {urls[0]}")
            if len(urls) > 1:
                for i, u in enumerate(urls[1:], 2):
                    print(f"  Extra output {i}: {u}")
        else:
            print("\n❌ FAILED: No output URLs returned")
    except Exception as exc:
        print(f"\n❌ FAILED with error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    test_tryon()
