#!/usr/bin/env python3
"""Independent readers of RSI-Anything section 2, written from the paper's
text alone and forbidden to look at the paper's own results section.

Two questions the text must answer, each with a discriminating case.

Q1  Eq. 17's skip. When is G_pair = 1 assigned WITHOUT a new
    evaluation, and is that assignment justified by the candidate or by
    the procedure?

Q2  The pair check's return type. Eq. 10's Reliability() returns
    THREE values -- reliable / unreliable / insufficient -- and the
    paper insists insufficient is not evidence of reliability. Q_pair
    returns a BIT. What happens when a pair check is attempted but
    cannot be completed?
"""
import json, sys

# ---- reader A: the paper as literally written -----------------------------
def reader_A_literal(u_pi, G_pi, u_W, G_W, pair_completed):
    """Eq. 15-18 transcribed. The 'otherwise' branch is keyed on
    'not pair_evaluated', per the sentence's own wording."""
    bar_theta = "new" if (u_pi and G_pi) else "old"
    bar_phi   = "new" if (u_W and G_W) else "old"
    at_least_one_changed = (bar_theta == "new") or (bar_phi == "new")
    if not at_least_one_changed or not pair_completed:
        # <- literal reading: no evaluation performed => assume pass
        return {"G_pair": 1, "basis": "skipped, assumed pass"}
    return {"G_pair": 1, "basis": "pair check ran and passed"}

# ---- reader B: identical, but a failed check is not a pass ---------------
def reader_B_failclosed(u_pi, G_pi, u_W, G_W, pair_completed):
    """Same equations, but the skip is justified by IDENTITY of the
    candidate pair, and an attempted-but-incomplete check retains the
    current pair (Eq. 11's posture at Eq. 10)."""
    bar_theta = "new" if (u_pi and G_pi) else "old"
    bar_phi   = "new" if (u_W and G_W) else "old"
    changed = (bar_theta == "new") or (bar_phi == "new")
    if not changed:
        # candidate pair IS the current pair -> vacuous comparison
        return {"G_pair": 1, "basis": "candidate identical to current"}
    if not pair_completed:
        # attempted but unresolved -> fail closed, matching Eq. 11
        return {"G_pair": 0, "basis": "unresolved pair check retains current"}
    return {"G_pair": 1, "basis": "pair check ran and passed"}

CASES = [
  # (name, u_pi, G_pi, u_W, G_W, pair_completed)
  ("both changed, pair check ran",        1, 1, 1, 1, True),
  ("policy changed, model not",           1, 1, 0, 0, True),
  ("model changed, policy not",           0, 0, 1, 1, True),
  ("neither changed",                     0, 0, 0, 0, False),
  ("policy changed, pair check SKIPPED",  1, 1, 0, 0, False),
  ("both changed, pair check INCOMPLETE", 1, 1, 1, 1, False),
]

if __name__ == "__main__":
    print(f"  {'case':<40} {'A (literal)':<28} {'B (fail-closed)'}")
    split = 0
    for name, a, b, c, d, e in CASES:
        ra, rb = reader_A_literal(a,b,c,d,e), reader_B_failclosed(a,b,c,d,e)
        mark = "  <-- SPLIT" if ra["G_pair"] != rb["G_pair"] else ""
        if mark: split += 1
        print(f"  {name:<40} G={ra['G_pair']} {ra['basis'][:14]:<14} G={rb['G_pair']} {rb['basis'][:16]}{mark}")
    print(f"\n  {split} of {len(CASES)} cases split the two readings")
