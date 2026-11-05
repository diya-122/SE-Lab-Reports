# Lab 6: Code and Branch Coverage Analysis — `coupon_validator.py`

SRN: PES1UG24AM096

## Results

| Test file | Tests | Line coverage | Branch coverage | Missing |
|-----------|-------|---------------|-----------------|---------|
| `test_coupon_validator.py` (starter) | 2 | 28% (23 of 32 lines missed) | 23% overall | lines 3, 7–18, 22–30, 36 |
| `CodeCoverageTest_PES1UG24AM096_coupon_validator.py` | 13 | **100%** | 98% | branch `25->23` |
| `BranchCoverageTest_PES1UG24AM096_coupon_validator.py` | 27 | **100%** | **100%** (24/24) | — |

Commands used:

```
coverage run -m pytest CodeCoverageTest_PES1UG24AM096_coupon_validator.py
coverage report -m
coverage run --branch -m pytest BranchCoverageTest_PES1UG24AM096_coupon_validator.py
coverage report -m
```

Screenshots are in `screenshots/`.

## Line coverage vs. branch coverage

The code coverage tests run every line of `coupon_validator.py`, so line coverage is 100%. But the branch report still shows one partial branch, `25->23`, in `best_discount`:

```python
for code in codes:
    value = coupon_discount(...)
    if value > best:      # line 25
        best = value
```

Every test that reaches line 25 has a coupon that *beats* the current best, so the `False` outcome (jump straight back to line 23 without updating `best`) never runs. If that path were broken, for example if `best = value` ran unconditionally, line coverage would still say 100%.

The branch coverage tests close that gap and add cases line coverage doesn't require:

- **Both outcomes of every `if`**: e.g. a weaker coupon after a stronger one (`["FLAT100", "WELCOME10"]`), and coupons that are all zero.
- **The loop running zero times**: `best_discount([], ...)` returns 0.
- **Boundary values** where `<`, `<=`, `>` and `>=` matter: cart exactly 500 (WEEKEND20 still 20%), cart exactly 300 (FLAT100 not applied), best exactly equal to the 40% cap, and a coupon used on exactly its last valid day.
- **Edge inputs**: negative cart totals, negative validity, and case sensitivity (`"Sat"`, `"welcome10"` are not recognised).

## Observations

- Codes and day names are case-sensitive: `"Sat"` is treated as a weekday and `"welcome10"` is unknown. The tests document this current behaviour.
- `is_expired` treats a coupon as still valid on exactly day `start + days_valid`, and only expired the day after.
