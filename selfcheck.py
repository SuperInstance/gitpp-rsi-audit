#!/usr/bin/env python3
"""Did my own v0.4.6 fix introduce fresh ambiguity?

A specification change is only good if the new text is at least as
determined as the old. I fixed four clauses, so the honest thing is to
probe the NEW text for holes I created rather than assume the fix is
clean.

This reads the new clauses and looks for cases the new wording does
not settle. Each candidate is stated as a record set, not as a feeling.
"""
import json

# The new sentences I added, verbatim.
NEW_5_1_RANK = ("Unclassifiable records rank below `witness`. A record whose `kind` is `null` "
  "or is not one of the three names has no class, and the fold must still rank it (5.2). "
  "Such a record ranks lowest: it can win an uncontested key, and it loses every contest "
  "against any classifiable record, whatever their relationship in the ancestry DAG. "
  "An unclassifiable record never displaces a classifiable one.")
NEW_5_1_CLASSFIRST = ("Class is compared FIRST. Ancestry is a tie-break within a class, never a "
  "competing ranking. Two records of different class are ordered by class alone, regardless "
  "of how they are related.")
NEW_5_2_TIEBREAK = ("Among equal-class survivors that are mutually incomparable in ancestry, "
  "the first in topo order wins.")

R = lambda i,k,p,e: {"id":i,"kind":k,"parents":p,"effects":e,"reason":None}

CANDIDATES = [
 ("C1 both records unclassifiable, contested key",
  "Records A and B both have kind=null (or an unknown kind) and contest the same key. "
  "The new text ranks each 'below witness' and says an unclassifiable record 'never "
  "displaces a classifiable one' -- but NEITHER is classifiable, so that sentence does "
  "not apply. Does the tie-break fall through to the equal-class rule (topo order), or is "
  "the key left unset, or is it undefined?",
  [R("a",None,[],{"x":1}), R("b",None,[],{"x":2})]),

 ("C2 unclassifiable is an ANCESTOR of a classifiable record",
  "An unclassifiable record O is the parent of a witness W, and both set the same key. "
  "The new text says unclassifiable 'loses every contest against any classifiable record, "
  "whatever their relationship in the ancestry DAG', which settles the value. But it does "
  "not say whether the unclassifiable O is recorded as a LOSER in the conflict ledger for "
  "that key, or is simply skipped without appearing in the ledger.",
  [R("o",None,[],{"x":1}), R("w","witness",["o"],{"x":2})]),

 ("C3 'classifiable' vs 'class is equal' interaction for null kinds",
  "5.1 says ancestry is consulted 'only when the two classes are equal'. An unclassifiable "
  "record has NO class, so 'equal' is undefined for it. Does an unclassifiable record ever "
  "reach the ancestry tie-break, or is it always decided by the 'ranks lowest' rule?",
  [R("a","override",[],{"x":1}), R("b",None,["a"],{"x":2})]),

 ("C4 unrecognised-kind STRING vs null -- same treatment?",
  "5.1 groups 'null or is not one of the three names' together. It does not say whether an "
  "unrecognised string is a hard error (malformed) or an unclassifiable record that ranks "
  "lowest. These give different results if the implementation validates kinds anywhere.",
  [R("a","banana",[],{"x":1}), R("b","witness",[],{"x":2})]),

 ("C5 two unclassifiable records in an ANCESTRY relation",
  "Both records are unclassifiable, and one descends from the other. If they are 'equal' "
  "for the purposes of the ancestry tie-break, the descendant wins. But the text never "
  "says unclassifiable records are 'equal' to each other.",
  [R("a",None,[],{"x":1}), R("b",None,["a"],{"x":2})]),
]

if __name__ == "__main__":
    print("  Candidate gaps in the NEW v0.4.6 text:\n")
    for name, q, recs in CANDIDATES:
        print(f"  {name}")
        print(f"    {q[:200]}")
        print(f"    records: {json.dumps(recs)[:120]}")
        print()
    print(f"  {len(CANDIDATES)} candidate gaps found in text I wrote myself.")
