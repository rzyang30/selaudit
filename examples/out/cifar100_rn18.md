# CIFAR-100-C, ResNet-18

Rounds 750 · candidates 4 · audit window 128 images · baseline candidate 3 · departures 248

## Headline estimands
| Estimand | Value (pp) | 95% interval (pp) |
|---|---:|---|
| Hindsight ceiling M1 | +1.120 | [+0.826, +1.379], one-sided upper +1.379 |
| Executable return M2 | -0.607 | [-0.827, -0.436], one-sided upper -0.436 |

## Candidate accuracy
| Candidate | Accuracy % | Δ vs baseline (pp) | 95% interval |
|---|---:|---:|---|
| c0 | 56.58 | -4.899 | [-6.261, -3.837] |
| c1 | 57.91 | -3.570 | [-4.880, -2.543] |
| c2 | 59.37 | -2.111 | [-2.796, -1.577] |
| c3 (baseline) | 61.48 | +0.000 | [+0.000, +0.000] |

## Resolution: can the audit see the difference?
| Measure | Value |
|---|---:|
| Paired standard error (median over 6 pairs) | 2.77 pp |
| Minimum detectable difference at 80% power | 7.75 pp |
| Observed gap, median / max | 2.45 / 4.90 pp |
| Resolvable at this audit size | **no** |
| Audit size to resolve the median gap | ≈ 1281 images |
| Audit size to resolve the largest gap | ≈ 320 images |

## Profitability: does a departure pay?
| Measure | Value |
|---|---:|
| Departures (win / tie / loss) | 248 (64 / 24 / 160) |
| Mean gain on a win | +2.100 pp |
| Mean absolute loss on a loss | 3.687 pp |
| Realized non-tie win rate p | 0.286 |
| Break-even win rate p* | 0.637 |
| Gap p − p* | -0.351 [-0.470, -0.235] |
| Net return over all rounds | -0.607 pp |
| Precision uplift required | ×2.23 |

## Verdict
**blind-and-unprofitable.** The audit cannot separate the candidates and the rule does not pay. Enlarge the audit or shrink the candidate set before designing another selector.
