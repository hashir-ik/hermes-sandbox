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
