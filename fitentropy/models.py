"""Structured outfit / product models."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ProductLink(BaseModel):
    brand: str
    name: str
    price_display: str = ""
    url: str = ""
    image_url: str = ""


class MissingItemOffer(BaseModel):
    """A wardrobe gap plus one shoppable pick."""

    label: str = Field(description="Missing category or garment")
    product: ProductLink


class OutfitPlan(BaseModel):
    title: str
    description: str
    trend_rationale: str = Field(
        default="",
        description="Why this look aligns with current trends",
    )
    missing_labels: List[str] = Field(
        default_factory=list,
        description="Items the user does not already own",
    )
    offers: List[MissingItemOffer] = Field(
        default_factory=list,
        description="One product per missing label when available",
    )


class PipelineResult(BaseModel):
    trend_keywords: List[str] = Field(default_factory=list)
    outfits: List[OutfitPlan] = Field(default_factory=list)
    demo_mode: bool = False
    notes: str = ""
    memory_snippet: str = ""
    actionbook_hints: List[str] = Field(default_factory=list)
