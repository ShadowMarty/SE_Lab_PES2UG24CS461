import pytest
from pizza_order import pizza_price, order_discount, delivery_status

# Example baseline test cases:
def test_plain_medium_pizza():
    assert pizza_price("medium", 0, False) == 350

def test_on_time_delivery():
    assert delivery_status(20, 3) == "on time"

# Tests added to achieve 90%+ Code (Line) Coverage
def test_pizza_price_extra_toppings():
    # 5 toppings: 3 * 40 + 2 * 30 = 180 + 350 = 530
    assert pizza_price("medium", 5, False) == 530

def test_pizza_price_cheese_burst():
    # large = 500, 2 toppings = 80, cheese burst = 100 -> 680
    assert pizza_price("large", 2, True) == 680

def test_order_discount_under_300():
    assert order_discount(200, "tuesday", False) == 0

def test_order_discount_tuesday():
    assert order_discount(400, "tuesday", False) == 200

def test_order_discount_weekend():
    assert order_discount(400, "saturday", False) == 0

def test_order_discount_regular_weekday_student():
    # 400 // 10 = 40 + 50 = 90
    assert order_discount(400, "friday", True) == 90

def test_delivery_status_not_deliverable():
    assert delivery_status(10, 15) == "not deliverable"

def test_delivery_status_late():
    assert delivery_status(40, 5) == "late"

def test_delivery_status_free_pizza():
    assert delivery_status(50, 5) == "free pizza"
