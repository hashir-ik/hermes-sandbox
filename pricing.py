"""Shopping cart pricing helpers."""


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


def checkout(items, discount_percent=0):
    """Cart total with an optional discount applied.

    ``discount_percent`` may be a number **or a string**.  Empty and
    whitespace-only strings are treated as "no discount" (0 %).
    """
    if isinstance(discount_percent, str):
        stripped = discount_percent.strip()
        if stripped == "":
            discount_percent = 0
        else:
            discount_percent = float(stripped)
    return apply_discount(cart_total(items), discount_percent)
