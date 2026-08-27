"""Tests for the order confirmation flow."""
import pytest

from app import app, ITEMS, _order_counter
import app as app_module


@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Reset order counter before each test
    app_module._order_counter = 0
    with app.test_client() as c:
        yield c


class TestCheckoutConfirmation:
    """AC 1-4: confirmation panel after checkout."""

    def test_checkout_shows_confirmation_heading(self, client):
        """AC 1: panel has heading 'Order confirmed'."""
        rv = client.post("/checkout")
        assert rv.status_code == 200
        assert b"Order confirmed" in rv.data

    def test_checkout_lists_items_with_qty_and_line_total(self, client):
        """AC 2: panel lists every item with quantity and line total."""
        rv = client.post("/checkout")
        html = rv.data.decode()
        # Check each item from ITEMS appears
        for item in ITEMS:
            assert item["name"] in html
            line_total = round(item["price"] * item["quantity"], 2)
            assert f"£{line_total:.2f}" in html

    def test_checkout_shows_amount_paid_matching_total(self, client):
        """AC 3: amount paid matches cart total (no discount)."""
        rv = client.post("/checkout")
        html = rv.data.decode()
        # Total = 4.50*3 + 1.25*4 + 22.00 = 40.50
        assert "£40.50" in html
        assert b"Amount paid" in rv.data

    def test_checkout_shows_amount_paid_with_discount(self, client):
        """AC 3: amount paid matches discounted total when discount applied."""
        rv = client.post("/checkout", data={"discount": "10"})
        html = rv.data.decode()
        # 40.50 * 0.9 = 36.45
        assert "£36.45" in html

    def test_checkout_shows_amount_paid_with_discount_code(self, client):
        """AC 3: discount code is honoured at checkout."""
        rv = client.post("/checkout", data={"discount_code": "SAVE20"})
        html = rv.data.decode()
        # 40.50 * 0.8 = 32.40
        assert "£32.40" in html

    def test_checkout_shows_order_reference(self, client):
        """AC 4: order reference in ORD-00001 format."""
        rv = client.post("/checkout")
        assert b"ORD-00001" in rv.data

    def test_order_references_increment(self, client):
        """AC 4: successive checkouts get incrementing references."""
        rv1 = client.post("/checkout")
        rv2 = client.post("/checkout")
        assert b"ORD-00001" in rv1.data
        assert b"ORD-00002" in rv2.data


class TestEmptyCartCheckout:
    """AC 5: empty cart behaviour."""

    def test_empty_cart_shows_message(self, client, monkeypatch):
        """AC 5: empty cart shows 'Your cart is empty'."""
        monkeypatch.setattr(app_module, "ITEMS", [])
        rv = client.post("/checkout")
        assert b"Your cart is empty" in rv.data

    def test_empty_cart_no_order_reference(self, client, monkeypatch):
        """AC 5: empty cart does not show an order reference."""
        monkeypatch.setattr(app_module, "ITEMS", [])
        rv = client.post("/checkout")
        assert b"ORD-" not in rv.data

    def test_empty_cart_counter_not_incremented(self, client, monkeypatch):
        """Empty cart checkout does not consume an order number."""
        monkeypatch.setattr(app_module, "ITEMS", [])
        client.post("/checkout")
        assert app_module._order_counter == 0


class TestCartHasCheckoutButton:
    """The cart page has a checkout button."""

    def test_cart_page_has_checkout_button(self, client):
        rv = client.get("/")
        assert b"checkout-button" in rv.data
        assert b"Checkout" in rv.data
