#!/usr/bin/env python3
"""
End-to-end test:
1. Bright Data scrape Zara dress + Steve Madden shoes
2. Extract product image, name, price
3. FASHN try-on: Zara dress → female standard model (category=one-pieces)
4. Print try-on result + buy links
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

ZARA_URL = "https://www.zara.com/us/en/short-crochet-dress-p05070144.html?v1=513128708"
HM_URL = "https://www.stevemadden.com/products/rocky-brown-distressed"

def scrape_product(url: str, brand: str) -> dict:
    """Scrape a product page via Bright Data and extract info."""
    print(f"\n{'='*60}")
    print(f"🔍 Scraping {brand}: {url}")
    
    if not config.brightdata_configured():
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
    else:
        html_text = scrape_html(url)
    
    product = first_product_for_query(html_text, brand=brand, search_url=url)
    
    info = {
        "name": product.name or "—",
        "price": product.price_display or "—",
        "image_url": (product.image_url or "").strip(),
        "url": product.url or url,
    }
    
    print(f"  📛 Name:  {info['name']}")
    print(f"  💰 Price: {info['price']}")
    print(f"  🖼️  Image: {info['image_url'][:100] if info['image_url'] else 'NONE'}...")
    print(f"  🔗 URL:   {info['url'][:80]}")
    
    return info


def test_tryon(garment_url: str, category: str = "one-pieces"):
    """Run FASHN try-on with the garment on female standard model."""
    print(f"\n{'='*60}")
    print(f"👗 FASHN Try-On")
    print(f"  Category: {category}")
    
    if not fashn_configured():
        print("  ❌ FASHN_API_KEY not set!")
        return None
    
    # Get model image
    model_img, label = model_image_for_tryon("女", "标准")
    print(f"  🧍 Model: {label}")
    print(f"  Model type: {'data-uri' if model_img.startswith('data:') else 'URL'} ({len(model_img)} chars)")
    
    # Convert garment to data-uri
    print(f"  🔄 Converting garment image to data-uri...")
    garment_data_uri = _garment_to_data_uri(garment_url)
    print(f"  Garment type: {'data-uri' if garment_data_uri.startswith('data:') else 'URL'} ({len(garment_data_uri)} chars)")
    
    # Call FASHN
    print(f"  ⏳ Calling FASHN try-on-v1.6...")
    try:
        urls = run_tryon_v16(
            model_img,
            garment_data_uri,
            category=category,
            garment_photo_type="auto",
            timeout=180.0,
        )
        if urls:
            print(f"  ✅ SUCCESS! Try-on result:")
            for i, u in enumerate(urls):
                print(f"     Output {i}: {u}")
            return urls[0]
        else:
            print(f"  ❌ No output URLs returned")
    except Exception as exc:
        print(f"  ❌ FASHN failed: {exc}")
    return None


def main():
    print("🚀 FitEntropy End-to-End Test")
    print(f"   Bright Data: {'✓' if config.brightdata_configured() else '—'}")
    print(f"   FASHN:       {'✓' if fashn_configured() else '—'}")
    
    # Step 1: Scrape Zara dress
    zara = scrape_product(ZARA_URL, "Zara")
    
    # Step 2: Scrape Steve Madden shoes
    shoes = scrape_product(HM_URL, "Steve Madden")
    
    # Step 3: FASHN try-on with Zara dress
    tryon_url = None
    if zara.get("image_url"):
        tryon_url = test_tryon(zara["image_url"], category="one-pieces")
    else:
        print("\n❌ No Zara garment image URL — cannot run try-on")
    
    # Step 4: Summary
    print(f"\n{'='*60}")
    print(f"📋 RESULT SUMMARY")
    print(f"{'='*60}")
    
    if tryon_url:
        print(f"\n✨ Try-on result image:")
        print(f"   {tryon_url}")
    
    print(f"\n🛍️ Shop Now:")
    if zara.get("name") != "—":
        print(f"   1. [{zara['name']}]({zara['url']})  —  {zara['price']}")
    else:
        print(f"   1. [Zara Short Crochet Dress]({ZARA_URL})")
    
    if shoes.get("name") != "—":
        print(f"   2. [{shoes['name']}]({shoes['url']})  —  {shoes['price']}")
    else:
        print(f"   2. [Steve Madden Rocky Brown Distressed]({HM_URL})")
    
    # Also show image URLs for verification
    print(f"\n🖼️ Product Images:")
    if zara.get("image_url"):
        print(f"   Zara: {zara['image_url'][:120]}...")
    if shoes.get("image_url"):
        print(f"   Steve Madden: {shoes['image_url'][:120]}...")


if __name__ == "__main__":
    main()
