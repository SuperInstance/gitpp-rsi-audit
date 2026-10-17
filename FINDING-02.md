# Finding 2 — the paper applies two opposite defaults for "not known"

This is the sharpest thing in the audit, and it is an *internal*
inconsistency rather than an omission, which makes it a stronger claim.

## Where the paper is rigorous

§2.4, on world-model reliability:

> Reliability is assessed from feedback history H_k using this version
> rule and the candidate range considered in cycle k
> (Eq. 10, $\rho^W_k \in \{$reliable, unreliable, insufficient$\}$)

> Because feedback comes from selected candidates, its conclusions are
> limited to the observed and covered candidate range. **Insufficient
> coverage yields an insufficient assessment rather than evidence of
> reliability** and does not activate the adaptation trigger.

That is exactly right, and it is a good piece of epistemics. Feedback
only ever arrived from candidates the *old* policy proposed, under the
*old* predictor's rankings. Measuring agreement inside that region says
nothing about behaviour outside it. So the paper refuses to promote
absence-of-evidence into evidence-of-safety.

The three-valued enum exists purely to make that refusal expressible.
`unreliable` and `insufficient` are separated so that "we don't know"
can never be silently collapsed into "it's fine."

## Where the paper is not rigorous

§2.5, Eq. 17:

> When at least one component changes, the pair decision compares the
> assembled candidate with the current pair under the same prescribed
> evaluation conditions; **otherwise G_k^pair = 1 without a new
> evaluation**

Here, "we don't know" is *promoted to a pass*.

## Why the two are not the same situation

They look like mirror images and are not. The reliability trigger has a
genuine unknown: Eq. 10's assessment can return `insufficient` because
coverage is thin, and the paper handles that explicitly.

The pair gate's "otherwise" branch, as shown in Finding 1, is reachable
only when the candidate pair is **identical** to the current pair. So
$G^{\text{pair}} = 1$ is not a guess — it is trivially true.

**But the paper justifies it by what was skipped, not by what is true
of the candidate.** The sentence's stated reason is "without a new
evaluation," which reads as *we didn't check, so assume pass*. Under
that reading the same default is wrong in a neighbouring case the text
does not discuss: what if a pair check was *attempted* and could not be
completed — insufficient budget, a missing compatibility set
$\mathcal{D}_{\text{compat},k}$, a crashed harness? Then the honest
value is `insufficient`, and the paper has given no symbol for it.

Eq. 17's $Q_{\text{pair}}$ returns a bit. Eq. 10's
$\operatorname{Reliability}$ returns three values. The paper needed the
third value in one place and did not provide it in the other.

## What this costs

A retention gate is exactly the component that should be hardest to
pass. Two of the paper's five applications report results consistent
with retention never firing:

- **Laboratory planning**: five consecutive versions, evaluated in
  development order, monotone improvement 21.80% → 46.01%. If no
  version had been rejected, the gate never bound.
- **GUI**: the "adapted" configuration is *worse* on the error
  diagnostic than baseline (21 incorrect submissions vs 9) while
  better on success. Whatever retained it, it was not a
  conservative gate.

Neither is evidence of a bug. Both are consistent with a gate whose
acceptance criteria are, in the paper's own words, "specified for the
application" and therefore unreported. A reader cannot tell whether
retention rejected anything at all.

## The one-sentence fix

Give $Q_{\text{pair}}$ the same three-valued enum as
$\operatorname{Reliability}$, and state the skip as a property of the
candidate rather than of the procedure:

> $Q_{\text{pair}}$ returns *accept*, *reject*, or *unresolved*. When
> neither component changed the candidate pair is identical to the
> current pair, so the comparison is vacuous and the result is
> *accept* by construction — not by default. An *unresolved* pair
> check retains the current pair, matching Eq. 11's treatment of
> insufficient evidence.

That last clause is the one that matters: it makes a crashed or
unfunded pair check fail **closed**, which is the same posture the
paper already takes at Eq. 11 and the opposite of the posture Eq. 17's
wording implies.
