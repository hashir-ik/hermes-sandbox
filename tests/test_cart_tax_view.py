"""Integration tests: tax line appears on the cart page."""

from app import app


def test_cart_shows_tax_line_no_discount():
    """Without discount: subtotal 40.50, tax 8.10, grand total 48.60."""
    client = app.test_client()
    r = client.get("/")
    html = r.data.decode()
    assert 'data-testid="tax-value"' in html
    assert "£8.10" in html
    assert 'data-testid="grand-total-value"' in html
    assert "£48.60" in html


def test_cart_shows_tax_after_discount():
    """10% off: subtotal 40.50, discounted 36.45, tax 7.29, grand 43.74."""
    client = app.test_client()
    r = client.get("/?discount=10")
    html = r.data.decode()
    assert "£7.29" in html
    assert "£43.74" in html


def test_cart_tax_with_discount_code():
    """SAVE20 → 20% off: 40.50 → 32.40, tax 6.48, grand 38.88."""
    client = app.test_client()
    r = client.get("/?discount_code=SAVE20")
    html = r.data.decode()
    assert "£6.48" in html
    assert "£38.88" in html


def test_tax_line_between_discount_and_total():
    """Tax line appears after discount line and before grand total."""
    client = app.test_client()
    r = client.get("/?discount=10")
    html = r.data.decode()
    discount_pos = html.index('data-testid="discounted-total"')
    tax_pos = html.index('data-testid="tax"')
    grand_pos = html.index('data-testid="grand-total"')
    assert discount_pos < tax_pos < grand_pos
