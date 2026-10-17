# Finding 1 — Eq. 17's fallback is not a fallback

Read the retention rule as written:

> When at least one component changes, the pair decision compares the
> assembled candidate with the current pair under the same prescribed
> evaluation conditions; **otherwise G_k^pair = 1 without a new
> evaluation**

So the pair check is skipped — and **assumed to pass** — exactly when
neither component changed. That looks safe, because if nothing was
proposed, there is nothing to reject.

It is not the same case. Consider the state where:
- $u^\pi_k = 1$ and $G^\pi_k = 1$ (policy improved, passed its check)
- $u^W_k = 1$ and $G^W_k = 0$ (predictor failed its check)

Then by Eq. 15–16: $\bar\theta_{k+1} = \theta'_{k+1}$ and
$\bar\phi_{d,k+1} = \phi_{d,k}$ — so *a component changed*, and Eq. 17
does require the pair comparison. Good, that path is covered.

Now the other order:
- $u^\pi_k = 1$, $G^\pi_k = 1$ — policy changed
- $u^W_k = 0$ (adaptation simply not enabled this cycle)

Same thing: $\bar\phi = \phi_{d,k}$, one component changed, pair check
runs. Covered.

So the "otherwise" branch is reached only when **both**
$\bar\theta = \theta_k$ and $\bar\phi = \phi_{d,k}$, i.e. the candidate
pair is bit-identical to the current pair. In that state
$G^{\text{pair}} = 1$ is correct, and Eq. 18 returns the same pair it
already had.

**The rule is sound.** But the paper never states *why* it is sound.
As written, "otherwise" reads as "if the pair check wasn't run, assume
it passed," and the safety of that reading depends entirely on an
argument the text does not make. An implementer who takes the sentence
at face value and writes:

```python
if not pair_evaluated:
    G_pair = 1          # "no new evaluation needed"
```

is correct here — and only by coincidence of the antecedent.

A safer statement is available and costs one sentence: the check is
skipped **because the candidate pair is identical to the current pair,
so the comparison is vacuous**. As written, the skip is justified by
*what was not done* rather than by *what is true of the candidate*.
