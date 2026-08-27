"""A deliberately small cart page, so the pipeline has something to click.

The pricing helpers in ``pricing.py`` were only ever exercised by unit
tests, which meant the QA stage had no browser surface and always took the
"this repo has no UI" path. This module exists to give it one.

Nothing here is clever on purpose. The interesting behaviour is all in
``pricing`` — this is a thin view over it, with stable ``data-testid``
hooks so a spec can select on intent rather than on styling.
"""

from __future__ import annotations

from flask import Flask, render_template, request

from pricing import cart_total, checkout, next_order_reference, resolve_discount_code

app = Flask(__name__)

#: The demo cart. A fixed basket keeps the page deterministic, which is
#: what makes it usable as a test fixture — a spec can assert on exact
#: totals without seeding a database first.
ITEMS = [
    {"name": "Notebook", "price": 4.50, "quantity": 3},
    {"name": "Pen", "price": 1.25, "quantity": 4},
    {"name": "Desk lamp", "price": 22.00, "quantity": 1},
]


@app.route("/", methods=["GET"])
def cart():
    """The cart, with an optional ``?discount=`` or ``?discount_code=`` applied.

    When both are supplied the code wins — see the task spec.
    """
    raw = (request.args.get("discount") or "").strip()
    raw_code = (request.args.get("discount_code") or "").strip()
    error = None
    percent = 0.0
    code_used = False

    # --- discount code takes priority ---
    if raw_code:
        resolved = resolve_discount_code(raw_code)
        if resolved is not None:
            percent = resolved
            code_used = True
        else:
            error = f"Unrecognised discount code: {raw_code!r}"
    elif raw:
        try:
            percent = float(raw)
        except ValueError:
            error = f"{raw!r} is not a number."

    total = cart_total(ITEMS)
    discounted = total
    if error is None and percent:
        try:
            discounted = checkout(ITEMS, percent)
        except ValueError as exc:
            error = str(exc)
            discounted = total
    return render_template(
        "cart.html",
        items=ITEMS,
        total=total,
        discounted=discounted,
        percent=percent,
        error=error,
        raw_discount=raw,
        raw_code=raw_code,
        code_used=code_used,
    )


@app.route("/checkout", methods=["POST"])
def do_checkout():
    """Process checkout and show the confirmation panel.

    The cart items, discount, and discount code are forwarded from the
    cart page as hidden fields so the confirmation can display them.
    """
    raw = (request.form.get("discount") or "").strip()
    raw_code = (request.form.get("discount_code") or "").strip()
    percent = 0.0
    code_used = False

    if raw_code:
        resolved = resolve_discount_code(raw_code)
        if resolved is not None:
            percent = resolved
            code_used = True
    elif raw:
        try:
            percent = float(raw)
        except ValueError:
            pass

    items = ITEMS
    total = cart_total(items)

    if not items:
        return render_template(
            "cart.html",
            empty_cart=True,
            confirmation=False,
        )

    if percent:
        paid = checkout(items, percent)
    else:
        paid = total

    order_ref = next_order_reference()

    return render_template(
        "cart.html",
        confirmation=True,
        order_ref=order_ref,
        items=items,
        total=total,
        paid=paid,
        percent=percent,
        code_used=code_used,
        raw_code=raw_code,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
