# Finding 4 — the retention gate is unreported, and the results are consistent with it never firing

The paper's contribution is a *retention* protocol. Retention only
matters if it rejects things. So: do the reported experiments contain
any evidence that it did?

## The code-repair ablation is the one clean test, and it passes

§3.1 is the strongest experiment in the paper and the only one where
the components are genuinely isolated:

| method | hidden all-pass | online calls/task |
|---|---|---|
| Random-K | 26.0% | 3.72 |
| Capacity-matched static verifier | 26.3% | 3.72 |
| RSI-Anything, fixed WM | 29.2% | 3.71 |
| RSI-Anything, WM adaptation | 31.2% | 3.72 |

The coder is held fixed, four candidates per round, one executed,
budgets matched to within 0.01 online calls/task. Paired gain over the
static verifier is +2.83pp, 95% interval [+0.17, +5.50]. Ranking
accuracy 66.5% → 72.8%, Brier 0.488 → 0.358.

This is a real ablation and the mechanism is visible, not just the
outcome. Two things deserve credit:

1. **The lower bound is near zero.** [+0.17, +5.50] is not a
   comfortable margin, and the paper reports it rather than the point
   estimate alone.
2. **The mechanism check.** Ranking accuracy and Brier move in the
   predicted direction. A result that only showed the outcome would be
   consistent with luck; showing the predictor got *better at
   ranking* is the intermediate quantity the theory says should move.

**This experiment does not depend on the retention gate**, and should
not be credited to it. The coder is fixed; only W1 is adapted; the
"retention" question never arises because there is no policy change to
retain.

## The two experiments that SHOULD involve retention report nothing about it

### Laboratory planning — five versions, monotone, no rejections reported

21.80% → 38.03% → 41.99% → 44.56% → 46.01%, five consecutive 4B
policy versions from one self-improvement process, evaluated in
development order on the same 200-task F200 benchmark.

This is the paper's only *multi-round* evidence, and it is the weakest
inferential structure in the paper:

- **No control arm.** There is no version trained the same way and
  *not* retained, so the sequence cannot distinguish retention from
  simply having trained five times.
- **Development order, not random order.** Evaluated as produced, so
  any drift in the benchmark or in the process maps monotonically onto
  the curve.
- **Spacing is "schematic"** (Figure 5c), so the x-axis carries no
  information and the curve's shape is a drawing choice.
- **The margin over the reference is 0.69pp** (46.01% vs 45.32% for
  Actor–Simulator–Selector), with no interval at n=200.

A monotone curve from one process is the *expected* shape whether or
not the gate ever fired. If all five versions passed — which is entirely
consistent with the reported numbers — retention is doing no work in
this experiment, and the paper is implicitly attributing to it a gain
that training alone would produce.

### GUI — the retained configuration is worse on the error diagnostic

The "adapted" configuration: 96% success (up from 51% baseline), fewer
actions (2.93 vs 5.30), and **21 incorrect-submission episodes vs 9 at
baseline**. The final configuration reaches 99% success with 3.21
actions and 1 incorrect submission.

So the intermediate retained state is strictly worse than baseline on
the diagnostic that catches confidently-wrong behaviour, while better
on success. Whatever retained it, it was not a conservative gate — or
the gate's criteria weighted success heavily enough to accept a
configuration that nearly doubled the error rate.

The paper reports this honestly in the text. It does not explain the
mechanism, and it does not say whether the adapted configuration was
the result of a *retention decision* or of simply continuing the
process.

## The gap underneath all of it

§2.5 says each check *"returns one only when its specified criteria are
met"* and that the evaluation specification *"fixes the task metrics,
prediction checks, constraints, feedback allowance, and acceptance
thresholds."* None of those thresholds are reported for any domain.

A retention protocol is only as real as its rejections. The strongest
version of the paper's claim would be a table like:

| application | updates proposed | rejected by component check | rejected by pair check | net retained |
|---|---|---|---|---|
| code repair | — | — | — | coder fixed |
| lab planning | 5 | ? | ? | ? |
| GUI | ? | ? | ? | ? |

Without it, a reader cannot tell whether the gate is a load-bearing
mechanism or a formality that approved everything it was shown.

This connects directly to Finding 3. If the gate is permissive by
construction, then the reported gains are gains from the *selection and
adaptation* pathways, which §3.1 does support, and the retention
argument is simply unmade. That is a fixable paper, not a broken one —
but the claim and the evidence are currently mismatched in scope.

## The honest summary

The paper's **selection** contribution is well-evidenced: one clean
ablation, matched budgets, a mechanism check, and a reported interval
with a near-zero lower bound.

Its **retention** contribution — the thing the title and §2 are about —
is specified but not demonstrated, and in one place (§2.5's wording) is
specified in a form that permits failing open.
