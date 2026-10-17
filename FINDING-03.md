# Finding 3 — the wording fails OPEN, against the paper's own intent

## What was measured

Two readers of Eq. 15–18, written from the paper's text alone:

- **Reader A (literal).** Transcribes the equations. The "otherwise"
  branch is keyed on *not pair-evaluated*, matching the sentence's own
  wording ("otherwise G_k^pair = 1 without a new evaluation").
- **Reader B (fail-closed).** Same equations, but the skip is justified
  by the candidate being identical to the current pair, and an
  attempted-but-incomplete check retains the current pair — the posture
  Eq. 11 already takes for insufficient reliability evidence.

Six cases, chosen so the two readings cannot be distinguished except
where they should be:

| case | A (literal) | B (fail-closed) |
|---|---|---|
| both changed, pair check ran | G=1 | G=1 |
| policy changed, model not | G=1 | G=1 |
| model changed, policy not | G=1 | G=1 |
| neither changed | G=1 | G=1 |
| **policy changed, pair check SKIPPED** | **G=1** | **G=0** |
| **both changed, pair check INCOMPLETE** | **G=1** | **G=0** |

**2 of 6 split.** The first four are genuinely agreed — the protocol is
well-defined on the paths everyone exercises. The split is entirely
about what happens when a check is *not* performed.

## Adjudication

Behind the calibration gate (0.960 true / 0.020 false / 0.070
out-of-scope, separation +0.940), on verbatim Eq. 15–18 text:

| reading | score |
|---|---|
| A — literal: "otherwise G_pair = 1", so the new policy is retained | **0.650** |
| B — fail-closed: the text does not settle it | 0.160 |

**The literal reading wins.** This is not a dispute about what the
authors intended — Eq. 11 and the surrounding prose make fail-closed
intent plain. It is a statement about what the *words* permit. An
implementer working from this text, asked "policy changed, pair check
was not run — retain or roll back?", has a defensible path to **accept**,
and the paper's own sentence points at it.

## Why this is the finding worth reporting

A retention gate is the last thing that should be permissive. Its entire
purpose is to stop a changed system from surviving on the strength of a
component check alone — the paper says so directly: *"a policy can
generate candidates for which an otherwise improved predictor is
unreliable."*

Yet the sentence that implements that protection can be read as: **if
the compatibility check did not happen, it passed.** In a research
system those are very different worlds. The first refuses an unverified
coupling. The second accepts one whenever the harness has a bad day,
runs out of budget, or quietly skips a stage.

The asymmetry with Eq. 10 sharpens it. The paper went to real trouble to
give reliability a three-valued enum so that *insufficient* could never
collapse into *reliable* — "insufficient coverage yields an insufficient
assessment **rather than evidence of reliability**." That is a
principle. Eq. 17 then applies the opposite default one section later,
and the only thing preventing it from being a live bug is an argument
the text does not make.

## The fix, in one sentence

> $Q_{\text{pair}}$ returns *accept*, *reject*, or *unresolved*. When
> neither component changed the candidate pair is identical to the
> current pair, so the comparison is vacuous and the result is *accept*
> by construction rather than by default. An *unresolved* pair check
> retains the current pair.

That converts a default into a fact about the candidate, gives the gate
the same third state the reliability trigger already has, and makes a
crashed or unfunded compatibility check fail closed.

## What this is not

This is not a claim that the reported experiments are wrong. Every
domain in §3 describes a working pipeline, and the gains are reported
against matched budgets. The finding is narrower and, I'd argue, more
useful: **the paper's central mechanism is stated in a form that
permits the opposite of its own stated intent, and a reader cannot tell
which form they are implementing.** For a paper whose contribution is a
retention protocol, the protocol should be unambiguous about failing.
