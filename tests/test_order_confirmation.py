"""Tests for the order confirmation feature.

Covers: order reference generation in pricing.py, the POST /checkout
route in app.py, and the confirmation panel rendering.
"""

import pytest

from pricing import next_order_reference, reset_order_counter
from app import app


# ── Order reference unit tests ────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_counter():
    """Reset the order counter before each test."""
    reset_order_counter()


def test_first_order_reference():
    assert next_order_reference() == "ORD-00001"


def test_order_references_increment():
    assert next_order_reference() == "ORD-00001"
    assert next_order_reference() == "ORD-00002"
    assert next_order_reference() == "ORD-00003"


def test_order_reference_format_five_digits():
    for _ in range(99):
        next_order_reference()
    assert next_order_reference() == "ORD-00100"


# ── Checkout view integration tests ──────────────────────────────

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_checkout_shows_confirmation_heading(client):
    resp = client.post("/checkout")
    html = resp.data.decode()
    assert "Order confirmed" in html
    assert 'data-testid="confirmation-heading"' in html


def test_checkout_shows_order_reference(client):
    resp = client.post("/checkout")
    html = resp.data.decode()
    assert "ORD-00001" in html
    assert 'data-testid="order-ref"' in html


def test_checkout_lists_items_with_quantity_and_line_total(client):
    resp = client.post("/checkout")
    html = resp.data.decode()
    # Notebook: 4.50 * 3 = 13.50
    assert "Notebook" in html
    assert "13.50" in html
    # Pen: 1.25 * 4 = 5.00
    assert "Pen" in html
    assert "5.00" in html
    # Desk lamp: 22.00 * 1 = 22.00
    assert "Desk lamp" in html
    assert "22.00" in html


def test_checkout_shows_total_paid(client):
    """Without a discount, amount paid = cart total = 40.50."""
    resp = client.post("/checkout")
    html = resp.data.decode()
    assert 'data-testid="amount-paid"' in html
    assert "40.50" in html


def test_checkout_with_discount_code(client):
    """SAVE10 gives 10% off 40.50 = 36.45."""
    resp = client.post("/checkout", data={"discount_code": "SAVE10"})
    html = resp.data.decode()
    assert "Order confirmed" in html
    assert "36.45" in html


def test_checkout_with_percentage_discount(client):
    """A raw percentage of 20 gives 20% off 40.50 = 32.40."""
    resp = client.post("/checkout", data={"discount": "20"})
    html = resp.data.decode()
    assert "Order confirmed" in html
    assert "32.40" in html


def test_checkout_order_references_increment(client):
    resp1 = client.post("/checkout")
    resp2 = client.post("/checkout")
    html1 = resp1.data.decode()
    html2 = resp2.data.decode()
    assert "ORD-00001" in html1
    assert "ORD-00002" in html2


def test_checkout_no_cart_table_shown(client):
    """The confirmation replaces the cart — no cart table or discount form."""
    resp = client.post("/checkout")
    html = resp.data.decode()
    assert 'data-testid="cart"' not in html
    assert 'data-testid="discount-input"' not in html
    assert 'data-testid="checkout-button"' not in html


def test_cart_page_has_checkout_button(client):
    """The cart page has a checkout button."""
    resp = client.get("/")
    html = resp.data.decode()
    assert 'data-testid="checkout-button"' in html


def test_checkout_empty_cart_shows_message(client, monkeypatch):
    """Checking out with an empty cart shows 'Your cart is empty'."""
    import app as app_module
    monkeypatch.setattr(app_module, "ITEMS", [])
    resp = client.post("/checkout")
    html = resp.data.decode()
    assert "Your cart is empty" in html
    assert 'data-testid="empty-cart"' in html
    assert "ORD-" not in html
