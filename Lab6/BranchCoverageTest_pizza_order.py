import pytest

from pizza_order import pizza_price, order_discount, delivery_status


# PIZZA SIZE BRANCHES

@pytest.mark.parametrize("size, expected", [
    ("small", 200),
    ("medium", 350),
    ("large", 500)
])
def test_valid_pizza_sizes(size, expected):
    assert pizza_price(size, 0, False) == expected


def test_invalid_pizza_size():
    with pytest.raises(ValueError):
        pizza_price("jumbo", 0, False)


# TOPPING BRANCHES

@pytest.mark.parametrize("toppings, expected", [
    (0, 350),
    (3, 470)
])
def test_three_or_fewer_toppings(toppings, expected):
    assert pizza_price("medium", toppings, False) == expected


@pytest.mark.parametrize("toppings, expected", [
    (4, 500 + 120 + 30),
    (6, 500 + 120 + 90)
])
def test_more_than_three_toppings(toppings, expected):
    assert pizza_price("large", toppings, False) == expected


def test_negative_toppings():
    with pytest.raises(ValueError):
        pizza_price("medium", -1, False)


# CHEESE BURST BRANCHES

def test_cheese_burst_enabled():
    assert pizza_price("large", 0, True) == 600


def test_cheese_burst_disabled():
    assert pizza_price("medium", 0, False) == 350


def test_cheese_burst_not_available_for_small():
    with pytest.raises(ValueError):
        pizza_price("small", 0, True)


# ORDER TOTAL BRANCHES

def test_order_below_300():
    assert order_discount(299, "monday", False) == 0


def test_order_equal_to_300():
    assert order_discount(300, "monday", False) == 30


# DAY-BASED DISCOUNT BRANCHES

def test_tuesday():
    assert order_discount(400, "tuesday", False) == 200


def test_saturday():
    assert order_discount(400, "saturday", False) == 0


def test_sunday():
    assert order_discount(400, "sunday", False) == 0


def test_regular_weekday():
    assert order_discount(400, "monday", False) == 40


# STUDENT BRANCHES

def test_student_discount():
    assert order_discount(400, "monday", True) == 90


def test_non_student_discount():
    assert order_discount(400, "monday", False) == 40


# DELIVERY DISTANCE BRANCHES

def test_distance_above_10_km():
    assert delivery_status(20, 11) == "not deliverable"


def test_distance_exactly_10_km():
    assert delivery_status(30, 10) == "on time"


# DELIVERY TIME BRANCHES

@pytest.mark.parametrize("minutes", [0, 30])
def test_on_time_delivery(minutes):
    assert delivery_status(minutes, 5) == "on time"


@pytest.mark.parametrize("minutes", [31, 45])
def test_late_delivery(minutes):
    assert delivery_status(minutes, 5) == "late"


def test_free_pizza_delivery():
    assert delivery_status(46, 5) == "free pizza"