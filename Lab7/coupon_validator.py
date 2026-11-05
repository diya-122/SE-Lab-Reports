"""Coupon helpers, hardened against invalid input found by fuzz testing.

Every function returns None for input it cannot handle instead of raising,
so callers (and the interactive demo) never crash on bad data.
"""
import datetime
import math
import re

CODE_PATTERN = re.compile(r"([A-Za-z]+)-([0-9]+)")
PRICE_PATTERN = re.compile(r"(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
DATE_PATTERN = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
BASE_YEAR = 2024


def split_code(code):
    """Split 'save-20' into ('SAVE', 20).

    Returns None unless the code is letters, one dash, then ASCII digits.
    """
    if not isinstance(code, str):
        return None
    match = CODE_PATTERN.fullmatch(code.strip())
    if match is None:
        return None
    prefix, value = match.groups()
    return prefix.upper(), int(value)


def most_expensive(prices_csv):
    """Return the highest price in a comma-separated list such as '199,49.5'.

    Returns None if the text is empty or any item is not a finite,
    non-negative number (so 'nan', 'inf', '-5', '1,,3' are all rejected).
    """
    if not isinstance(prices_csv, str):
        return None
    prices = []
    for item in prices_csv.split(","):
        item = item.strip()
        if not PRICE_PATTERN.fullmatch(item):
            return None
        price = float(item)
        if not math.isfinite(price):
            return None
        prices.append(price)
    return max(prices)


def expiry_days(date_text):
    """Return the day count since 2024 for a 'YYYY-MM-DD' date.

    Uses the original formula (365-day years, 30-day months). Returns None
    for malformed text, impossible dates (e.g. 2025-13-45) or years before 2024.
    """
    if not isinstance(date_text, str):
        return None
    match = DATE_PATTERN.fullmatch(date_text.strip())
    if match is None:
        return None
    year, month, day = (int(part) for part in match.groups())
    try:
        datetime.date(year, month, day)
    except ValueError:
        return None
    if year < BASE_YEAR:
        return None
    return (year - BASE_YEAR) * 365 + (month - 1) * 30 + day


def main():
    """Interactive demo; prints a message instead of crashing on bad input."""
    print("==== Running split_code ====")
    user_input = input("Enter a coupon code (e.g. save-20): ")
    result = split_code(user_input)
    if result is None:
        print("Invalid coupon code. Use letters, a dash and a number, e.g. SAVE-20")
    else:
        print("Prefix and Value:", result)

    print("\n==== Running most_expensive ====")
    user_input = input("Enter item prices as CSV (e.g. 199,49.5,320): ")
    result = most_expensive(user_input)
    if result is None:
        print("Invalid price list. Use non-negative numbers separated by commas")
    else:
        print("Most Expensive Item:", result)

    print("\n==== Running expiry_days ====")
    user_input = input("Enter an expiry date as YYYY-MM-DD: ")
    result = expiry_days(user_input)
    if result is None:
        print("Invalid date. Use a real date from 2024 onwards, e.g. 2025-03-15")
    else:
        print("Days Since 2024:", result)


if __name__ == "__main__":
    main()
