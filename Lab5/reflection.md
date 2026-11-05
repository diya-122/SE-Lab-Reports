# Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style issues (missing spaces, inline comment spacing, blank lines) and most Pylint convention messages (docstrings, snake_case names, the unnecessary `else`). Each message points to an exact line and the fix is mechanical. Renaming functions took a little care because every call site in `main()` had to change too.

The hardest was the mutable default argument (`guests=[]`). Pylint reports it as a single warning, but it was causing a real bug: both events shared one guest list, so the Alumni Dinner was reported as full and Meena was turned away even though nobody had registered for it. Understanding *why* the output was wrong took more thought than the one-line fix. The `os.system` replacement was also non-trivial: swapping to `subprocess` made Bandit raise three new low-severity warnings, so I had to resolve the executable path, validate the event name, and then decide which remaining warnings were acceptable.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes, or at least warnings that don't apply in context:

- **Bandit B404 / B603** flag *any* use of `subprocess`, even after it is called safely with a list of arguments, no shell, an absolute executable path and validated input. I reviewed them and suppressed them with targeted `# nosec B404` / `# nosec B603` comments, with the reason written on the line above.
- **Bandit B311** (`random.choice`) is arguably a false positive for a casual lucky draw, since it's not cryptography. Switching to `secrets.choice` cost nothing, so I fixed it anyway.

On the other side, the tools missed things a human reviewer would catch: none of them noticed that the program's *output* was wrong — Pylint only said "dangerous default value", not "your seat counts are incorrect". Running the program and reading the output was essential.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint from the editor on save, and add a `pre-commit` hook that runs Flake8, Pylint and Bandit so bad code never reaches a commit.
- **In CI:** run all three on every pull request (e.g. a GitHub Actions job), fail the build on any Bandit High/Medium finding, Flake8 error, or a Pylint score below a threshold such as 9.5.
- **Configuration:** keep the rules in a shared config (`.pylintrc`, `setup.cfg`/`.flake8`, `.bandit`) so the whole team gets the same results, and require a written justification for every `# nosec` or `# pylint: disable`.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Correctness:** events no longer share guests. Alumni Dinner now shows 1 seat left and accepts Meena; previously it showed 0 and rejected her.
- **Security:** no shell injection through event names, no arbitrary code execution from a tampered save file (JSON instead of pickle), and an unpredictable lucky draw.
- **Readability:** consistent snake_case names, a docstring on every function, PEP 8 formatting, and flatter control flow.
- **Robustness:** `guest_report` now actually honours `sort_order` and rejects invalid values instead of silently ignoring them; the module can be imported without running the demo.
- **Measured:** Pylint rose from 4.64 to 10.00/10, Bandit went from 4 issues to none, and Flake8 from 4 issues to none.
