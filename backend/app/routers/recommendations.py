"""
Deckers D2C Product Comparison & Recommendation endpoints.

GET  /products/                     — list full Deckers catalog
GET  /products/{product_id}         — single product detail
POST /products/compare              — side-by-side comparison matrix (2-4 products)
POST /recommendations               — scored recommendations driven by context
"""

from fastapi import APIRouter, HTTPException
from backend.app.models import (
    DeckersProduct, DeckersProductList, DeckersBrand, ProductCategory,
    CompareRequest, CompareResult, ComparisonRow,
    RecommendRequest, RecommendResult, RecommendedProduct,
)

router = APIRouter()

# ── Deckers D2C Catalog ───────────────────────────────────────────────────────
# Representative catalog for the five Deckers brands sold via Direct-to-Consumer
# (D2C) channels.  In production this would be pulled from Unity Catalog
# silver_product / a PIM system.

_CATALOG: list[DeckersProduct] = [
    # ── UGG ──────────────────────────────────────────────────────────────────
    DeckersProduct(
        product_id="UGG-001", brand=DeckersBrand.UGG,
        name="Classic Short II Boot", category=ProductCategory.BOOTS,
        price=160.0, msrp=160.0, rating=4.8, review_count=48320,
        in_stock=True, colors_available=12,
        features=["Genuine suede upper", "UGGplush™ wool blend lining",
                  "Treadlite by UGG™ outsole", "Water-resistant treatment"],
        use_cases=["comfort", "casual", "cold-weather"],
        best_for=["everyday wear", "cold climates", "gifting"],
        seasons=["fall", "winter"],
        gender="women", sustainability_score=55, d2c_exclusive=False,
        return_rate_pct=6.2,
    ),
    DeckersProduct(
        product_id="UGG-002", brand=DeckersBrand.UGG,
        name="Tasman Slipper", category=ProductCategory.SLIPPERS,
        price=120.0, msrp=120.0, rating=4.7, review_count=62100,
        in_stock=True, colors_available=18,
        features=["Sheepskin collar", "Suede heel counter",
                  "UGGpure™ wool sockliner", "Flexible EVA outsole"],
        use_cases=["comfort", "casual", "indoor-outdoor"],
        best_for=["gifting", "everyday casual", "year-round comfort"],
        seasons=["spring", "fall", "winter", "summer"],
        gender="unisex", sustainability_score=58, d2c_exclusive=False,
        return_rate_pct=4.8,
    ),
    DeckersProduct(
        product_id="UGG-003", brand=DeckersBrand.UGG,
        name="Neumel Boot", category=ProductCategory.BOOTS,
        price=150.0, msrp=150.0, rating=4.6, review_count=28450,
        in_stock=True, colors_available=8,
        features=["Nubuck upper", "UGGpure™ wool lining",
                  "Crepe rubber outsole", "Chukka silhouette"],
        use_cases=["comfort", "casual", "cold-weather"],
        best_for=["men's gifting", "casual office", "weekend wear"],
        seasons=["fall", "winter"],
        gender="men", sustainability_score=53, d2c_exclusive=False,
        return_rate_pct=7.1,
    ),
    DeckersProduct(
        product_id="UGG-004", brand=DeckersBrand.UGG,
        name="Ultra Mini Platform Boot", category=ProductCategory.BOOTS,
        price=170.0, msrp=170.0, rating=4.5, review_count=15200,
        in_stock=True, colors_available=10,
        features=["Genuine suede", "UGGplush™ lining", "Platform EVA outsole",
                  "D2C-exclusive colorways"],
        use_cases=["fashion", "casual", "cold-weather"],
        best_for=["fashion-forward", "holiday gifting", "street style"],
        seasons=["fall", "winter"],
        gender="women", sustainability_score=52, d2c_exclusive=True,
        return_rate_pct=8.4,
    ),
    DeckersProduct(
        product_id="UGG-005", brand=DeckersBrand.UGG,
        name="Scuffette II Slipper", category=ProductCategory.SLIPPERS,
        price=95.0, msrp=95.0, rating=4.6, review_count=38600,
        in_stock=True, colors_available=14,
        features=["Sheepskin upper", "UGGpure™ wool lining",
                  "Flexible outsole", "Slip-on silhouette"],
        use_cases=["comfort", "indoor-outdoor"],
        best_for=["everyday comfort", "gifting", "recovery"],
        seasons=["spring", "fall", "winter", "summer"],
        gender="women", sustainability_score=56, d2c_exclusive=False,
        return_rate_pct=5.0,
    ),

    # ── HOKA ─────────────────────────────────────────────────────────────────
    DeckersProduct(
        product_id="HOK-001", brand=DeckersBrand.HOKA,
        name="Clifton 9", category=ProductCategory.ROAD_RUNNING,
        price=145.0, msrp=145.0, rating=4.7, review_count=24300,
        in_stock=True, colors_available=20,
        features=["CMEVA midsole", "Early-stage meta-rocker",
                  "Engineered mesh upper", "Full-length compression-molded EVA"],
        use_cases=["running", "road-running", "daily-training", "walking"],
        best_for=["daily mileage", "marathon training", "recovery runs"],
        seasons=["spring", "summer", "fall"],
        gender="unisex", sustainability_score=62, d2c_exclusive=False,
        return_rate_pct=5.5,
    ),
    DeckersProduct(
        product_id="HOK-002", brand=DeckersBrand.HOKA,
        name="Speedgoat 5", category=ProductCategory.TRAIL,
        price=155.0, msrp=155.0, rating=4.8, review_count=18900,
        in_stock=True, colors_available=15,
        features=["Vibram® Megagrip outsole", "Max cushion midsole",
                  "Reinforced toe cap", "Quick-Dry mesh upper"],
        use_cases=["trail-running", "hiking", "outdoor", "running"],
        best_for=["technical trails", "ultra events", "rugged terrain"],
        seasons=["spring", "summer", "fall"],
        gender="unisex", sustainability_score=60, d2c_exclusive=False,
        return_rate_pct=4.2,
    ),
    DeckersProduct(
        product_id="HOK-003", brand=DeckersBrand.HOKA,
        name="Bondi 8", category=ProductCategory.ROAD_RUNNING,
        price=165.0, msrp=165.0, rating=4.6, review_count=31200,
        in_stock=True, colors_available=22,
        features=["Maximum EVA cushion", "Meta-Rocker geometry",
                  "Plush collar and tongue", "Extended heel crash pad"],
        use_cases=["running", "road-running", "walking", "comfort"],
        best_for=["maximum cushion seekers", "long-distance", "standing all day"],
        seasons=["spring", "summer", "fall", "winter"],
        gender="unisex", sustainability_score=63, d2c_exclusive=False,
        return_rate_pct=6.0,
    ),
    DeckersProduct(
        product_id="HOK-004", brand=DeckersBrand.HOKA,
        name="Challenger ATR 7", category=ProductCategory.TRAIL,
        price=135.0, msrp=135.0, rating=4.5, review_count=12400,
        in_stock=True, colors_available=12,
        features=["Multi-directional lugs", "Lightweight EVA midsole",
                  "Breathable mesh", "All-terrain-ready outsole"],
        use_cases=["trail-running", "hiking", "outdoor", "running"],
        best_for=["trail-to-road transitions", "beginner trail runners"],
        seasons=["spring", "summer", "fall"],
        gender="unisex", sustainability_score=58, d2c_exclusive=False,
        return_rate_pct=5.8,
    ),
    DeckersProduct(
        product_id="HOK-005", brand=DeckersBrand.HOKA,
        name="Rincon 3", category=ProductCategory.ROAD_RUNNING,
        price=130.0, msrp=130.0, rating=4.5, review_count=16800,
        in_stock=True, colors_available=16,
        features=["Lightweight EVA foam", "Breathable mesh upper",
                  "Early-stage meta-rocker", "Single-layer construction"],
        use_cases=["running", "road-running", "speed-training"],
        best_for=["tempo runs", "racing", "lightweight preference"],
        seasons=["spring", "summer", "fall"],
        gender="unisex", sustainability_score=59, d2c_exclusive=False,
        return_rate_pct=5.2,
    ),

    # ── Teva ─────────────────────────────────────────────────────────────────
    DeckersProduct(
        product_id="TEV-001", brand=DeckersBrand.TEVA,
        name="Original Universal Sandal", category=ProductCategory.SANDALS,
        price=50.0, msrp=50.0, rating=4.6, review_count=45200,
        in_stock=True, colors_available=24,
        features=["Strappy nylon upper", "Hook-and-loop closure",
                  "EVA foam midsole", "Spider Original rubber outsole"],
        use_cases=["outdoor", "casual", "water", "hiking-light"],
        best_for=["beach", "camping", "travel", "everyday summer"],
        seasons=["spring", "summer"],
        gender="unisex", sustainability_score=72, d2c_exclusive=False,
        return_rate_pct=3.8,
    ),
    DeckersProduct(
        product_id="TEV-002", brand=DeckersBrand.TEVA,
        name="Hurricane XLT2", category=ProductCategory.SANDALS,
        price=65.0, msrp=65.0, rating=4.5, review_count=22100,
        in_stock=True, colors_available=18,
        features=["Quick-dry webbing", "Shoc Pad™ heel cushion",
                  "Universal Strapping System", "High-traction rubber outsole"],
        use_cases=["outdoor", "hiking", "water", "casual"],
        best_for=["river crossings", "light hikes", "festival wear"],
        seasons=["spring", "summer"],
        gender="unisex", sustainability_score=70, d2c_exclusive=False,
        return_rate_pct=4.5,
    ),
    DeckersProduct(
        product_id="TEV-003", brand=DeckersBrand.TEVA,
        name="Terra Fi 5", category=ProductCategory.HIKING,
        price=100.0, msrp=100.0, rating=4.4, review_count=9800,
        in_stock=True, colors_available=8,
        features=["Durabrasion rubber outsole", "Recycled webbing upper",
                  "4mm lug depth", "Teva Float foam midsole"],
        use_cases=["hiking", "outdoor", "water", "backpacking"],
        best_for=["technical hikes", "canyoneering", "multi-day"],
        seasons=["spring", "summer"],
        gender="unisex", sustainability_score=78, d2c_exclusive=False,
        return_rate_pct=5.1,
    ),

    # ── Sanuk ─────────────────────────────────────────────────────────────────
    DeckersProduct(
        product_id="SAN-001", brand=DeckersBrand.SANUK,
        name="Yoga Mat 3 Sandal", category=ProductCategory.CASUAL,
        price=45.0, msrp=45.0, rating=4.4, review_count=18200,
        in_stock=True, colors_available=20,
        features=["Real yoga mat footbed", "Vegan upper",
                  "Lightweight EVA outsole", "Soft webbing straps"],
        use_cases=["casual", "comfort", "indoor-outdoor"],
        best_for=["yoga enthusiasts", "beach days", "casual daily"],
        seasons=["spring", "summer"],
        gender="women", sustainability_score=68, d2c_exclusive=False,
        return_rate_pct=4.2,
    ),
    DeckersProduct(
        product_id="SAN-002", brand=DeckersBrand.SANUK,
        name="Vagabond Canvas Sneaker", category=ProductCategory.CASUAL,
        price=65.0, msrp=65.0, rating=4.3, review_count=12500,
        in_stock=True, colors_available=10,
        features=["Canvas upper", "Happy U™ construction",
                  "Life is Good™ insole", "Flexible rubber outsole"],
        use_cases=["casual", "comfort", "everyday"],
        best_for=["laid-back lifestyle", "weekend casual", "travel"],
        seasons=["spring", "summer", "fall"],
        gender="men", sustainability_score=65, d2c_exclusive=False,
        return_rate_pct=6.0,
    ),

    # ── Koolaburra ────────────────────────────────────────────────────────────
    DeckersProduct(
        product_id="KOO-001", brand=DeckersBrand.KOOLABURRA,
        name="Victoria Short Boot", category=ProductCategory.BOOTS,
        price=90.0, msrp=90.0, rating=4.4, review_count=8400,
        in_stock=True, colors_available=9,
        features=["Faux fur lining", "Suede-like upper",
                  "Flexible outsole", "Pull-on silhouette"],
        use_cases=["comfort", "casual", "cold-weather"],
        best_for=["value shoppers", "gift ideas", "casual winter"],
        seasons=["fall", "winter"],
        gender="women", sustainability_score=48, d2c_exclusive=False,
        return_rate_pct=8.0,
    ),
    DeckersProduct(
        product_id="KOO-002", brand=DeckersBrand.KOOLABURRA,
        name="Koola Short Boot", category=ProductCategory.BOOTS,
        price=80.0, msrp=80.0, rating=4.3, review_count=5200,
        in_stock=False, colors_available=7,
        features=["Faux fur collar", "Fabric upper",
                  "Slip-on design", "Lightweight EVA outsole"],
        use_cases=["comfort", "casual", "cold-weather"],
        best_for=["budget-conscious", "casual winter", "kids and teens"],
        seasons=["fall", "winter"],
        gender="unisex", sustainability_score=45, d2c_exclusive=False,
        return_rate_pct=9.5,
    ),
]

_CATALOG_INDEX: dict[str, DeckersProduct] = {p.product_id: p for p in _CATALOG}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _score_product(p: DeckersProduct, req: RecommendRequest) -> tuple[float, list[str]]:
    """
    Rule-based D2C recommendation scoring (0 – 100).

    Weights:
      Rating quality     →  up to 30 pts
      Activity match     →  up to 25 pts
      Budget fit         →  up to 15 pts
      Season relevance   →  up to 10 pts
      Gender match       →   up to 8 pts
      Stock availability →   up to 7 pts
      Sustainability     →   up to 5 pts
    """
    score = 0.0
    reasons: list[str] = []

    # Rating (max 30)
    rating_pts = (p.rating / 5.0) * 30.0
    score += rating_pts
    if p.rating >= 4.7:
        reasons.append(f"Top-rated ({p.rating}★ from {p.review_count:,} reviews)")
    elif p.rating >= 4.4:
        reasons.append(f"Highly rated ({p.rating}★)")

    # Activity / use-case match (max 25)
    if req.activity:
        activity_lower = req.activity.lower()
        matched = [uc for uc in p.use_cases if activity_lower in uc.lower() or uc.lower() in activity_lower]
        if matched:
            score += 25.0
            reasons.append(f"Strong match for '{req.activity}' activity")
        else:
            # Partial credit if same family (e.g. "hiking" overlaps "outdoor")
            outdoor_family = {"hiking", "outdoor", "trail-running", "water", "camping"}
            running_family = {"running", "road-running", "trail-running", "speed-training", "daily-training"}
            comfort_family = {"comfort", "casual", "indoor-outdoor"}
            families = [outdoor_family, running_family, comfort_family]
            for fam in families:
                if activity_lower in fam and any(uc.lower() in fam for uc in p.use_cases):
                    score += 12.0
                    reasons.append(f"Related match for '{req.activity}' activity")
                    break

    # Budget fit (max 15)
    if req.budget_max is not None:
        if p.price <= req.budget_max:
            budget_ratio = 1.0 - (p.price / req.budget_max)
            score += 10.0 + budget_ratio * 5.0
            reasons.append(f"Within budget (${p.price:.0f} ≤ ${req.budget_max:.0f})")
        else:
            reasons.append(f"Above budget (${p.price:.0f} vs ${req.budget_max:.0f} limit)")

    # Season relevance (max 10)
    if req.season:
        if req.season.lower() in [s.lower() for s in p.seasons]:
            score += 10.0
            reasons.append(f"Perfect for {req.season}")

    # Gender match (max 8)
    if req.gender:
        if p.gender == "unisex" or p.gender == req.gender.lower():
            score += 8.0
            if p.gender == "unisex":
                reasons.append("Available for all genders")

    # Stock (max 7)
    if p.in_stock:
        score += 7.0
    else:
        reasons.append("Currently out of stock")

    # Sustainability (max 5)
    score += (p.sustainability_score / 100.0) * 5.0
    if p.sustainability_score >= 70:
        reasons.append(f"High sustainability score ({p.sustainability_score}/100)")

    # Customer segment signal
    if req.customer_segment:
        seg = req.customer_segment.lower()
        if seg == "premium" and p.price >= 140:
            score += 5.0
            reasons.append("Premium tier product")
        elif seg == "athlete" and p.brand == "HOKA":
            score += 5.0
            reasons.append("Preferred brand for athletes")
        elif seg == "outdoor" and p.brand in ("Teva", "HOKA"):
            score += 5.0
            reasons.append("Top pick for outdoor enthusiasts")
        elif seg == "casual" and p.brand in ("Sanuk", "UGG"):
            score += 5.0
            reasons.append("Ideal for casual lifestyle")

    # D2C exclusive bonus
    if p.d2c_exclusive:
        reasons.append("D2C exclusive — only on Deckers.com")

    return round(min(score, 100.0), 1), reasons


def _comparison_winner(attribute: str, values: dict[str, float | str | bool],
                       products: list[DeckersProduct]) -> tuple[str | None, str | None]:
    """Return (winner_product_id, reason) for a numeric comparison attribute."""
    numeric_higher = {"rating", "review_count", "colors_available", "sustainability_score", "feature_count"}
    numeric_lower  = {"price", "return_rate_pct"}
    id_map = {p.product_id: p for p in products}

    if attribute in numeric_higher:
        best_id = max(values, key=lambda k: float(values[k]))
        best_val = values[best_id]
        tied = [k for k, v in values.items() if float(v) == float(best_val)]
        if len(tied) > 1:
            return None, None
        name = id_map[best_id].name
        return best_id, f"{name} leads on {attribute.replace('_', ' ')}"

    if attribute in numeric_lower:
        best_id = min(values, key=lambda k: float(values[k]))
        best_val = values[best_id]
        tied = [k for k, v in values.items() if float(v) == float(best_val)]
        if len(tied) > 1:
            return None, None
        name = id_map[best_id].name
        label = "most affordable" if attribute == "price" else "lowest return rate"
        return best_id, f"{name} wins — {label}"

    return None, None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=DeckersProductList)
def list_products(
    brand:    str | None = None,
    category: str | None = None,
    gender:   str | None = None,
    in_stock: bool | None = None,
):
    """List all Deckers D2C products. Supports optional filters."""
    results = list(_CATALOG)
    if brand:
        results = [p for p in results if p.brand.lower() == brand.lower()]
    if category:
        results = [p for p in results if p.category.lower() == category.lower()]
    if gender:
        results = [p for p in results if p.gender == gender.lower() or p.gender == "unisex"]
    if in_stock is not None:
        results = [p for p in results if p.in_stock == in_stock]
    return DeckersProductList(products=results, total=len(results))


@router.get("/{product_id}", response_model=DeckersProduct)
def get_product(product_id: str):
    """Get full details for a single Deckers product."""
    product = _CATALOG_INDEX.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")
    return product


@router.post("/compare", response_model=CompareResult)
def compare_products(body: CompareRequest):
    """
    Compare 2–4 Deckers products side by side.
    Returns a structured comparison matrix with winner highlighted per attribute.
    """
    if len(body.product_ids) < 2 or len(body.product_ids) > 4:
        raise HTTPException(status_code=400, detail="Provide between 2 and 4 product IDs.")

    products: list[DeckersProduct] = []
    for pid in body.product_ids:
        p = _CATALOG_INDEX.get(pid)
        if not p:
            raise HTTPException(status_code=404, detail=f"Product '{pid}' not found.")
        products.append(p)

    # Build comparison matrix
    matrix: list[ComparisonRow] = []

    def row(attr: str, extractor, fmt=None) -> ComparisonRow:
        values = {p.product_id: extractor(p) for p in products}
        winner, reason = _comparison_winner(attr, values, products)
        if fmt:
            display_values = {k: fmt(v) for k, v in values.items()}
        else:
            display_values = {k: str(v) for k, v in values.items()}
        return ComparisonRow(attribute=attr, values=display_values, winner=winner, winner_reason=reason)

    matrix.append(row("price",               lambda p: p.price,               lambda v: f"${v:.2f}"))
    matrix.append(row("rating",              lambda p: p.rating,              lambda v: f"{v}★"))
    matrix.append(row("review_count",        lambda p: p.review_count,        lambda v: f"{int(v):,}"))
    matrix.append(row("colors_available",    lambda p: p.colors_available,    lambda v: str(int(v))))
    matrix.append(row("sustainability_score",lambda p: p.sustainability_score,lambda v: f"{int(v)}/100"))
    matrix.append(row("return_rate_pct",     lambda p: p.return_rate_pct,     lambda v: f"{v}%"))
    matrix.append(row("feature_count",       lambda p: len(p.features),       lambda v: str(int(v))))

    # Boolean rows (no winner logic)
    matrix.append(ComparisonRow(
        attribute="in_stock",
        values={p.product_id: "Yes" if p.in_stock else "No" for p in products},
    ))
    matrix.append(ComparisonRow(
        attribute="d2c_exclusive",
        values={p.product_id: "Yes" if p.d2c_exclusive else "No" for p in products},
    ))
    matrix.append(ComparisonRow(
        attribute="gender",
        values={p.product_id: p.gender for p in products},
    ))
    matrix.append(ComparisonRow(
        attribute="seasons",
        values={p.product_id: ", ".join(p.seasons) for p in products},
    ))

    # Determine overall recommended winner using a quick composite score
    winner = max(
        products,
        key=lambda p: (p.rating * 20 + (100 - p.return_rate_pct) + p.sustainability_score * 0.3
                       + (10 if p.in_stock else 0) + len(p.features) * 2),
    )
    reason = (
        f"{winner.name} earns the top recommendation: "
        f"{winner.rating}★ rating across {winner.review_count:,} reviews, "
        f"{winner.sustainability_score}/100 sustainability, and "
        f"only {winner.return_rate_pct}% return rate."
    )

    return CompareResult(
        products=products,
        matrix=matrix,
        recommended_winner=winner.product_id,
        recommendation_reason=reason,
    )


@router.post("/recommendations", response_model=RecommendResult)
def get_recommendations(body: RecommendRequest):
    """
    Return top Deckers D2C product recommendations scored against customer context.
    Supports based-on product, budget, activity, season, gender, and customer segment.
    """
    scored: list[tuple[float, list[str], DeckersProduct]] = []

    for p in _CATALOG:
        # Skip the seed product itself from results
        if body.based_on_product_id and p.product_id == body.based_on_product_id:
            continue
        score, reasons = _score_product(p, body)
        scored.append((score, reasons, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:5]

    recommendations = [
        RecommendedProduct(product=p, score=s, match_reasons=r)
        for s, r, p in top
    ]

    # Build context summary
    parts: list[str] = []
    if body.based_on_product_id:
        seed = _CATALOG_INDEX.get(body.based_on_product_id)
        if seed:
            parts.append(f"based on {seed.name}")
    if body.activity:
        parts.append(f"activity: {body.activity}")
    if body.budget_max:
        parts.append(f"budget: ${body.budget_max:.0f}")
    if body.season:
        parts.append(f"season: {body.season}")
    if body.gender:
        parts.append(f"gender: {body.gender}")
    if body.customer_segment:
        parts.append(f"segment: {body.customer_segment}")
    context = "Recommendations " + (" · ".join(parts) if parts else "across full D2C catalog")

    return RecommendResult(
        based_on=body.based_on_product_id,
        recommendations=recommendations,
        context_summary=context,
    )
