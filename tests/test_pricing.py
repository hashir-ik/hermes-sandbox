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


def test_cart_total_respects_quantity():
    items = [
        {"name": "Notebook", "price": 4.50, "quantity": 3},
        {"name": "Pen", "price": 1.25, "quantity": 4},
        {"name": "Desk lamp", "price": 22.00, "quantity": 1},
    ]
    # 4.50*3 + 1.25*4 + 22.00*1 = 13.50 + 5.00 + 22.00 = 40.50
    assert cart_total(items) == 40.50


def test_checkout():
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, 25) == 15.00


def test_checkout_empty_string_discount():
    """Empty string discount should return the plain total, no error."""
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, "") == 20.00


def test_checkout_whitespace_only_discount():
    """Whitespace-only discount should behave the same as empty."""
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, "   ") == 20.00
    assert checkout(items, "\t\n") == 20.00


def test_checkout_string_number_discount():
    """A numeric string discount should work normally."""
    items = [{"name": "mug", "price": 20.00, "quantity": 1}]
    assert checkout(items, "25") == 15.00


def test_checkout_with_quantity():
    items = [{"name": "mug", "price": 10.00, "quantity": 3}]
    # total = 30.00, 25% off = 22.50
    assert checkout(items, 25) == 22.50
