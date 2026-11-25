# selaudit

**Two diagnostics that decide whether per-round selection can work at all — before you build a selector.**

Per-round selection papers usually report one number: the accuracy of a new selector against a
baseline. That number conflates two independent failures, and the fix for each is different:

| Question | Measured by | Fails when |
|---|---|---|
| Can the audit window tell the candidates apart? | paired standard error, minimum detectable difference (MDE) | candidate gaps are smaller than the MDE |
| Does departing from the fixed rule pay? | realized win rate `p` against break-even `p* = L/(G+L)` | `p < p*` |

`selaudit` computes both from a round log, in one call, and returns a verdict that says
which of the four situations you are in. It does not need a selector, a training run, or
any unlabeled score: only the labeled audit outcomes that a replay already produces.

This repository accompanies the manuscript *When Does Per-Round Selection of Batch
Normalization Updates Pay Off in Test-Time Adaptation?* and contains the package, the
six-item reporting checklist, and the archived round logs used in the paper.

## Install

```bash
python -m pip install -e .          # from this directory; requires numpy
```

## Quickstart

```bash
# 1. both diagnostics on an archived run
selaudit report --npz archived/cifar10_r18/arms_holdout_deploy_per_image.npz \
                --arms archived/cifar10_r18/arms_holdout_deploy_arms.csv \
                --baseline 3 --md report.md

# 2. the six numbers to report, as a checklist
selaudit checklist
```

```python
from selaudit import RoundLog, verdict, report

log = RoundLog.from_archived(
    "archived/cifar10_r18/arms_holdout_deploy_per_image.npz",
    "archived/cifar10_r18/arms_holdout_deploy_arms.csv",
    baseline=3,
)
print(report(log, title="CIFAR-10-C, ResNet-18"))

v = verdict(log)
print(v["situation"])      # blind-and-unprofitable / visible-but-unprofitable / ...
print(v["breakeven"]["p"], v["breakeven"]["p_star"])
```

If you already have per-round accuracies instead of per-image outcomes:

```python
from selaudit import RoundLog

log = RoundLog(acc=acc,          # (rounds, candidates) accuracy on the audit window
               m0_acc=m0_acc,    # (rounds,) accuracy of the retained model
               chosen=chosen,    # (rounds,) index, -1 for retention
               baseline=3,
               condition=cond,   # (rounds,) used as the bootstrap cluster
               n_audit=128)
# resolution needs per-image correctness; pass correct=(rounds, candidates, n) to enable it
```

## Validated against the paper's runs

Values are percentage points. `upper` is the one-sided 95% limit clustered by condition;
`p` is the non-tie win rate and `p* = L/(G+L)` is the break-even rate.

| Run | M1 | upper | M2 | SE | MDE | p | p* |
|---|---:|---:|---:|---:|---:|---:|---:|
| CIFAR-10-C, ResNet-18 | +0.677 | +0.854 | −0.186 | 2.33 | 6.52 | 0.338 | 0.577 |
| CIFAR-10-C, ResNet-50 | +0.703 | +0.847 | −0.408 | 2.48 | 6.94 | 0.327 | 0.655 |
| CIFAR-100-C, ResNet-18 | +1.120 | +1.379 | −0.607 | 2.77 | 7.75 | 0.286 | 0.637 |

The first two rows use the primary per-block CIFAR-10-C runs. The third uses the primary
CIFAR-100-C run with a ResNet-18 + dropout source model. The AETTA-style comparison in the
paper uses a single-trajectory selector run with its own E (83.63 / 61.49); the deltas there
are relative to that run's E. The values above are the primary runs.

`p` is the non-tie win rate over all departures from E (switching to another update or
retaining M0). The paper's Table 3 splits these into "other update" (p = .253 / .248) and
"retain M0" (p = .444 / .492); their union gives the .338 / .327 shown here. Table 4's
S-max is a different rule (p = .515 / .549 on CIFAR-10 and .323 on CIFAR-100).

Two readings that a point estimate hides:

- At 128 audit images the MDE is 6.5–7.8 pp while the largest observed candidate gap is
  5.7 pp. **No candidate pair is resolvable**, on either dataset.
- On CIFAR-100-C the ceiling is *larger* (+1.120) yet the return is *more negative*
  (−0.607). Raising the ceiling did not raise the win rate.

## Archived data

`archived/` contains the per-image predictions, round actions and AETTA-style logs used to
recompute the paper's tables. `archived/README.md` lists the full SHA-256 of every file.
The CIFAR-10-C and CIFAR-100-C image corpora are public and are **not** redistributed here.

```bash
python examples/reproduce_paper.py --root .
```

writes one report per run into `examples/out/` and prints the comparison table.

## The verdict matrix

| | `p < p*` | `p > p*` (interval excludes 0) |
|---|---|---|
| **no gap clears the MDE** | `blind-and-unprofitable` — enlarge the audit or shrink the candidate set before designing another selector | `blind-but-profitable` — the gain may be luck; enlarge the audit before reporting |
| **some gap clears the MDE** | `visible-but-unprofitable` — the audit can see the difference; the rule cannot capture it. The binding constraint is the win rate | `visible-and-profitable` — the selector is justified at this audit size; report the interval |

Most negative selection results sit in the top-left cell, which is why "we tried another
score function" rarely helps: the audit never had the resolution to support the claim.

## Repository layout

```
selaudit/core.py      RoundLog, audit_resolution, breakeven, verdict
selaudit/report.py    markdown report and the six-item checklist
selaudit/__main__.py  CLI
examples/             synthetic demo + reproduction of the three archived runs
tests/                unit tests
archived/             per-image predictions, action logs, AETTA logs
supplement/           S1 reproducibility audit (PDF)
```

## What this is not

- It does not estimate accuracy from unlabeled data; it audits decisions you already made.
- It does not choose a baseline for you. The baseline must be fixed before the run; a
  comparator tuned on the audit rounds depresses every ceiling reported.
- The MDE assumes independent audit images and a normal approximation at 80% power. With
  strongly clustered images, treat it as a lower bound on the required audit size.

## Citation

If this is useful, please cite the accompanying study and the GitHub release:
https://github.com/rzyang30/selaudit/releases/tag/v1.0.0

## License

Code: MIT. Archived prediction/action logs: CC BY 4.0 (see `LICENSE-DATA`).
