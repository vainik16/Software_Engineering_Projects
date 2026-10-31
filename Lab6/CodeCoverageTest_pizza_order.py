import pytest

from pizza_order import pizza_price, order_discount, delivery_status


# PIZZA PRICE TESTS

def test_small_pizza():
    assert pizza_price("small", 0, False) == 200


def test_medium_pizza():
    assert pizza_price("medium", 3, False) == 470


def test_large_pizza():
    assert pizza_price("large", 5, False) == 680


def test_cheese_burst():
    assert pizza_price("medium", 1, True) == 490


def test_invalid_size():
    with pytest.raises(ValueError):
        pizza_price("extra-large", 0, False)


def test_negative_toppings():
    with pytest.raises(ValueError):
        pizza_price("large", -1, False)


def test_small_cheese_burst():
    with pytest.raises(ValueError):
        pizza_price("small", 0, True)


# ORDER DISCOUNT TESTS

def test_order_below_300():
    assert order_discount(299, "monday", False) == 0


def test_tuesday_student_discount():
    assert order_discount(400, "tuesday", True) == 250


def test_weekend_discount():
    assert order_discount(400, "sunday", False) == 0


def test_regular_weekday_discount():
    assert order_discount(400, "monday", False) == 40


def test_student_weekday_discount():
    assert order_discount(400, "wednesday", True) == 90


# DELIVERY STATUS TESTS

def test_not_deliverable():
    assert delivery_status(20, 11) == "not deliverable"


def test_on_time():
    assert delivery_status(30, 5) == "on time"


def test_late():
    assert delivery_status(40, 5) == "late"


def test_free_pizza():
    assert delivery_status(50, 5) == "free pizza"