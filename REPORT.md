# Audit of arXiv:2610.13912v1 — RSI-Anything

An independent audit applying a "reading-room" method: give the text to
readers who implement its load-bearing mechanism without consulting each
other, then check whether the readers agree. Disagreement locates a
clause the text does not determine. Full artifacts in this repo.

**Scope.** The paper's prose, plus the public code at
`github.com/Gen-Verse/RSI-Anything` (pushed 2026-10-13). No complaint
about results, models, or baselines — the ablation in §3.1 is well
constructed and the 2×2 pair evaluation in the GUI code is better
evidence than the paper claims. This is about whether §2's retention
protocol is unambiguous.

## 1. Eq. 17's fallback is keyed on procedure, not on the candidate

> When at least one component changes, the pair decision compares the
> assembled candidate with the current pair under the same prescribed
> evaluation conditions; otherwise G_k^pair = 1 without a new evaluation

Read literally, this assigns a pass when the check **did not happen**.

Two readers of Eqs. 15–18, written from the text alone:

| case | literal | fail-closed |
|---|---|---|
| both changed, check ran | G=1 | G=1 |
| policy changed, model not | G=1 | G=1 |
| model changed, policy not | G=1 | G=1 |
| neither changed | G=1 | G=1 |
| **policy changed, check SKIPPED** | **G=1** | **G=0** |
| **both changed, check INCOMPLETE** | **G=1** | **G=0** |

2 of 6 split, and the split is entirely about unchecked cases.
Adjudicated on the verbatim text behind a calibration gate (0.960 true /
0.020 false / 0.070 out-of-scope): literal **0.650**, fail-closed
0.160. The literal reading wins.

The intent is not in question — §2.4 is explicit that "insufficient
coverage yields an insufficient assessment **rather than evidence of
reliability**," and Eq. 11's three-way AND is fail-closed throughout.
**The code is fail-closed too** (`rsi.py:53` promotes only under an
ANDed, thresholded rule). So this is a prose bug with a correct
implementation behind it.

**Suggested wording.** `Q_pair` returns *accept* / *reject* /
*unresolved*. When neither component changed the candidate pair is
identical to the current pair, so the comparison is vacuous and the
result is *accept* by construction rather than by default. An
*unresolved* pair check retains the current pair, matching Eq. 11.

## 2. Retention is demonstrated in GUI and under-reported in the paper

The released GUI code contains a real, concrete gate
(`tasks/gui/src/rsi_anything_gui/rsi.py:53`):

```python
promoted = newdev['success_rate'] - olddev['success_rate'] >= protocol['promotion_gain'] \
       and newdev['effective_seconds'] <= olddev['effective_seconds'] * protocol['promotion_cost_ratio']
```

with `promotion_gain: .04` and `promotion_cost_ratio: 1.2`
(`protocol.py:32`), applied to the assembled (world, policy, controller)
triple — the pair structure §2.5 describes.

Two things the paper does not surface:

- **A 2×2 factorial of the pair** (`rsi.py:57`): every combination of
  old/new world model × old/new policy is rolled out separately. That
  is a direct experimental test of the claim that the pair is the right
  unit, and it is exactly the measurement §2.5 argues component scoring
  cannot replace.
- **An audit anchored to raw rollouts** (`audit.py:104,242`):
  `compare_summary()` re-reads the episode files and re-derives the
  summary before the gate is recomputed, so the verdict cannot be
  inflated by editing a manifest.

Worth a sentence or two in §3.2 — it is the strongest evidence the
paper has for its central claim.

## 3. The gate is never exercised as a rejection

No test under `tasks/gui/tests/` drives the gate to `False`, and no
published artefact shows a refused promotion. Untested: a sub-0.04 gain
is rejected; a ≥0.04 gain at >1.2× cost is rejected (the clause that
makes this a *joint* rather than an accuracy gate); and behaviour at the
exact boundaries, where `>=` vs `<=` silently flips retention.

The paper's thesis is that retention must fail closed. The released
evidence for that is a passing path.

**Suggested.** One fixture — `success_gain=0.02, cost_ratio=1.5`,
`assert not promoted(...)`. The gate is a pure function of two summaries
and two protocol constants, and `audit.py` already does this kind of
assertion.

## 4. Laboratory planning has no gate and no control arm

Of four tasks, only GUI implements retention. `code_repair`'s
`keep_current` is a **ranked candidate** competing in the same
predicted-outcome ranking as four patches (`evaluation.py:108`) — that
is selection, which §3.1's ablation supports, and it is not credited
as retention.

Laboratory planning is the only multi-round result and the only place a
gate plainly belongs, yet the released code has no promotion logic. The
five versions run 21.80% → 46.01% in development order with no control
arm, and the margin over the Actor–Simulator–Selector reference is
0.69pp at n=200 with no interval. A monotone curve from one process is
the expected shape whether or not a gate fired. §5 already concedes that
joint multi-round evaluation is needed.

## What is not in dispute

- **§3.1 is a clean ablation.** Coder fixed, four candidates, one
  executed, budgets matched to 0.01 online calls/task, and — the part
  that makes it real — a mechanism check: ranking accuracy 66.5→72.8%
  and Brier 0.488→0.358 are the intermediate quantities the theory says
  should move.
- **The interval is reported honestly**: +2.83pp, [+0.17, +5.50], with
  a lower bound near zero. Reporting that rather than the point estimate
  is the right call.
- **§2.4's version rule is a genuinely good piece of epistemics**:
  reliability must be assessed using predictions attributable to the
  current model version, preventing error measurements from earlier
  generations being pooled into one number. That clause prevents a
  large and common failure and is worth keeping prominent.
- **The GUI intermediate result is reported against the authors'
  interest** — the adapted configuration nearly doubles incorrect
  submissions while improving success.

## Method, stated so it can be criticised

The audit's instrument is Jev, which returns a calibrated probability
that a framed claim is supported by supplied text, and is instructed to
decline rather than guess. It is gated on three controls before any real
clause is scored: 0.960 (true claim stated), 0.020 (false claim
contradicted by the text), 0.070 (true claim, never mentioned). An
adjudicator that cannot say "no" cannot adjudicate, and one that
proves nothing about a false claim is noise.

Limitation worth stating: the adjudication is a probability, not an
argument, and Finding 1's 0.650 is not overwhelming. It is enough to
establish that the wording *permits* the permissive reading, which is
the claim being made — not that the authors intended it.

A caveat on the whole approach, from our own practice: two earlier
audits in this series produced confident wrong numbers from a broken
search and from paraphrased rather than quoted text. Both are recorded
in this repo's history rather than removed, because the second one
silently changed a verdict.

---

Artifacts: `FINDING-01..06.md` (full derivations, including the
corrections to our own earlier claims), `reader.py` (the two
implementations), `jev-adjudicate.py` (calibration + adjudication).
