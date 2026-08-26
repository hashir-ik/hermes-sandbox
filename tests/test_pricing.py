import pytest

from pricing import apply_discount, cart_total, checkout


def test_cart_total_single_item():
    items = [{"name": "mug", "price": 9.50, "quantity": 1}]
    assert cart_total(items) == 9.50


def test_cart_total_several_items():
    items = [
        {"name": "mug", "price": 9.50, "quantity": 1},
        {"name": "notebook", "price": 4.25, "quantity": 1},
    ]
    assert cart_total(items) == 13.75


def test_cart_total_empty():
    assert cart_total([]) == 0.0


def test_apply_discount():
    assert apply_discount(100.0, 10) == 90.0
    assert apply_discount(100.0, 0) == 100.0
    assert apply_discount(100.0, 100) == 0.0


def test_apply_discount_rejects_out_of_range():
    with pytest.raises(ValueError):
        apply_discount(100.0, 101)
    with pytest.raises(ValueError):
        apply_discount(100.0, -1)


def test_checkout():
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, 25) == 15.00


# ---------------------------------------------------------------------------
# Cart page (Flask) tests for discount-field preservation (BUG-16)
# ---------------------------------------------------------------------------
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app as flask_app  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_invalid_discount_keeps_value_in_field(client):
    """Typing a non-numeric discount should keep the raw text in the input."""
    rv = client.get("/?discount=abc")
    body = rv.data.decode()
    assert 'value="abc"' in body
    assert "is not a number" in body


def test_valid_discount_shows_in_field(client):
    """A valid discount should still appear in the input after applying."""
    rv = client.get("/?discount=10")
    body = rv.data.decode()
    assert 'value="10"' in body
    assert "error" not in body.lower() or 'data-testid="error"' not in body


def test_empty_discount_field_unchanged(client):
    """No discount param → empty field, no error."""
    rv = client.get("/")
    body = rv.data.decode()
    assert 'value=""' in body
    assert 'data-testid="error"' not in body


def test_error_message_still_appears_for_invalid(client):
    """Error message must be rendered for non-numeric input."""
    rv = client.get("/?discount=xyz")
    body = rv.data.decode()
    assert 'data-testid="error"' in body
    assert "xyz" in body and "is not a number" in body
