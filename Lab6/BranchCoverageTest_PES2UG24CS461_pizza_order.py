import pytest
from pizza_order import pizza_price, order_discount, delivery_status

# Baseline tests
def test_plain_medium_pizza():
    assert pizza_price("medium", 0, False) == 350

def test_on_time_delivery():
    assert delivery_status(20, 3) == "on time"

# Tests for pizza_price branches & exception edge cases
def test_pizza_price_unknown_size():
    with pytest.raises(ValueError, match="unknown size"):
        pizza_price("extra_large", 0, False)

def test_pizza_price_negative_toppings():
    with pytest.raises(ValueError, match="invalid toppings"):
        pizza_price("small", -1, False)

def test_pizza_price_extra_toppings():
    # toppings > 3 branch: 3 * 40 + (5 - 3) * 30 = 120 + 60 = 180 + 350 = 530
    assert pizza_price("medium", 5, False) == 530

def test_pizza_price_cheese_burst_small_exception():
    with pytest.raises(ValueError, match="cheese burst not available for small"):
        pizza_price("small", 1, True)

def test_pizza_price_cheese_burst_large():
    # size != "small" with cheese burst: 500 + (2 * 40) + 100 = 680
    assert pizza_price("large", 2, True) == 680

# Tests for order_discount branches & edge cases
def test_order_discount_under_300():
    # order_total < 300 branch
    assert order_discount(250, "tuesday", False) == 0

def test_order_discount_tuesday_non_student():
    # tuesday branch (order_total // 2), is_student = False
    assert order_discount(400, "tuesday", False) == 200

def test_order_discount_saturday():
    # weekend branch: saturday
    assert order_discount(400, "saturday", False) == 0

def test_order_discount_sunday():
    # weekend branch: sunday
    assert order_discount(500, "sunday", False) == 0

def test_order_discount_weekday_with_student():
    # else branch (order_total // 10), is_student = True (+50)
    assert order_discount(400, "thursday", True) == 90

# Tests for delivery_status branches & edge cases
def test_delivery_status_not_deliverable():
    # distance_km > 10 branch
    assert delivery_status(15, 12) == "not deliverable"

def test_delivery_status_boundary_30_on_time():
    # minutes_taken <= 30 boundary
    assert delivery_status(30, 5) == "on time"

def test_delivery_status_late():
    # minutes_taken <= 45 branch
    assert delivery_status(45, 5) == "late"

def test_delivery_status_free_pizza():
    # minutes_taken > 45 branch
    assert delivery_status(46, 5) == "free pizza"
