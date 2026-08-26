"""Start the Flask dev server without the debugger/reloader."""
import os
import sys

# Ensure we're in the right directory
_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_dir)
sys.path.insert(0, _dir)

from flask import Flask, render_template, request
from pricing import cart_total, checkout

app = Flask(__name__, template_folder=os.path.join(_dir, "templates"))

ITEMS = [
    {"name": "Notebook", "price": 4.50, "quantity": 3},
    {"name": "Pen", "price": 1.25, "quantity": 4},
    {"name": "Desk lamp", "price": 22.00, "quantity": 1},
]

@app.route("/", methods=["GET"])
def cart():
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
        raw_discount=raw,
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5111)
