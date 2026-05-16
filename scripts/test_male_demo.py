#!/usr/bin/env python3
"""
Male date demo:
1. Bright Data scrape: Zara tee + Zara pants + Adidas shoes
2. FASHN layered try-on: model + tee → + pants → final
3. Shoes: image + buy link only (FASHN doesn't support shoes)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fitentropy import config
from fitentropy.brightdata_client import scrape_html
from fitentropy.retail_parser import first_product_for_query
from fitentropy.mannequin_assets import model_image_for_tryon
from fitentropy.fashn_client import fashn_configured, run_tryon_v16
from fitentropy.tryon_service import _garment_to_data_uri

ZARA_TEE_URL = "https://www.zara.com/us/en/basic-heavyweight-t-shirt--03-p01887410.html?v1=495703002"
ZARA_PANTS_URL = "https://www.zara.com/us/en/splash-effect-flare-fit-jeans-p06688410.html?v1=523577070"
ADIDAS_SHOES_URL = "https://www.adidas.com/us/samba-og-shoes/B75806.html"


def scrape_product(url: str, brand: str) -> dict:
    """Scrape a product page and extract info."""
    print(f"\n🔍 Scraping {brand}: {url}")

    if config.brightdata_configured():
        html_text = scrape_html(url)
    else:
        print("  ⚠️  No BRIGHTDATA_API_KEY, trying direct fetch...")
        import requests
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0"
            })
            html_text = resp.text
        except Exception as e:
            print(f"  ❌ Direct fetch failed: {e}")
            return {}

    product = first_product_for_query(html_text, brand=brand, search_url=url)

    info = {
        "name": product.name or "—",
        "price": product.price_display or "—",
        "image_url": (product.image_url or "").strip(),
        "url": product.url or url,
    }

    print(f"  📛 Name:  {info['name']}")
    print(f"  💰 Price: {info['price']}")
    print(f"  🖼️  Image: {info['image_url'][:120] if info['image_url'] else 'NONE'}...")
    print(f"  🔗 URL:   {info['url'][:100]}")

    return info


def layered_tryon(model_img: str, tee_data_uri: str, pants_data_uri: str):
    """Layered FASHN try-on: Step 1 model+tee → Step 2 result+pants → final."""
    print(f"\n{'='*60}")
    print(f"👗 FASHN Layered Try-On (Male)")

    if not fashn_configured():
        print("  ❌ FASHN_API_KEY not set!")
        return None, None

    # Step 1: Model + T-shirt (category=tops)
    print(f"\n  Step 1: Model + T-shirt (category=tops)...")
    print(f"  ⏳ Calling FASHN try-on-v1.6...")
    try:
        tee_urls = run_tryon_v16(
            model_img,
            tee_data_uri,
            category="tops",
            garment_photo_type="auto",
            timeout=180.0,
        )
        if tee_urls:
            step1_url = tee_urls[0]
            print(f"  ✅ Step 1 done: {step1_url[:80]}...")
        else:
            print(f"  ❌ Step 1: No output URLs")
            return None, None
    except Exception as exc:
        print(f"  ❌ Step 1 failed: {exc}")
        return None, None

    # Step 2: Step1 result (model in tee) + Pants (category=bottoms)
    print(f"\n  Step 2: Model(in tee) + Pants (category=bottoms)...")
    # Convert step1 result to data-uri for the next call
    step1_data_uri = _garment_to_data_uri(step1_url)
    print(f"  Step1 model type: {'data-uri' if step1_data_uri.startswith('data:') else 'URL'} ({len(step1_data_uri)} chars)")

    try:
        final_urls = run_tryon_v16(
            step1_data_uri,
            pants_data_uri,
            category="bottoms",
            garment_photo_type="auto",
            timeout=180.0,
        )
        if final_urls:
            final_url = final_urls[0]
            print(f"  ✅ Step 2 done: {final_url[:80]}...")
            return step1_url, final_url
        else:
            print(f"  ❌ Step 2: No output URLs — returning Step 1 result")
            return step1_url, None
    except Exception as exc:
        print(f"  ❌ Step 2 failed: {exc} — returning Step 1 result")
        return step1_url, None


def main():
    print("🚀 FitEntropy Male Date Demo — E2E Test")
    print(f"   Bright Data: {'✓' if config.brightdata_configured() else '—'}")
    print(f"   FASHN:       {'✓' if fashn_configured() else '—'}")

    # Step 1: Scrape all 3 products
    tee = scrape_product(ZARA_TEE_URL, "Zara")
    pants = scrape_product(ZARA_PANTS_URL, "Zara")
    shoes = scrape_product(ADIDAS_SHOES_URL, "Adidas")

    # Step 2: Layered FASHN try-on
    step1_url = None
    final_url = None
    if tee.get("image_url") and pants.get("image_url"):
        model_img, label = model_image_for_tryon("男", "标准")
        print(f"\n  🧍 Model: {label}")

        print(f"\n  🔄 Converting T-shirt image to data-uri...")
        tee_data_uri = _garment_to_data_uri(tee["image_url"])
        print(f"  Tee: {'data-uri' if tee_data_uri.startswith('data:') else 'URL'} ({len(tee_data_uri)} chars)")

        print(f"  🔄 Converting pants image to data-uri...")
        pants_data_uri = _garment_to_data_uri(pants["image_url"])
        print(f"  Pants: {'data-uri' if pants_data_uri.startswith('data:') else 'URL'} ({len(pants_data_uri)} chars)")

        step1_url, final_url = layered_tryon(model_img, tee_data_uri, pants_data_uri)
    else:
        print("\n❌ Missing garment images — cannot run try-on")

    # Step 3: Summary
    print(f"\n{'='*60}")
    print(f"📋 RESULT SUMMARY")
    print(f"{'='*60}")

    best_url = final_url or step1_url
    if best_url:
        print(f"\n✨ Final try-on result:")
        print(f"   {best_url}")
    if step1_url and final_url:
        print(f"\n👕 Step 1 (tee only):")
        print(f"   {step1_url}")

    print(f"\n🛍️ Shop Now:")
    if tee.get("name") != "—":
        print(f"   1. [{tee['name']}]({tee['url']})  —  {tee['price']}")
    else:
        print(f"   1. [Zara Heavyweight Tee]({ZARA_TEE_URL})")

    if pants.get("name") != "—":
        print(f"   2. [{pants['name']}]({pants['url']})  —  {pants['price']}")
    else:
        print(f"   2. [Zara Flare Jeans]({ZARA_PANTS_URL})")

    if shoes.get("name") != "—":
        print(f"   3. [{shoes['name']}]({shoes['url']})  —  {shoes['price']}  👢 (no try-on)")
    else:
        print(f"   3. [Adidas Samba OG]({ADIDAS_SHOES_URL})  👢 (no try-on)")

    print(f"\n🖼️ Product Images:")
    if tee.get("image_url"):
        print(f"   Tee:   {tee['image_url'][:120]}...")
    if pants.get("image_url"):
        print(f"   Pants: {pants['image_url'][:120]}...")
    if shoes.get("image_url"):
        print(f"   Shoes: {shoes['image_url'][:120]}...")


if __name__ == "__main__":
    main()
