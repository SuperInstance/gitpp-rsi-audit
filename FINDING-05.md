# Finding 5 — CORRECTION to Finding 4, after reading the released code

Finding 4 claimed the retention gate was "unreported" and that the GUI
results were "consistent with it never firing." I then found the code
(`github.com/Gen-Verse/RSI-Anything`, public, 774 stars, pushed
2026-10-13) and checked.

**Finding 4 was wrong about GUI, and wrong in the paper's favour.**
The correction matters more than the original claim, so it gets its own
file.

## GUI has a real, concrete, tested retention gate

`tasks/gui/src/rsi_anything_gui/rsi.py:53`, verbatim:

```python
promoted = newdev['success_rate'] - olddev['success_rate'] >= protocol['promotion_gain'] \
       and newdev['effective_seconds'] <= olddev['effective_seconds'] * protocol['promotion_cost_ratio']
```

Two clauses, ANDed, both fail-closed. Thresholds are concrete
(`protocol.py:32`): `promotion_gain: .04`, `promotion_cost_ratio: 1.2`.
Promotion requires a ≥4pp dev success gain **and** no more than 1.2×
the cost. A new world/policy/controller triple that is more accurate
but more expensive is rejected.

And the gate is applied to the **assembled triple**, not to components
separately — which is exactly the pair-check structure §2.5 describes.
`rsi.py:59` only rebinds the incumbents when `promoted`:

```python
if promoted: incumbent_world=new_world; incumbent_policy=new_policy; incumbent_controller=selected['controller']
```

Two further things I did not expect to find:

1. **A 2×2 factorial evaluation of the pair.** `rsi.py:57` defines
   `combinations = [('old_old',...), ('old_new',...), ('new_old',...),
   ('new_new',...)]` — every combination of old/new world model and
   old/new policy is rolled out separately. This is a *direct
   experimental* test of the claim that the pair is the right unit, and
   it is a stronger test than the paper's prose reports. Isolating each
   component's contribution is precisely what §2.5's pair check says
   cannot be done by scoring components alone.

2. **An independent audit that re-derives the verdict.**
   `audit.py:242`:

   ```python
   check(m['promoted'] == (newdev['success_rate']-olddev['success_rate'] >= protocol['promotion_gain']
        and newdev['effective_seconds'] <= olddev['effective_seconds']*protocol['promotion_cost_ratio']),
         f'RSI {generation}: promotion gate incorrect')
   ```

   The audit recomputes the gate expression and asserts it matches the
   recorded `promoted` flag. That is a receipt for the gate, and it is
   also — usefully — a place where a *substituted* promotion rule would
   be caught.

So: the paper under-reports its own strongest retention evidence. That
is the opposite failure from the one I alleged, and it is worth saying
plainly.

## What survives from Finding 4, and what does not

| claim | status |
|---|---|
| GUI retained a permissive config | **WRONG.** The gate has explicit thresholds and an audit. |
| The gate is "unreported" | **WRONG for GUI.** Reported in code with numbers, if not in the paper. |
| Code-repair gains don't depend on the gate | **HOLDS.** The coder is fixed; only W1 is adapted. |
| Lab-planning curve lacks a control arm | **STILL HOLDS** — see below. |
| Retention needs a rejections table | **STILL HOLDS, and is now sharper.** |

## What the code does confirm, and what it still leaves open

Of four tasks, only GUI implements a retention gate:

| task | gate lines | note |
|---|---|---|
| gui | 12 | real gate, thresholds, audit, 2×2 pair eval |
| code_repair | 0 | `keep_current` is a **ranked candidate**, not a gate outcome |
| laboratory_planning | 0 | five versions, no promotion logic in the released code |
| reaction_optimization | 0 | consistent with the paper — it is search, not retention |

The `code_repair` case is worth being precise about, because it looks
like a gate and is not. `evaluation.py:108` adds `keep_current` as a
fifth *candidate* to the ranking:

```python
candidates = tuple(Candidate(r['candidate_id'], r['code']) for r in raw) + (Candidate('keep_current', code),)
predictions = model.predict(item['problem'], code, feedback, tests, candidates)
choice = choose(predictions)
```

So "do nothing" competes in the same predicted-outcome ranking as four
proposed patches, decided by the same predictor. That is *selection*,
which is what §3.1 credits and which the ablation supports. It is not
retention, and correctly should not be credited as such.

**Laboratory planning is the real gap.** It is the paper's only
multi-round result and the only one where a retention gate is
appropriate, and the released code contains no promotion logic for it.
The five versions run 21.80% → 46.01% in development order with no
control arm, and the paper's own §5 concedes joint multi-round
evaluation is still needed.

## The corrected summary

The paper's retention mechanism is **implemented, thresholded, audited,
and experimentally decomposed by a 2×2 pair evaluation — in GUI — and
reported in code rather than in the paper.** My claim that it was
unsubstantiated was wrong.

What remains is narrower and more specific:

- The retention evidence lives in one task out of four, and the paper's
  prose does not surface the 2×2 result, which is the most direct
  available test of its central theoretical claim.
- Code repair's gains are selection gains and are reported as such.
- Laboratory planning's five-version curve is the only multi-round
  evidence and has no gate, no control arm, and a 0.69pp margin over
  its reference at n=200 without an interval.

## Method note

This is the second time in this audit that checking the artifact rather
than the prose changed the conclusion — the first was Finding 3, where
the *wording* permitted failing open even though the released GUI code
fails closed. Those two findings are not in conflict:

**the code implements the fail-closed gate the paper's prose fails to
state.** That is a writing bug with a working implementation behind it,
which is the cheapest possible kind of bug to fix and the easiest to
misread as a design flaw.
