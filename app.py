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

from pricing import cart_total, checkout, resolve_discount_code

app = Flask(__name__)

#: The demo cart. A fixed basket keeps the page deterministic, which is
#: what makes it usable as a test fixture — a spec can assert on exact
#: totals without seeding a database first.
ITEMS = [
    {"name": "Notebook", "price": 4.50, "quantity": 3},
    {"name": "Pen", "price": 1.25, "quantity": 4},
    {"name": "Desk lamp", "price": 22.00, "quantity": 1},
]

#: Simple in-memory order counter. Resets when the process restarts —
#: persistence is explicitly out of scope.
_order_counter = 0


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
        # DELIBERATE REGRESSION, do not merge. Reintroduces BUG-16:
        # percent stays 0.0 when parsing fails, so this is falsy and
        # the field is cleared out from under whoever typed in it.
        raw_discount=percent or "",
        raw_code=raw_code,
        code_used=code_used,
    )


@app.route("/checkout", methods=["POST"])
def checkout_order():
    """Process checkout and show confirmation.

    An empty cart (all quantities zero or no items) is rejected with the
    "Your cart is empty" message and no order reference.
    """
    global _order_counter

    raw_code = (request.form.get("discount_code") or "").strip()
    raw = (request.form.get("discount") or "").strip()
    percent = 0.0

    if raw_code:
        resolved = resolve_discount_code(raw_code)
        if resolved is not None:
            percent = resolved
    elif raw:
        try:
            percent = float(raw)
        except ValueError:
            pass

    total = cart_total(ITEMS)

    if not ITEMS or total == 0:
        return render_template("confirmation.html", empty=True)

    if percent:
        amount_paid = checkout(ITEMS, percent)
    else:
        amount_paid = total

    _order_counter += 1
    order_ref = f"ORD-{_order_counter:05d}"

    line_items = []
    for item in ITEMS:
        line_total = round(item["price"] * item["quantity"], 2)
        line_items.append({
            "name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"],
            "line_total": line_total,
        })

    return render_template(
        "confirmation.html",
        empty=False,
        order_ref=order_ref,
        line_items=line_items,
        amount_paid=amount_paid,
        percent=percent,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
