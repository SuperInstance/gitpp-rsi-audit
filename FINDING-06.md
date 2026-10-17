# Finding 6 — the audit is stronger than claimed, but the gate is never exercised as a rejection

Refining Finding 5 after reading `audit.py` properly. Two things I got
wrong in my own favour-of-the-paper reading, and one residual that is
real.

## Correction to my own correction: the audit is not just arithmetic

I wrote in Finding 5 that the audit "recomputes the gate expression and
asserts it matches the recorded flag," implying it trusts
`m['dev']`. It does not.

`audit.py:104`:

```python
def compare_summary(actual, claimed, where):
    for key, value in actual.items():
        check(abs(value - claimed[key]) < 1e-8, where + ': summary ' + key + ' differs from raw episodes')
```

`actual` comes from re-reading the raw episode `.jsonl` files
(`episode_file(...)`). So the chain is:

    raw episodes → re-derived summary → compared to recorded summary
                 → gate recomputed from the verified summary
                 → asserted equal to the recorded `promoted` flag

The promotion verdict is therefore anchored to raw rollouts, not to a
stored number. Someone cannot quietly inflate `newdev['success_rate']`
in the manifest to force a promotion; the audit recomputes it from the
episodes and the check fails. `compare_summary` is called on
`old_old` and `new_new` at `audit.py:240`, immediately before the gate
assertion at `:242`.

**That is a real receipt for the gate**, and it is stronger than the
paper's prose claims anywhere. My Finding 5 undersold it; this
corrects that.

## The residual: the gate is never exercised as a rejection

`grep` for `promotion_gain` / `promoted` across `tasks/gui/tests/`
returns nothing. No unit test drives the gate to `False`.

This is the same negative-control discipline that `negctl` applies on
the git.pp side, and the gap is the same shape: a gate is only known to
work if it has been observed to refuse.

Consider what is untested. The expression is:

```python
promoted = (newdev.success - olddev.success >= 0.04) \
       and (newdev.seconds <= olddev.seconds * 1.2)
```

Three behaviours are untested:

1. **A gain below 0.04 is rejected** — the primary path.
2. **A gain above 0.04 with cost above 1.2× is rejected** — the clause
   that makes this a *joint* gate rather than an accuracy gate. This is
   the interesting one, because it is the clause that implements §2.5's
   claim that the pair is the unit: a better-but-dearer system is
   refused.
3. **A tie at exactly 0.04 / exactly 1.2×** — boundary behaviour with
   `>=` and `<=`, where an off-by-one silently flips retention.

There is also no published artefact showing a run in which promotion
was **refused**. The gate may well have fired correctly in practice;
nothing in the public record shows it refusing anything.

## Why this is worth raising, precisely

Not because a missing unit test invalidates the GUI result. The 2×2
factorial, the sealed-test discipline (`test_not_opened_yet: True`,
`all_versions_frozen_before_test: True`), and the hash-verified
training lineage are careful work, and CI runs
`reproduce_reported_statistics.py` and `verify_release.py`.

Because the paper's central claim is that **retention must fail
closed**, and the released evidence for that is a passing path. The
paper's own prose is where this goes wrong (Finding 3: Eq. 17 permits
failing open on an unevaluated check). The code is where it goes
right. And the one artefact that would demonstrate fail-closed
behaviour — a refused promotion, or a test that asserts refusal — is
the one that is not there.

The authors have the infrastructure to fix this in an afternoon: the
gate is a pure function of two summaries and two protocol constants,
`protocol.py` already exposes the thresholds, and `audit.py` already
does exactly this kind of assertion. A single fixture with
`success_gain=0.02, cost_ratio=1.5` and `assert not promoted(...)` would
close it.

## Summary of the audit, corrected

| | my claim | status after reading the code |
|---|---|---|
| F3 | Eq. 17 wording permits failing open | **HOLDS** — prose only; code fails closed |
| F4 | retention unreported / never fires | **WRONG** — real gate, thresholds, audit, 2×2 |
| F5 | GUI gate is real but thinly evidenced | **WRONG in the paper's favour again** — audit re-derives from raw episodes |
| F6 | — | gate never exercised as a **rejection**; no test drives it to False |
