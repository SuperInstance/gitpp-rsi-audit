#!/usr/bin/env python3
"""Adjudicate the gaps my own fix introduced, behind the same gate.

A caveat that matters more than usual here: the author of the text being
adjudicated is also the author of the instrument, and has a stake in
the verdict. So the question asked is deliberately narrow -- 'does this
text SETTLE the question' -- and 'no' is a legitimate and useful
answer. A high score on UNDETERMINED is the finding, not a failure of
the run.
"""
import json, os, subprocess, sys

def jev(state, question, tries=4):
    body=json.dumps({"state":state,"model":"jev-latest",
                     "questions":{"q":{"type":"noul","instructions":question}}})
    last=""
    for i in range(tries):
        r=subprocess.run(["curl","-sk","-m","60","--fail-with-body",
          "https://api.typesafe.ai/v1/systemone",
          "-H",f"Authorization: Bearer {os.environ['TYPESAFE_AI_TOKEN']}",
          "-H","Content-Type: application/json","--data-binary",body],
          capture_output=True,text=True,timeout=90)
        last=(r.stdout or "")+(r.stderr or "")
        if r.returncode==0:
            try:
                d=json.loads(r.stdout)
                if "answers" in d: return d["answers"]["q"]["noul"]
            except Exception: last=r.stdout[:200]
        if i<tries-1: subprocess.run(["sleep","2"])
    raise RuntimeError(last[:160])

S51RANK=("Unclassifiable records rank below `witness`. A record whose `kind` is `null` or is "
 "not one of the three names has no class, and the fold must still rank it. Such a record "
 "ranks lowest: it can win an uncontested key, and it loses every contest against any "
 "classifiable record, whatever their relationship in the ancestry DAG. An unclassifiable "
 "record never displaces a classifiable one.")
S51CF=("Class is compared FIRST. Ancestry is a tie-break within a class, never a competing "
 "ranking. Two records of different class are ordered by class alone, regardless of how "
 "they are related. Ancestry is consulted only when the two classes are equal, where it "
 "selects the more derived of two same-class records.")
S52=("For each candidate R, for each key K that R sets: if K is set, compare R's class to "
 "the current setter's class. If R's class outranks, R is the new setter and the previous "
 "setter becomes a loser. If R's class is lower, R is a loser. If R's class is equal, R wins "
 "iff R descends from the current setter.")
S51_1=("kind is optional, defaulting to null. One of task, witness, override. Other values "
 "are accepted. A record missing any of the five content fields is malformed; the fold "
 "excludes malformed records from the applied set.")

TESTS = {
 "C1 two unclassifiable contest a key": {
   "state":{"s51_rank":S51RANK,"s52":S52},
   "q":"Two records BOTH have kind=null and both set key x. They are unrelated in ancestry. Which value ends up in state for x?",
   "A_undetermined":"The text DOES NOT DETERMINE it. Both records are unclassifiable; the rule that an unclassifiable record never displaces a classifiable one does not apply when neither is classifiable, and the text never says whether two unclassifiable records are 'equal' so the ancestry tie-break never engages.",
   "B_topofirst":"The first in topo order wins, because both records rank lowest and therefore have EQUAL rank, which routes the decision to the equal-class rule and its topo-order tie-break."},
 "C4 unrecognised string vs null": {
   "state":{"s51_1":S51_1,"s51_rank":S51RANK},
   "q":"A record has kind='banana', an unrecognised string. Is it malformed and excluded, or accepted and ranked lowest?",
   "A_lowest":"It is accepted and ranks lowest. The malformed rule covers records MISSING a field, not records carrying an unrecognised value, and 5.1 says other values are accepted and rank lowest.",
   "B_malformed":"It is malformed and excluded, because 1.1 says a record must have one of the three named classes."},
 "C5 two unclassifiable, one descends": {
   "state":{"s51_rank":S51RANK,"s52":S52},
   "q":"Two records both have kind=null. Record b descends from record a. Both set key x. Which value ends up in state?",
   "A_undetermined":"The text DOES NOT DETERMINE it. Ancestry is consulted only 'when the two classes are equal', and an unclassifiable record has no class, so whether two unclassifiable records are equal is never stated.",
   "B_descendant":"The descendant b wins, because both rank lowest, which makes them equal, so the equal-class rule selects the more derived record."},
}

if __name__=="__main__":
    if "--calibrate" in sys.argv:
        ctl=[("true",{"s":"An orphan is a record whose parent id is absent. Example: ghost."},"The text uses the identifier ghost."),
             ("false",{"s":"An orphan is a record whose parent id is absent. Example: ghost."},"The text uses the identifier zzz-9."),
             ("scope",{"s":"An orphan is a record whose parent id is absent. Example: ghost."},"Water boils at 100 C at sea level.")]
        r={}
        for n,st,cl in ctl:
            r[n]=jev(st,f"{cl}\n\nAnswer true if the text above supports this statement. If the text does not settle it, do not guess.")
            print(f"  {n:<8} {r[n]:.3f}")
        ok=(r["true"]-r["false"])>0.3 and r["false"]<r["scope"]<r["true"]
        print(f"  separation {r['true']-r['false']:+.3f}  CALIBRATED: {ok}")
        sys.exit(0 if ok else 1)
    out={}
    for name,t in TESTS.items():
        out[name]={}
        for k in ("A_undetermined","B_topofirst","B_descendant","A_lowest","B_malformed"):
            if k not in t: continue
            out[name][k]=jev(t["state"],
              f"{t[k]}\n\nQuestion: {t['q']}\n\nAnswer true if the specification text above supports this statement. If the text does not settle it, do not guess.")
            print(f"  {name:<40} {k:<16} {out[name][k]:.3f}", flush=True)
        print()
    json.dump(out, open("selfcheck-verdicts.json","w"), indent=1)
