import pytest

from pricing import (
    BULK_DISCOUNT_TIERS,
    apply_discount,
    bulk_discount_percent,
    cart_total,
    checkout,
)


# ---------------------------------------------------------------------------
# cart_total
# ---------------------------------------------------------------------------

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


def test_cart_total_respects_quantity():
    items = [{"name": "pen", "price": 2.00, "quantity": 5}]
    assert cart_total(items) == 10.00


def test_cart_total_mixed_quantities():
    items = [
        {"name": "pen", "price": 2.00, "quantity": 3},
        {"name": "mug", "price": 10.00, "quantity": 2},
    ]
    assert cart_total(items) == 26.00


# ---------------------------------------------------------------------------
# apply_discount
# ---------------------------------------------------------------------------

def test_apply_discount():
    assert apply_discount(100.0, 10) == 90.0
    assert apply_discount(100.0, 0) == 100.0
    assert apply_discount(100.0, 100) == 0.0


def test_apply_discount_rejects_out_of_range():
    with pytest.raises(ValueError):
        apply_discount(100.0, 101)
    with pytest.raises(ValueError):
        apply_discount(100.0, -1)


# ---------------------------------------------------------------------------
# bulk_discount_percent
# ---------------------------------------------------------------------------

def test_bulk_discount_no_discount_below_10():
    items = [{"name": "mug", "price": 10.0, "quantity": 9}]
    assert bulk_discount_percent(items) == 0


def test_bulk_discount_5_at_10():
    items = [{"name": "mug", "price": 10.0, "quantity": 10}]
    assert bulk_discount_percent(items) == 5


def test_bulk_discount_10_at_25():
    items = [{"name": "mug", "price": 10.0, "quantity": 25}]
    assert bulk_discount_percent(items) == 10


def test_bulk_discount_15_at_50():
    items = [{"name": "mug", "price": 10.0, "quantity": 50}]
    assert bulk_discount_percent(items) == 15


def test_bulk_discount_20_at_100():
    items = [{"name": "mug", "price": 10.0, "quantity": 100}]
    assert bulk_discount_percent(items) == 20


def test_bulk_discount_sums_across_items():
    items = [
        {"name": "pen", "price": 2.0, "quantity": 7},
        {"name": "mug", "price": 10.0, "quantity": 5},
    ]
    # 7 + 5 = 12 → 5%
    assert bulk_discount_percent(items) == 5


def test_bulk_discount_empty_cart():
    assert bulk_discount_percent([]) == 0


# ---------------------------------------------------------------------------
# checkout
# ---------------------------------------------------------------------------

def test_checkout_no_discount():
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items) == 20.00


def test_checkout_with_manual_discount():
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, 25) == 15.00


def test_checkout_auto_bulk_discount():
    # 10 items → 5% bulk discount applied automatically
    items = [{"name": "mug", "price": 10.00, "quantity": 10}]
    # total = 100, 5% off = 95
    assert checkout(items) == 95.00


def test_checkout_manual_beats_bulk_when_higher():
    # 10 items → 5% bulk, but manual is 30% → 30% wins
    items = [{"name": "mug", "price": 10.00, "quantity": 10}]
    assert checkout(items, 30) == 70.00


def test_checkout_bulk_beats_manual_when_higher():
    # 100 items → 20% bulk, manual is 5% → 20% wins
    items = [{"name": "mug", "price": 10.00, "quantity": 100}]
    # total = 1000, 20% off = 800
    assert checkout(items) == 800.00
    assert checkout(items, 5) == 800.00
