"""Hypothesis fuzz tests for coupon_validator.py.

Two kinds of test for each function:
  * no-crash fuzzing: random text (or None) must never raise; invalid
    input should come back as None.
  * property tests: well-formed input must give the right answer, and
    malformed-but-parseable input must be rejected instead of accepted.
"""
import datetime

from hypothesis import given, settings, strategies as st
from coupon_validator import split_code, most_expensive, expiry_days

settings.register_profile("lab", max_examples=300, deadline=None)
settings.load_profile("lab")

FUZZ = st.text() | st.none()
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ---------------------------------------------------------------- split_code

@given(FUZZ)
def test_split_code_no_crash(s):
    try:
        split_code(s)
    except Exception as e:
        assert False, f"split_code crashed on {s!r} with: {e!r}"


@given(st.text(alphabet=LETTERS, min_size=1, max_size=10),
       st.integers(min_value=0, max_value=10**6))
def test_split_code_valid_round_trip(prefix, value):
    assert split_code(f"  {prefix}-{value} ") == (prefix.upper(), value)


@given(st.sampled_from(["SAVE-", "-20", "SAVE--20", "SAVE-20-5", "SAVE-2.5",
                        "SAVE-+20", "SAVE- 20", "SAVE-2_0", "SAVE-٣",
                        "S4VE-20", "", "   "]))
def test_split_code_rejects_malformed(code):
    # These used to crash, or were silently accepted by int().
    assert split_code(code) is None


# ------------------------------------------------------------ most_expensive

@given(FUZZ)
def test_most_expensive_no_crash(s):
    try:
        most_expensive(s)
    except Exception as e:
        assert False, f"most_expensive crashed on {s!r} with: {e!r}"


@given(st.lists(st.floats(min_value=0, max_value=1e9, allow_nan=False),
                min_size=1, max_size=20))
def test_most_expensive_matches_max(prices):
    csv = ",".join(repr(p) for p in prices)
    assert most_expensive(csv) == max(prices)


@given(st.sampled_from(["nan", "inf", "-inf", "1,nan,3", "1,inf", "-5",
                        "10,-1", "1e400", "abc", "1,,3", ",", ""]))
def test_most_expensive_rejects_bad_prices(csv):
    # nan / inf / negative / overflowing / empty prices are not real prices.
    assert most_expensive(csv) is None


# --------------------------------------------------------------- expiry_days

@given(FUZZ)
def test_expiry_days_no_crash(s):
    try:
        expiry_days(s)
    except Exception as e:
        assert False, f"expiry_days crashed on {s!r} with: {e!r}"


@given(st.dates(min_value=datetime.date(2024, 1, 1),
                max_value=datetime.date(9999, 12, 31)))
def test_expiry_days_valid_dates(d):
    expected = (d.year - 2024) * 365 + (d.month - 1) * 30 + d.day
    assert expiry_days(d.isoformat()) == expected


@given(st.integers(min_value=2024, max_value=2100),
       st.integers(min_value=-50, max_value=100),
       st.integers(min_value=-50, max_value=100))
def test_expiry_days_rejects_impossible_dates(year, month, day):
    try:
        datetime.date(year, month, day)
        real_date = True
    except ValueError:
        real_date = False
    result = expiry_days(f"{year}-{month:02d}-{day:02d}")
    if real_date:
        assert isinstance(result, int) and result >= 1
    else:
        assert result is None, f"accepted impossible date {year}-{month}-{day}"


def test_expiry_days_rejects_before_2024():
    assert expiry_days("2023-12-31") is None
