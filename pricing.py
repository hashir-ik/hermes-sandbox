"""Shopping cart pricing helpers."""

#: Recognised discount codes and the percentage they grant.
DISCOUNT_CODES = {
    "SAVE10": 10,
    "SAVE20": 20,
}

#: In-memory order counter (no persistence required by the spec).
_order_counter = 0


def next_order_reference():
    """Return the next order reference in the form ORD-00001."""
    global _order_counter
    _order_counter += 1
    return f"ORD-{_order_counter:05d}"


def reset_order_counter():
    """Reset the order counter — for tests only."""
    global _order_counter
    _order_counter = 0


def resolve_discount_code(code):
    """Return the discount percentage for *code*, or ``None`` if unrecognised.

    Lookup is case-insensitive.  Empty / whitespace-only strings return
    ``None`` (no error).
    """
    stripped = code.strip() if isinstance(code, str) else ""
    if not stripped:
        return None
    return DISCOUNT_CODES.get(stripped.upper())


def cart_total(items):
    """Total price of a cart.

    ``items`` is a list of dicts, each with ``name``, ``price`` and
    ``quantity``.
    """
    total = 0.0
    for item in items:
        total += item["price"] * item["quantity"]
    return round(total, 2)


#: Tax rate applied to the cart total after discounts.
TAX_RATE = 0.20


def calculate_tax(price):
    """Return the tax amount for *price* at the standard rate (20 %)."""
    return round(price * TAX_RATE, 2)


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
