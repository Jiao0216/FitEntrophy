"""Mock pipeline output for UI development without API keys."""

from __future__ import annotations

from fitentropy.models import MissingItemOffer, OutfitPlan, PipelineResult, ProductLink


def mock_pipeline_result() -> PipelineResult:
    return PipelineResult(
        trend_keywords=[
            "quiet luxury",
            "wide-leg tailoring",
            "metallic accents",
            "ballet flats comeback",
            "layered knits",
        ],
        demo_mode=True,
        notes="Mock entropy reduction — connect API keys to run the live mesh.",
        memory_snippet="",
        actionbook_hints=[],
        outfits=[
            OutfitPlan(
                title="Low-entropy commuter polish",
                description=(
                    "Structured blazer over a clean tee, wide-leg denim, and "
                    "minimal sneakers — sharp lines with soft texture contrast."
                ),
                trend_rationale=(
                    "Quiet luxury and relaxed tailoring dominate SS editorial boards; "
                    "this stack maps those keywords onto pieces you already own."
                ),
                missing_labels=["阔腿裤", "细腰带"],
                offers=[
                    MissingItemOffer(
                        label="阔腿裤",
                        product=ProductLink(
                            brand="Zara",
                            name="ZW Collection high-waist wide-leg jeans",
                            price_display="$49.90",
                            url="https://www.zara.com/us/en/search?searchTerm=wide%20leg%20jeans",
                        ),
                    ),
                    MissingItemOffer(
                        label="细腰带",
                        product=ProductLink(
                            brand="UNIQLO",
                            name="Italian leather reversible belt",
                            price_display="$39.90",
                            url="https://www.uniqlo.com/us/en/search?q=leather+belt",
                        ),
                    ),
                ],
            ),
            OutfitPlan(
                title="Date-night signal boost",
                description=(
                    "Short slip silhouette with an oversized knit thrown over the "
                    "shoulders — high contrast, camera-friendly depth."
                ),
                trend_rationale=(
                    "Metallic micro-accents and 'undone' layering are recurring in "
                    "party coverage; the knit tempers sheen for dinner lighting."
                ),
                missing_labels=["丝质吊带裙", "小号耳环"],
                offers=[
                    MissingItemOffer(
                        label="丝质吊带裙",
                        product=ProductLink(
                            brand="H&M",
                            name="Satin slip dress",
                            price_display="$34.99",
                            url="https://www2.hm.com/en_us/search-results.html?q=satin+slip+dress",
                        ),
                    ),
                    MissingItemOffer(
                        label="小号耳环",
                        product=ProductLink(
                            brand="H&M",
                            name="Chunky small hoop earrings",
                            price_display="$12.99",
                            url="https://www2.hm.com/en_us/search-results.html?q=hoop+earrings",
                        ),
                    ),
                ],
            ),
            OutfitPlan(
                title="Weekend entropy sink",
                description=(
                    "Crew sweatshirt, cropped jacket if wind picks up, straight "
                    "jeans, lug-sole boots — maximal comfort, still directional."
                ),
                trend_rationale=(
                    "Street moodboards favor lug soles + clean upper blocks; "
                    "mirrors the 'heavy sole / light top' silhouette trending on boards."
                ),
                missing_labels=["工装靴"],
                offers=[
                    MissingItemOffer(
                        label="工装靴",
                        product=ProductLink(
                            brand="Zara",
                            name="Track sole leather ankle boots",
                            price_display="$169.00",
                            url="https://www.zara.com/us/en/search?searchTerm=lug%20sole%20boots",
                        ),
                    ),
                ],
            ),
        ],
    )
