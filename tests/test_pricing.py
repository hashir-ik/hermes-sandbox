import pytest

from pricing import (
    BULK_DISCOUNT_TIERS,
    apply_discount,
    bulk_discount_percent,
    cart_total,
    checkout,
)


# ── cart_total ──────────────────────────────────────────────

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
        {"name": "eraser", "price": 1.50, "quantity": 2},
    ]
    assert cart_total(items) == 9.00


# ── apply_discount ──────────────────────────────────────────

def test_apply_discount():
    assert apply_discount(100.0, 10) == 90.0
    assert apply_discount(100.0, 0) == 100.0
    assert apply_discount(100.0, 100) == 0.0


def test_apply_discount_rejects_out_of_range():
    with pytest.raises(ValueError):
        apply_discount(100.0, 101)
    with pytest.raises(ValueError):
        apply_discount(100.0, -1)


# ── bulk_discount_percent ──────────────────────────────────

def test_bulk_discount_no_discount_below_threshold():
    items = [{"name": "pen", "price": 2.00, "quantity": 5}]
    assert bulk_discount_percent(items) == 0


def test_bulk_discount_5_pct_at_10():
    items = [{"name": "pen", "price": 2.00, "quantity": 10}]
    assert bulk_discount_percent(items) == 5


def test_bulk_discount_10_pct_at_25():
    items = [{"name": "pen", "price": 2.00, "quantity": 25}]
    assert bulk_discount_percent(items) == 10


def test_bulk_discount_15_pct_at_50():
    items = [{"name": "pen", "price": 2.00, "quantity": 50}]
    assert bulk_discount_percent(items) == 15


def test_bulk_discount_20_pct_at_100():
    items = [{"name": "pen", "price": 2.00, "quantity": 100}]
    assert bulk_discount_percent(items) == 20


def test_bulk_discount_sums_across_items():
    items = [
        {"name": "pen", "price": 2.00, "quantity": 6},
        {"name": "eraser", "price": 1.00, "quantity": 6},
    ]
    # 12 total -> 5% tier
    assert bulk_discount_percent(items) == 5


def test_bulk_discount_empty_cart():
    assert bulk_discount_percent([]) == 0


def test_bulk_discount_just_below_tier():
    items = [{"name": "pen", "price": 2.00, "quantity": 9}]
    assert bulk_discount_percent(items) == 0


def test_bulk_discount_above_highest_tier():
    items = [{"name": "pen", "price": 2.00, "quantity": 500}]
    assert bulk_discount_percent(items) == 20


# ── checkout with bulk discount ────────────────────────────

def test_checkout_no_discount():
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items) == 20.00


def test_checkout_manual_discount():
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, 25) == 15.00


def test_checkout_bulk_discount_applied():
    # 10 mugs @ $20 = $200, bulk 5% -> $190
    items = [{"name": "mug", "price": 20.00, "quantity": 10}]
    assert checkout(items) == 190.00


def test_checkout_manual_beats_bulk():
    # 10 items -> 5% bulk, but manual 50% is bigger
    items = [{"name": "mug", "price": 20.00, "quantity": 10}]
    assert checkout(items, 50) == 100.00


def test_checkout_bulk_beats_manual():
    # 100 items -> 20% bulk, manual only 5%
    items = [{"name": "pen", "price": 1.00, "quantity": 100}]
    assert checkout(items, 5) == 80.00


def test_checkout_large_bulk_order():
    # 50 pens @ $3 = $150, 15% bulk -> $127.50
    items = [{"name": "pen", "price": 3.00, "quantity": 50}]
    assert checkout(items) == 127.50
