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

from pricing import cart_total, checkout

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
    """The cart, with an optional ``?discount=`` applied."""
    raw = (request.args.get("discount") or "").strip()
    error = None
    percent = 0.0
    if raw:
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
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
