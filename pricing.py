"""Shopping cart pricing helpers."""

# Bulk order discount tiers: (minimum_quantity, discount_percent)
# Evaluated highest-first; the first tier whose minimum is met wins.
BULK_DISCOUNT_TIERS = [
    (50, 10),
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
    """Return the bulk discount percentage for the given cart items.

    Sums the ``quantity`` of every item and returns the highest
    matching tier from ``BULK_DISCOUNT_TIERS``, or 0 if none match.
    """
    total_qty = sum(item["quantity"] for item in items)
    for min_qty, pct in BULK_DISCOUNT_TIERS:
        if total_qty >= min_qty:
            return pct
    return 0


def checkout(items, discount_percent=0):
    """Cart total with an optional discount applied.

    The effective discount is the greater of ``discount_percent`` and
    the automatic bulk-order discount determined by total quantity.
    """
    bulk_pct = bulk_discount_percent(items)
    effective = max(discount_percent, bulk_pct)
    return apply_discount(cart_total(items), effective)
