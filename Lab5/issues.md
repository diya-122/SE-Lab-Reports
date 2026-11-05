# Issues Found and Fixed — `event_manager.py`

Line numbers refer to the original file (commit `b6bf665`). Ordered by severity, highest first.

| # | Issue | Type | Tool / Code | Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|----------|---------|-------------|--------------|
| 1 | Shell command injection | Security | Bandit B605 | High | 56 | `os.system("lp badges_" + eventName + ".txt")` runs through a shell, so an event name such as `x; rm -rf ~` would execute extra commands. | Replaced with `subprocess.run([...], check=False)` (no shell, list arguments), resolved `lp` to an absolute path with `shutil.which`, and validated the event name with an allow-list regex. |
| 2 | Unsafe deserialisation | Security | Bandit B301 / B403 | Medium (B301), Low (B403) | 2, 44–51 | `pickle.load` can execute arbitrary code if `events.pkl` is tampered with. | Switched save/load to `json` with explicit `encoding="utf-8"`; file is now `events.json`. Removed the `pickle` import. |
| 3 | Mutable default argument (runtime bug) | Bug | Pylint W0102 | Medium | 9–11 | `guests=[]` is created once and shared by every event. Both events used the same list, so the Alumni Dinner (capacity 2) was "full" after Asha and Ravi registered for the Tech Meetup, Meena was rejected, and its seat count showed 0. | Default changed to `guests=None`; a fresh list (`list(guests) if guests else []`) is made per event. Alumni Dinner now correctly shows 1 seat left and accepts Meena. |
| 4 | Insecure random generator | Security | Bandit B311 | Low | 72 | `random.choice` is predictable; a lucky draw should not be guessable. | Replaced with `secrets.choice`. |
| 5 | Subprocess follow-up warnings | Security | Bandit B404 / B603 / B607 | Low | 56 (after fix 1) | After moving to `subprocess`, Bandit flags the import, the call, and the partial path `lp`. | B607 fixed by using the absolute path from `shutil.which`. B404/B603 reviewed and suppressed with targeted `# nosec` comments, with the reasoning on the line above (no shell, fixed argument list, validated input). |
| 6 | Unused argument | Bug / Quality | Pylint W0613 | Medium | 39–41 | `guestReport` accepts `sortOrder` but ignores it, so callers silently get the same result for any value. | Implemented it: `"name"` sorts alphabetically, `"registration"` keeps signup order, anything else raises `ValueError`. |
| 7 | Non-snake_case names | Convention | Pylint C0103 | Low | 9–54 | Function and argument names use camelCase (`createEvent`, `eventName`, …). | Renamed to PEP 8 snake_case (`create_event`, `event_name`, …) and updated all call sites. |
| 8 | Missing docstrings | Convention | Pylint C0114 / C0116 | Low | 1, all functions | No module or function docstrings. | Added a module docstring and a docstring for every function. |
| 9 | Unnecessary `else` after `return` | Refactor | Pylint R1705 | Low | 33–36 | `else:` after a `return` adds nesting for no reason. | Removed the `else` and de-indented. |
| 10 | Code runs on import | Quality | Review | Low | 79 | `main()` at module level runs the demo whenever the file is imported. | Wrapped in `if __name__ == "__main__":`. |
| 11 | Missing whitespace after `,` | Style | Flake8 E231 | Low | 61 | `"Rooftop",2` | Added a space: `"Rooftop", 2`. |
| 12 | Missing whitespace around operator | Style | Flake8 E225 | Low | 66 | `left=seatsLeft(...)` | Changed to `left = ...`. |
| 13 | Inline comment spacing | Style | Flake8 E261 | Low | 75 | Only one space before `#`. | Two spaces before the inline comment. |
| 14 | Blank lines before top-level code | Style | Flake8 E305 | Low | 79 | Only one blank line after the last function. | Added a second blank line. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.64 / 10 (30 messages) | **10.00 / 10** |
| Bandit | 4 issues (1 High, 1 Medium, 2 Low) | **No issues identified** |
| Flake8 | 4 issues | **0 issues** |

Reports are in `reports/before/` and `reports/after/`.

## Commits

1. `446d52f` — Bandit fixes (pickle → json, `os.system` → safe `subprocess`, `random` → `secrets`)
2. `a2ce928` — Flake8 fixes (E231, E225, E261, E305)
3. `d45f7ab` — Pylint fixes (mutable default, naming, docstrings, unused argument, no-else-return, main guard)
