"""Branch coverage tests for coupon_validator.py.

Goal: make every decision take both its True and its False outcome,
including the loop in best_discount (runs / doesn't run) and the
`value > best` check (updates / doesn't update).
"""
import pytest
from coupon_validator import coupon_discount, best_discount, is_expired


# ---------- coupon_discount ----------

@pytest.mark.parametrize("total", [0, -50])
def test_non_positive_cart_raises(total):
    # cart_total <= 0 -> True (zero and negative)
    with pytest.raises(ValueError, match="empty cart"):
        coupon_discount("WELCOME10", total, True, "mon")


@pytest.mark.parametrize("is_new_user, expected", [
    (True, 20),    # is_new_user True
    (False, 0),    # is_new_user False
])
def test_welcome10_branches(is_new_user, expected):
    assert coupon_discount("WELCOME10", 200, is_new_user, "mon") == expected


@pytest.mark.parametrize("total, day, expected", [
    (600, "sat", 120),   # weekend True, total >= 500 True
    (500, "sun", 100),   # boundary: exactly 500 still gets 20%
    (499, "sat", 50),    # weekend True, total >= 500 False
    (600, "fri", 0),     # weekend False
    (600, "Sat", 0),     # day check is case-sensitive -> treated as weekday
])
def test_weekend20_branches(total, day, expected):
    assert coupon_discount("WEEKEND20", total, False, day) == expected


@pytest.mark.parametrize("total, expected", [
    (301, 100),   # total > 300 True
    (300, 0),     # boundary: exactly 300 is False
])
def test_flat100_branches(total, expected):
    assert coupon_discount("FLAT100", total, False, "mon") == expected


@pytest.mark.parametrize("code", ["BOGUS", "", "welcome10"])
def test_unknown_codes_give_zero(code):
    # every code comparison False -> final return 0 (codes are case-sensitive)
    assert coupon_discount(code, 200, True, "sat") == 0


# ---------- best_discount ----------

def test_best_discount_empty_list():
    # loop body never runs -> best stays 0
    assert best_discount([], 400, True, "sat") == 0


def test_best_discount_later_code_is_not_better():
    # value > best True for FLAT100, then False for WELCOME10 (40 < 100)
    assert best_discount(["FLAT100", "WELCOME10"], 400, True, "mon") == 100


def test_best_discount_later_code_is_better():
    # value > best True twice: 40 then 100
    assert best_discount(["WELCOME10", "FLAT100"], 400, True, "mon") == 100


def test_best_discount_all_zero():
    # value > best False on every iteration
    assert best_discount(["BOGUS", "FLAT100"], 200, False, "mon") == 0


def test_best_discount_capped():
    # best (50) > cap (100 * 0.4 = 40) -> True
    assert best_discount(["WEEKEND20"], 100, False, "sat") == 40


def test_best_discount_equal_to_cap_not_capped():
    # boundary: best (50) == cap (125 * 0.4 = 50) -> False, returns best
    assert best_discount(["WEEKEND20"], 125, False, "sun") == 50


def test_best_discount_propagates_empty_cart_error():
    with pytest.raises(ValueError):
        best_discount(["WELCOME10"], 0, True, "mon")


# ---------- is_expired ----------

@pytest.mark.parametrize("days_valid", [0, -1])
def test_non_positive_validity_is_expired(days_valid):
    # days_valid <= 0 -> True
    assert is_expired(10, 5, days_valid) is True


@pytest.mark.parametrize("today, start, days_valid, expected", [
    (20, 5, 10, True),    # 15 days elapsed > 10 -> expired
    (12, 5, 10, False),   # 7 days elapsed -> still valid
    (15, 5, 10, False),   # boundary: exactly 10 days is still valid
    (16, 5, 10, True),    # boundary + 1 -> expired
])
def test_expiry_window(today, start, days_valid, expected):
    assert is_expired(today, start, days_valid) is expected
