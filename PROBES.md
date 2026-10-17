# Why probe this paper at all

RSI-Anything §2 is written with unusual care about scope. It repeatedly
delegates: "the domain specification states...", "is specified
separately", "the implementation specifies...", "the evaluation
specification fixes...".

That is a *good* drafting habit. It is also exactly the shape of a
document that defers its load-bearing decisions somewhere it never
shows you. §2.5 defines three gates Q_pi, Q_W, Q_pair as opaque
functions and says each "returns one only when its specified criteria
are met" — with the criteria specified per-application and never given.

That is structurally identical to the git.pp §1.1 defect: a fold that
must rank every record, where the rank for an unrecognised kind is
"out of scope". A gate whose acceptance test is unspecified is a gate
that cannot be checked by reading it.

The paper's own §5 concedes the central claim is unproven: "Joint
multiround evaluation is needed to establish sustained mutual
improvement of the policy and world model within a single task."

So the question is not "is this paper good". It is: **which of its
load-bearing decisions does the text actually determine, and which does
it hand to a configuration file that is not in the paper?**
