"""Line (statement) coverage tests for coupon_validator.py.

Goal: execute every line of coupon_validator.py at least once.
Each test is labelled with the line(s) it is there to reach.
"""
import pytest
from coupon_validator import coupon_discount, best_discount, is_expired


# ---------- coupon_discount ----------

def test_empty_cart_raises():
    # line 3: cart_total <= 0
    with pytest.raises(ValueError):
        coupon_discount("WELCOME10", 0, True, "mon")


def test_welcome_coupon_new_user():
    # line 6: new user gets 10%
    assert coupon_discount("WELCOME10", 200, True, "mon") == 20


def test_welcome_coupon_existing_user():
    # line 7: existing user gets nothing
    assert coupon_discount("WELCOME10", 200, False, "mon") == 0


def test_weekend_coupon_big_cart():
    # line 11: weekend and cart >= 500 -> 20%
    assert coupon_discount("WEEKEND20", 600, False, "sat") == 120


def test_weekend_coupon_small_cart():
    # line 12: weekend and cart < 500 -> flat 50
    assert coupon_discount("WEEKEND20", 300, False, "sun") == 50


def test_weekend_coupon_on_weekday():
    # line 13: WEEKEND20 on a weekday -> 0
    assert coupon_discount("WEEKEND20", 600, False, "mon") == 0


def test_flat100_above_threshold():
    # line 16: cart > 300 -> 100 off
    assert coupon_discount("FLAT100", 400, False, "mon") == 100


def test_flat100_below_threshold():
    # line 17: cart <= 300 -> 0
    assert coupon_discount("FLAT100", 200, False, "mon") == 0


def test_unknown_code():
    # line 18: unrecognised code -> 0
    assert coupon_discount("BOGUS", 200, False, "mon") == 0


# ---------- best_discount ----------

def test_best_discount_picks_highest():
    # lines 22-27, 30: loop updates best, result under the cap
    codes = ["WELCOME10", "FLAT100"]
    assert best_discount(codes, 400, True, "mon") == 100


def test_best_discount_capped_at_40_percent():
    # line 29: best (50) exceeds cap (100 * 0.4 = 40)
    assert best_discount(["WEEKEND20"], 100, False, "sat") == 40


# ---------- is_expired ----------

def test_zero_validity_expired():
    # line 35: days_valid <= 0
    assert is_expired(10, 5, 0) is True


def test_expired_after_validity():
    # line 36: past the validity window
    assert is_expired(20, 5, 10) is True
