"""Shopping cart pricing helpers."""

# Bulk discount tiers: (minimum_quantity, discount_percent)
# Evaluated top-down; first matching tier wins.
BULK_DISCOUNT_TIERS = [
    (100, 20),
    (50, 15),
    (25, 10),
    (10, 5),
]


def cart_total(items):
    """Total price of a cart.

    ``items`` is a list of dicts, each with ``name``, ``price`` and
    ``quantity``.
    """
    total = 0.0
    for item in items:
        total += item["price"] * item["quantity"]
    return round(total, 2)


def apply_discount(price, percent):
    """Return ``price`` after applying a percentage discount."""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def bulk_discount_percent(items):
    """Return the bulk discount percentage for a cart based on total quantity.

    Uses ``BULK_DISCOUNT_TIERS`` to look up the discount.  Returns 0 if
    the total quantity doesn't reach any tier.
    """
    total_qty = sum(item["quantity"] for item in items)
    for min_qty, percent in BULK_DISCOUNT_TIERS:
        if total_qty >= min_qty:
            return percent
    return 0


def checkout(items, discount_percent=0):
    """Cart total with an optional manual discount *and* automatic bulk
    discount applied.

    The larger of the two discounts wins (they are not stacked).
    """
    bulk_pct = bulk_discount_percent(items)
    effective_discount = max(discount_percent, bulk_pct)
    return apply_discount(cart_total(items), effective_discount)
