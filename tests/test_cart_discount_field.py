"""Regression tests for the discount field clearing bug (BUG-16).

The discount input must preserve the user's typed value after submission,
whether the value is valid, invalid, or empty.
"""

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_invalid_discount_stays_in_field(client):
    """An invalid (non-numeric) discount value stays in the input after submit."""
    resp = client.get("/?discount=abc")
    html = resp.data.decode()
    assert 'value="abc"' in html
    assert "not a number" in html


def test_valid_discount_stays_in_field(client):
    """A valid discount value stays in the input after submit."""
    resp = client.get("/?discount=10")
    html = resp.data.decode()
    assert 'value="10"' in html
    assert "error" not in html.lower() or 'data-testid="error"' not in html


def test_empty_discount_field_unchanged(client):
    """An empty discount leaves the field empty (no error, no value)."""
    resp = client.get("/")
    html = resp.data.decode()
    assert 'value=""' in html
    assert 'data-testid="error"' not in html


def test_valid_discount_shows_discounted_total(client):
    """A valid discount still computes and displays the discounted total."""
    resp = client.get("/?discount=10")
    html = resp.data.decode()
    assert 'data-testid="discounted-total"' in html
