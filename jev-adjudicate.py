#!/usr/bin/env python3
"""Adjudicate the two readings with Jev, behind the same calibration gate.

The calibration is not ceremony. An earlier run in this repo produced a
verdict that flipped when the clause was quoted verbatim instead of
paraphrased, and one "too close to call" turned out to be an artefact
of my own summary. So: calibrate first, quote verbatim second, and treat
a sub-threshold spread as UNRESOLVED rather than inventing a winner.
"""
import json, os, subprocess, sys

def jev(state, question, tries=4):
    body = json.dumps({"state": state, "model": "jev-latest",
                       "questions": {"q": {"type": "noul", "instructions": question}}})
    last = ""
    for i in range(tries):
        r = subprocess.run(["curl","-sk","-m","60","--fail-with-body",
            "https://api.typesafe.ai/v1/systemone",
            "-H", f"Authorization: Bearer {os.environ['TYPESAFE_AI_TOKEN']}",
            "-H","Content-Type: application/json","--data-binary", body],
            capture_output=True, text=True, timeout=90)
        last = (r.stdout or "") + (r.stderr or "")
        if r.returncode == 0:
            try:
                d = json.loads(r.stdout)
                if "answers" in d: return d["answers"]["q"]["noul"]
            except Exception: last = r.stdout[:200]
        if i < tries - 1: subprocess.run(["sleep","2"])
    raise RuntimeError(f"Jev unreachable: {last[:160]}")

# --- gate -------------------------------------------------------------
CONTROLS = [
 ("true stated",   {"s":"An orphan is a record whose parent id is absent. Example: ghost."},
                   "The text uses the identifier ghost.", "high"),
 ("false stated",  {"s":"An orphan is a record whose parent id is absent. Example: ghost."},
                   "The text uses the identifier zzz-9.", "low"),
 ("out of scope",  {"s":"An orphan is a record whose parent id is absent. Example: ghost."},
                   "Water boils at 100 degrees Celsius at sea level.", "middle"),
]
if "--calibrate" in sys.argv:
    res = {}
    for n, st, cl, exp in CONTROLS:
        s = jev(st, f"{cl}\n\nAnswer true if the text above supports this statement. If the text does not settle it, do not guess.")
        res[n] = s
        print(f"  {n:<16} {s:.3f}  (expect {exp})")
    t, f, o = res["true stated"], res["false stated"], res["out of scope"]
    ok = (t - f) > 0.3 and f < o < t
    print(f"  separation {t-f:+.3f}   CALIBRATED: {ok}")
    sys.exit(0 if ok else 1)

# --- the two claims, on VERBATIM paper text ----------------------------
STATE = {
 "eq17": "When at least one component changes, the pair decision compares the assembled candidate with the current pair under the same prescribed evaluation conditions; otherwise G_k^pair = 1 without a new evaluation.",
 "eq18": "(theta_{k+1}, phi_{d,k+1}) = (bar_theta, bar_phi) if G_k^pair = 1, else (theta_k, phi_{d,k}).",
 "eq15_16": "bar_theta_{k+1} = theta'_{k+1} if u_k^pi = 1 AND G_k^pi = 1, else theta_k. bar_phi_{d,k+1} = phi'_{d,k+1} if u_k^W = 1 AND G_k^W = 1, else phi_{d,k}.",
 "eq10": "rho_k^W = Reliability(W_phi; H_k, K_k) in {reliable, unreliable, insufficient}.",
 "eq11_insufficient": "Because feedback comes from selected candidates, its conclusions are limited to the observed and covered candidate range. Insufficient coverage yields an insufficient assessment rather than evidence of reliability and does not activate the adaptation trigger.",
 "pair_check_desc": "Pair acceptance therefore concerns the decision behavior of the assembled system and predictor suitability on candidates proposed by the selected policy, beyond isolated component quality. Each check returns one only when its specified criteria are met.",
}
Q = "Suppose the policy component changed and passed its check, the world-model component was not updated, and the pair check was NOT performed. According to the text above, is the new policy retained?"
CLAIMS = {
 "A_literal": "YES. The text says that otherwise G_k^pair = 1 without a new evaluation, so G_k^pair is one and Eq. 18 retains the candidate pair including the new policy.",
 "B_failclosed": "NO. The text only reaches the 'otherwise' branch when neither component changed, in which case the candidate pair is identical to the current pair and the comparison is vacuous. Here a component DID change, so the pair check was required by the text and its absence is not covered. The text does not settle what happens.",
}
if "--adjudicate" in sys.argv:
    out = {}
    for k, c in CLAIMS.items():
        s = jev(STATE, f"{c}\n\nQuestion: {Q}\n\nAnswer true if the specification text above supports this statement. If the text does not settle it, do not guess.")
        out[k] = s
        print(f"  {k:<16} {s:.3f}")
    sp = abs(out["A_literal"] - out["B_failclosed"])
    verdict = "A_literal" if out["A_literal"] > out["B_failclosed"] else "B_failclosed"
    if sp < 0.25: verdict = "UNRESOLVED"
    print(f"  spread {sp:+.3f}  -> {verdict}")
