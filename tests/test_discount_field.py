"""Tests for the discount field preservation bug (BUG-16).

Acceptance criteria:
- An invalid discount value stays in the field after submitting
- The error message still appears
- A valid discount still applies and still displays in the field
- Existing behaviour for empty input is unchanged
"""

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_invalid_discount_stays_in_field(client):
    """Typing 'abc' keeps 'abc' in the input after submit."""
    resp = client.get("/?discount=abc")
    html = resp.data.decode()
    assert 'value="abc"' in html


def test_invalid_discount_shows_error(client):
    """Typing 'abc' shows an error message."""
    resp = client.get("/?discount=abc")
    html = resp.data.decode()
    assert "not a number" in html.lower()


def test_valid_discount_shows_in_field(client):
    """A valid discount value is preserved in the field."""
    resp = client.get("/?discount=10")
    html = resp.data.decode()
    assert 'value="10"' in html


def test_valid_discount_applies(client):
    """A valid discount produces a discounted total."""
    resp = client.get("/?discount=10")
    html = resp.data.decode()
    assert "10" in html  # percent shown
    assert "discounted" in html  # discounted total section rendered


def test_empty_discount_leaves_field_empty(client):
    """Empty input keeps the field empty — existing behaviour."""
    resp = client.get("/")
    html = resp.data.decode()
    assert 'value=""' in html


def test_empty_string_discount_no_error(client):
    """Empty discount string does not produce an error."""
    resp = client.get("/?discount=")
    html = resp.data.decode()
    assert "error" not in html.lower() or 'data-testid="error"' not in html
