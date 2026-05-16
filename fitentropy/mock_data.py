"""Mock pipeline output for UI development without API keys."""

from __future__ import annotations

from fitentropy.models import MissingItemOffer, OutfitPlan, PipelineResult, ProductLink

# ── Female demo: Zara dress + Steve Madden boots ──
_ZARA_DRESS = ProductLink(
    brand="Zara",
    name="SHORT CROCHET DRESS",
    price_display="USD 79.9",
    url="https://www.zara.com/us/en/short-crochet-dress-p05070144.html?v1=513128708",
    image_url=(
        "https://static.zara.net/assets/public/93d9/7640/181c4d08b911/"
        "f586570d47cb/05070144250-p/05070144250-p.jpg?ts=1776843570400"
    ),
)
_STEVE_MADDEN_SHOES = ProductLink(
    brand="Steve Madden",
    name="ROCKY BROWN DISTRESSED",
    price_display="USD 159.95",
    url="https://www.stevemadden.com/products/rocky-brown-distressed",
    image_url=(
        "https://www.stevemadden.com/cdn/shop/files/"
        "STEVEMADDEN_SHOES_ROCKY_BROWN-DISTRESSED_01.jpg?v=1690565301&width=1920"
    ),
)
_ZARA_NECKLACE = ProductLink(
    brand="Zara",
    name="DOUBLE CORD CERAMIC PIECES NECKLACE",
    price_display="USD 39.9",
    url="https://www.zara.com/us/en/double-cord-ceramic-pieces-necklace-p01856117.html?v1=539570769&v2=2418989",
    image_url=(
        "https://static.zara.net/assets/public/13be/80dd/e38a41259411/"
        "d90298b0b820/01856117330-p/01856117330-p.jpg?ts=1773856412800"
    ),
)

# ── Male demo: Zara tee + Zara pants + Adidas Samba ──
_ZARA_TEE = ProductLink(
    brand="Zara",
    name="BASIC HEAVYWEIGHT T-SHIRT /03",
    price_display="USD 29.9",
    url="https://www.zara.com/us/en/basic-heavyweight-t-shirt--03-p01887410.html?v1=495703002",
    image_url=(
        "https://static.zara.net/assets/public/21b9/d278/0bcc488eb5fb/"
        "f199aca0fe61/01887410250-p/01887410250-p.jpg?ts=1767021854900"
    ),
)
_ZARA_PANTS = ProductLink(
    brand="Zara",
    name="SPLASH EFFECT FLARE FIT JEANS",
    price_display="USD 99.9",
    url="https://www.zara.com/us/en/splash-effect-flare-fit-jeans-p06688410.html?v1=523577070",
    image_url=(
        "https://static.zara.net/assets/public/3a83/0ddd/12c74beb88c7/"
        "f7474816835c/06688410708-p/06688410708-p.jpg?ts=1774528526000"
    ),
)
_ADIDAS_SAMBA = ProductLink(
    brand="Adidas",
    name="Samba OG Shoes",
    price_display="USD 100",
    url="https://www.adidas.com/us/samba-og-shoes/B75806.html",
    image_url=(
        "https://assets.adidas.com/images/w_600,f_auto,q_auto/"
        "3bbecbdf584e40398446a8bf0117cf62_9366/Samba_OG_Shoes_White_B75806_01_standard.jpg"
    ),
)

# FASHN try-on result URLs
_FEMALE_TRYON_URL = (
    "https://cdn.fashn.ai/019e32cc-acbf-7f80-a9e7-1ba9157b013b/output_0.jpeg"
)
# Female boots try-on (tryon-max — dress + boots)
_FEMALE_TRYON_BOOTS_URL = (
    "https://cdn.fashn.ai/019e32ed-86b3-7500-af3f-b9957d0b272d/try_on_0.jpeg"
)
# Female necklace try-on (tryon-max — dress + boots + necklace)
_FEMALE_TRYON_NECKLACE_URL = (
    "https://cdn.fashn.ai/019e32f0-4e58-7442-bb3e-c4cd3b1d431f/try_on_0.jpeg"
)
# Male layered: Step 1 (tee only) + Final (tee + pants)
_MALE_TRYON_STEP1_URL = (
    "https://cdn.fashn.ai/019e32d4-b61e-7461-b11a-336080bc8f26/output_0.jpeg"
)
_MALE_TRYON_FINAL_URL = (
    "https://cdn.fashn.ai/019e32d4-ebb6-7cd0-8f22-0a02f0fd516b/output_0.jpeg"
)
# Male shoes try-on (tryon-max)
_MALE_TRYON_SHOES_URL = (
    "https://cdn.fashn.ai/019e32e4-f61b-7771-a851-bf549a9880d8/try_on_0.jpeg"
)
# Male necklace try-on (tryon-max — Step 4)
_MALE_TRYON_NECKLACE_URL = (
    "https://cdn.fashn.ai/019e32ec-16a9-7a01-aa51-0342bbdbeeee/try_on_0.jpeg"
)


def mock_pipeline_result() -> PipelineResult:
    return PipelineResult(
        trend_keywords=[
            "quiet luxury",
            "crochet details",
            "distressed leather",
            "ballet flats comeback",
            "earthy tones",
        ],
        demo_mode=True,
        notes="Mock entropy reduction — connect API keys to run the live mesh.",
        memory_snippet="",
        actionbook_hints=[],
        outfits=[
            OutfitPlan(
                title="Resort Crochet",
                description=(
                    "Zara crochet mini dress paired with Steve Madden distressed brown boots, "
                    "effortlessly creating a resort-chic look that balances elegance and ease."
                ),
                trend_rationale=(
                    "Crochet details and distressed leather are trending for SS25; "
                    "the combination of texture contrast creates visual depth "
                    "while staying effortlessly chic."
                ),
                missing_labels=["Dresses:Crochet Mini Dress", "Shoes:Distressed Brown Boots", "Accessories:Ceramic Necklace"],
                offers=[
                    MissingItemOffer(
                        label="Dresses:Crochet Mini Dress",
                        product=_ZARA_DRESS,
                    ),
                    MissingItemOffer(
                        label="Shoes:Distressed Brown Boots",
                        product=_STEVE_MADDEN_SHOES,
                    ),
                    MissingItemOffer(
                        label="Accessories:Ceramic Necklace",
                        product=_ZARA_NECKLACE,
                    ),
                ],
            ),
            OutfitPlan(
                title="Urban Ease",
                description=(
                    "Crochet dress with minimal accessories and boots, "
                    "seamlessly transitioning from afternoon coffee to evening dates."
                ),
                trend_rationale=(
                    "Quiet luxury and relaxed tailoring dominate SS editorial boards; "
                    "the crochet dress anchors a low-effort, high-impact look."
                ),
                missing_labels=["Dresses:Crochet Mini Dress", "Accessories:Metallic Cuff"],
                offers=[
                    MissingItemOffer(
                        label="Dresses:Crochet Mini Dress",
                        product=_ZARA_DRESS,
                    ),
                    MissingItemOffer(
                        label="Accessories:Metallic Cuff",
                        product=ProductLink(
                            brand="Zara",
                            name="Metallic cuff bracelet",
                            price_display="USD 29.90",
                            url="https://www.zara.com/us/en/search?searchTerm=metallic+bracelet",
                        ),
                    ),
                ],
            ),
            OutfitPlan(
                title="Rock Edge",
                description=(
                    "Distressed brown boots + skinny jeans + leather jacket, "
                    "cool without trying too hard."
                ),
                trend_rationale=(
                    "Distressed leather and earthy tones dominate street moodboards; "
                    "the heavy-sole / light-top silhouette is trending on boards."
                ),
                missing_labels=["Shoes:Distressed Brown Boots", "Outerwear:Black Leather Jacket"],
                offers=[
                    MissingItemOffer(
                        label="Shoes:Distressed Brown Boots",
                        product=_STEVE_MADDEN_SHOES,
                    ),
                    MissingItemOffer(
                        label="Outerwear:Black Leather Jacket",
                        product=ProductLink(
                            brand="Zara",
                            name="FAUX LEATHER BIKER JACKET",
                            price_display="USD 99.90",
                            url="https://www.zara.com/us/en/search?searchTerm=leather+jacket",
                        ),
                    ),
                ],
            ),
        ],
    )


def mock_pipeline_male_result() -> PipelineResult:
    """Male date night demo with Zara tee + pants + Adidas Samba."""
    return PipelineResult(
        trend_keywords=[
            "relaxed tailoring",
            "vintage sport",
            "flare denim",
            "minimalist basics",
            "retro sneakers",
        ],
        demo_mode=True,
        notes="Mock male date outfit — connect API keys for live generation.",
        memory_snippet="",
        actionbook_hints=[],
        outfits=[
            OutfitPlan(
                title="Date Night Cool",
                description=(
                    "Zara heavyweight tee + splash-effect flare jeans + Adidas Samba, "
                    "effortless but not careless, perfect first impression for a date."
                ),
                trend_rationale=(
                    "Flare denim and retro sneakers are dominating SS25 street style; "
                    "the heavyweight tee adds structure while keeping it effortless. "
                    "Samba OGs are the 'it' shoe — seen on every fashion board."
                ),
                missing_labels=["Tops:Heavyweight T-Shirt", "Bottoms:Flare Jeans", "Shoes:Adidas Samba"],
                offers=[
                    MissingItemOffer(
                        label="Tops:Heavyweight T-Shirt",
                        product=_ZARA_TEE,
                    ),
                    MissingItemOffer(
                        label="Bottoms:Flare Jeans",
                        product=_ZARA_PANTS,
                    ),
                    MissingItemOffer(
                        label="Shoes:Adidas Samba",
                        product=_ADIDAS_SAMBA,
                    ),
                ],
            ),
            OutfitPlan(
                title="Weekend Stroll",
                description=(
                    "Same heavyweight tee paired with cargo pants and Samba, "
                    "laid-back style for weekend outings."
                ),
                trend_rationale=(
                    "Utility pants paired with retro sport shoes create a "
                    "scandinavian-clean aesthetic that's trending globally."
                ),
                missing_labels=["Tops:Heavyweight T-Shirt", "Bottoms:Cargo Pants", "Shoes:Adidas Samba"],
                offers=[
                    MissingItemOffer(
                        label="Tops:Heavyweight T-Shirt",
                        product=_ZARA_TEE,
                    ),
                    MissingItemOffer(
                        label="Bottoms:Cargo Pants",
                        product=ProductLink(
                            brand="Zara",
                            name="CARGO POCKET PANTS",
                            price_display="USD 49.90",
                            url="https://www.zara.com/us/en/search?searchTerm=cargo+pants",
                        ),
                    ),
                    MissingItemOffer(
                        label="Shoes:Adidas Samba",
                        product=_ADIDAS_SAMBA,
                    ),
                ],
            ),
            OutfitPlan(
                title="Minimal Gentleman",
                description=(
                    "Flare jeans paired with a shirt and derby shoes, "
                    "seamlessly switching from date dinner to business casual."
                ),
                trend_rationale=(
                    "Flare silhouettes meeting tailored elements is a key SS25 direction; "
                    "the jeans become the statement piece."
                ),
                missing_labels=["Bottoms:Flare Jeans", "Tops:White Shirt", "Shoes:Derby Shoes"],
                offers=[
                    MissingItemOffer(
                        label="Bottoms:Flare Jeans",
                        product=_ZARA_PANTS,
                    ),
                    MissingItemOffer(
                        label="Tops:White Shirt",
                        product=ProductLink(
                            brand="Zara",
                            name="OVERSIZED LINEN SHIRT",
                            price_display="USD 45.90",
                            url="https://www.zara.com/us/en/search?searchTerm=linen+shirt",
                        ),
                    ),
                    MissingItemOffer(
                        label="Shoes:Derby Shoes",
                        product=ProductLink(
                            brand="Zara",
                            name="LEATHER DERBY SHOES",
                            price_display="USD 79.90",
                            url="https://www.zara.com/us/en/search?searchTerm=derby+shoes",
                        ),
                    ),
                ],
            ),
        ],
    )


# Mock try-on results for demo mode
def mock_tryon_results() -> dict:
    """Return mock try-on results for female demo (dress + boots + necklace via tryon-max)."""
    return {
        1: {
            "tryon_url": _FEMALE_TRYON_NECKLACE_URL,
            "tryon_step1_url": _FEMALE_TRYON_URL,
            "tryon_shoes_url": _FEMALE_TRYON_BOOTS_URL,
            "tryon_necklace_url": _FEMALE_TRYON_NECKLACE_URL,
            "garment_url": _ZARA_DRESS.image_url,
            "category": "one-pieces+shoes+accessories",
            "label": "Dresses:Crochet Mini Dress + Shoes:Distressed Brown Boots + Accessories:Ceramic Necklace",
        },
    }


def mock_male_tryon_results() -> dict:
    """Return mock try-on results for male demo (layered: tee + pants + shoes via tryon-max)."""
    return {
        1: {
            "tryon_url": _MALE_TRYON_FINAL_URL,
            "tryon_step1_url": _MALE_TRYON_STEP1_URL,
            "tryon_shoes_url": _MALE_TRYON_SHOES_URL,
            "garment_url": _ZARA_TEE.image_url,
            "category": "tops+bottoms+shoes",
            "label": "Tops:Heavyweight T-Shirt + Bottoms:Flare Jeans + Shoes:Adidas Samba",
        },
    }
