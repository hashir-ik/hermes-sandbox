"""Tests for the discount-code feature.

Covers: resolve_discount_code() in pricing.py and the discount_code
query parameter in the cart view.
"""

import pytest

from pricing import resolve_discount_code
from app import app


# ── resolve_discount_code unit tests ──────────────────────────────

def test_save10_resolves_to_10():
    assert resolve_discount_code("SAVE10") == 10


def test_save20_resolves_to_20():
    assert resolve_discount_code("SAVE20") == 20


def test_code_is_case_insensitive():
    assert resolve_discount_code("save10") == 10
    assert resolve_discount_code("Save20") == 20
    assert resolve_discount_code("sAvE10") == 10


def test_unrecognised_code_returns_none():
    assert resolve_discount_code("BOGUS") is None
    assert resolve_discount_code("SAVE30") is None


def test_empty_string_returns_none():
    assert resolve_discount_code("") is None


def test_whitespace_only_returns_none():
    assert resolve_discount_code("   ") is None
    assert resolve_discount_code("\t\n") is None


# ── Cart view integration tests ───────────────────────────────────

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_save10_applies_10_percent(client):
    """SAVE10 applies 10% off; total is 40.50 → 36.45."""
    resp = client.get("/?discount_code=SAVE10")
    html = resp.data.decode()
    assert 'value="SAVE10"' in html
    assert "36.45" in html
    assert 'data-testid="error"' not in html


def test_save20_applies_20_percent(client):
    """SAVE20 applies 20% off; total is 40.50 → 32.40."""
    resp = client.get("/?discount_code=SAVE20")
    html = resp.data.decode()
    assert 'value="SAVE20"' in html
    assert "32.40" in html
    assert 'data-testid="error"' not in html


def test_case_insensitive_code_in_view(client):
    """save10 works the same as SAVE10."""
    resp = client.get("/?discount_code=save10")
    html = resp.data.decode()
    assert "36.45" in html
    assert 'data-testid="error"' not in html
    # The typed code stays in the field as-is
    assert 'value="save10"' in html


def test_unrecognised_code_shows_error(client):
    """An unrecognised code shows an error and leaves the total unchanged."""
    resp = client.get("/?discount_code=NOTREAL")
    html = resp.data.decode()
    assert 'data-testid="error"' in html
    assert "Unrecognised" in html
    # The typed code stays in the field
    assert 'value="NOTREAL"' in html
    # No discounted total shown
    assert 'data-testid="discounted-total"' not in html


def test_empty_code_no_error(client):
    """An empty code is not an error."""
    resp = client.get("/?discount_code=")
    html = resp.data.decode()
    assert 'data-testid="error"' not in html
    assert 'data-testid="discounted-total"' not in html


def test_code_wins_over_percentage(client):
    """When both are supplied, the code wins."""
    resp = client.get("/?discount_code=SAVE10&discount=50")
    html = resp.data.decode()
    # 10% off 40.50 = 36.45, NOT 50% off
    assert "36.45" in html
    assert "20.25" not in html  # 50% would give 20.25


def test_no_discount_code_field_renders(client):
    """The discount code input exists on the page."""
    resp = client.get("/")
    html = resp.data.decode()
    assert 'data-testid="discount-code-input"' in html
