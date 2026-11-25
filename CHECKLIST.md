# Six numbers to report before claiming a selector works

A reporting checklist for per-round selection under distribution shift. Each item is
computable from a labeled audit window; none requires the selector to be rerun.

Use it in one of three ways: as authors before writing the results section, as reviewers
when a paper reports only a selector-to-baseline delta, or as a reader deciding whether a
claim transfers to your audit budget.

---

## 1. The fixed comparator, and how it was chosen

Name the rule precisely (update scope, strength, step count) and say whether it was
selected on the same rounds you evaluate on.

- If the comparator was tuned on the audit rounds, every ceiling you report is depressed
  by construction, and the sign of the realized return is close to predetermined.
- Acceptable: chosen on a disjoint development split and frozen before the confirmatory
  run, with a leave-one-condition-out check that it is still selected in all folds.

## 2. The hindsight ceiling, with a one-sided upper limit

Report the best-of-candidates-and-retention gain over the comparator (M1), with an
interval that resamples **conditions**, not rounds.

- A point estimate cannot separate "small" from "zero".
- Count retention of the current model as a candidate. Omitting it inflates the ceiling.
- Report the ceiling on at least two weightings (equal cells; equal corruption types) —
  unequal cell counts can move it by 0.1–0.2 pp.

## 3. The paired audit resolution

For each candidate pair, take the per-image difference in correctness, divide its
within-round standard deviation by √n, average across rounds, and take the median over
pairs. Multiply by 2.8 for the minimum detectable difference at 80% power.

- Put the MDE next to the candidate gaps you actually observed.
- **If no gap clears the MDE, no selector can be shown to work at that audit size.** The
  honest conclusion is about the audit, not about selectors.
- Report the audit size that would resolve the median gap. If it is an order of magnitude
  above a streaming budget, that is the finding.

## 4. The departure accounting

For every round where the rule departs from the comparator, record win / tie / loss, the
mean gain on wins `G`, and the mean absolute loss on losses `L`.

- Report the realized non-tie win rate `p` and the break-even rate `p* = L/(G+L)`.
- Report the net return per departure and over all rounds; the second must reproduce the
  headline selector-to-baseline delta.
- Separate "switch to another candidate" from "abstain and keep the current model". Their
  `p*` differ, and abstention is usually the less bad of the two.

## 5. The gap `p − p*`, with an interval

This is the quantity that decides whether a selector pays, and it is not the same as the
accuracy difference.

- An interval that contains zero is not evidence of neutrality; it is absence of evidence.
- A required precision uplift (`p*/p`) is a concrete target for the next method, and a
  concrete falsification criterion for this one.

## 6. The departure count

Loss scales with the number of departures. Two papers can report the same negative delta
with 130 and 700 departures; the first has a threshold problem, the second has a scoring
problem.

- Report departures as a fraction of rounds.
- If the rule departs on most rounds and still loses, the score is uninformative, not
  merely conservative.
- If it departs rarely and loses slightly, the loss is a handful of decisions and the
  interval will usually cover zero.

---

## Review questions

1. Is the audit size justified, or inherited from an earlier protocol?
2. Are the ceiling and the return reported separately? Conflating them hides whether the
   bottleneck is the audit or the rule.
3. Are intervals clustered by condition? Rounds within a condition are not independent,
   and round-level bootstrapping understates the interval by roughly a factor of two.
4. Is the retention action counted as a candidate?
5. Does the paper report the comparator's selection procedure, or only its accuracy?
6. Would the claimed gain survive an audit twice as large? If the answer is "we do not
   know", item 3 is missing.

## Tool

`selaudit` computes items 2–6 from a round log:

```bash
pip install -e .
selaudit report --npz per_image.npz --arms arms.csv --baseline 3 --md report.md
selaudit checklist
```
