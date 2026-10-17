# Finding 7 — the v0.4.6 fix was itself incomplete, and only probing it found that

The audit that found a fail-open gate in someone else's paper produced
four spec fixes, pushed as v0.4.6 twenty minutes before this file was
written. The obvious next question is the one a spec author is least
inclined to ask: **is the new text better than the old?**

A specification change is only an improvement if it is at least as
determined as what it replaced. Reading the new clauses again does not
answer that — the words now say what I intended them to say, which is
exactly the condition under which I would fail to notice a second-order
gap. So the fix was probed the same way the original was: candidate
cases where the new text might not settle an answer, then adjudication.

## Five candidates, three real

| # | case | undetermined | concrete answer | verdict |
|---|---|---|---|---|
| C1 | two unclassifiable records contest a key | **0.700** | 0.340 | **real gap** |
| C2 | unclassifiable ancestor of a classifiable — conflict ledger? | — | — | bookkeeping, not ranking |
| C3 | does an unclassifiable record ever reach the ancestry tie-break? | — | — | subsumed by C1/C5 |
| C4 | unrecognised `kind` string vs `null` | — | 0.910 vs 0.070 | **not a gap** |
| C5 | two unclassifiable records, one descends | **0.790** | 0.860 | **real gap, near-tie** |

Calibration gate: 0.950 true / 0.020 false / 0.070 out-of-scope,
separation +0.930.

### C1 — the mixed rule did not cover the unmixed case

The new §5.1 says an unclassifiable record "never displaces a classifiable
one." That settles a contest between an unclassifiable record and a
witness. It says **nothing** about two unclassifiable records contesting
a key, which is precisely the case the clause was written to handle.

**0.700 that the text does not determine it**, against 0.340 for "first
in topo order."

### C5 — the near-tie that matters most

0.790 undetermined vs 0.860 for "the descendant wins."

This is the one worth dwelling on, because of how close it is. §5.1
says ancestry is consulted "only when the two classes are **equal**."
An unclassifiable record has *no class*. So whether two unclassifiable
records are "equal" for the purposes of the tie-break is never stated.

A 0.79/0.86 split is not a verdict — it is the signature of a clause a
careful reader can talk themselves either way out of. **That is exactly
how the original §5.1 gap looked before it was found:** reader2 in the
reading-room adopted a reading the author had not considered, and it
turned out to be wrong. The difference is that this time the tell was a
small score gap rather than a large one, and this time I looked.

If the repaired text is scored and comes back near 0.5 again, that is
the same signal and it should be treated the same way.

### C4 — a candidate that was not a gap, and that is worth recording

I expected `kind: "banana"` to be ambiguous between "malformed" and
"ranks lowest." The adjudication says 0.910 for "accepted, ranks
lowest" and 0.070 for "malformed," because §1.1's malformed rule covers
a record *missing* a content field, not one carrying an unrecognised
*value*.

The original text was already clear. Probing found nothing, and
recording that is as useful as recording the hits — a fix that only
reports its successes is a fix whose coverage you cannot trust.

## The repair

Both sentences are now explicit:

> An unrecognised `kind` **string** is not malformed. §1.1's malformed
> rule covers a record *missing* a content field; a record carrying an
> unrecognised value for `kind` is accepted and ranked lowest by this
> rule. Only a missing field makes a record malformed.
>
> **Unclassifiable records are ranked `lowest` as a single class.** They
> are equal to each other, so a contest between two of them is decided
> by the equal-class rule in §5.2 step 3 — ancestry first, then topo
> order — exactly as for any other same-class pair. A contest between an
> unclassifiable record and a classifiable one is decided by class alone,
> and the classifiable record always wins.

Pushed as v0.4.6 alongside the original fixes.

## Why this is the finding I'd lead with in the whole audit

A gap that is only visible *after* fixing an earlier gap is invisible to
every method that reads the document once.

The reading-room experiment found §5.1 and §1.1 by having readers
implement the spec. That works on a document's *known* ambiguities. It
cannot find a gap introduced by the repair, because the repair's own
text is what the readers are now being asked to disagree about, and
there is no earlier version of it to compare against.

What found this was a different move: take the new text, construct
cases the new sentences do not obviously cover, and ask whether an
independent adjudicator thinks the text settles them. The instrument
does not know the text is mine, and I do not choose the answer.

**The generalisable form — a fix must be audited like the defect.**
Every ambiguity I have removed from this spec was found by constructing a
case where the answer is *not obvious*, and then checking whether the
document decides it. A clause can read as decisive to its author and be
silent exactly where the hard case lives; the only reliable detector is a
case chosen to be hard, by someone who does not know which clause is
under suspicion.
