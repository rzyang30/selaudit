# CIFAR-10-C, ResNet-18

Rounds 750 · candidates 4 · audit window 128 images · baseline candidate 3 · departures 159

## Headline estimands
| Estimand | Value (pp) | 95% interval (pp) |
|---|---:|---|
| Hindsight ceiling M1 | +0.677 | [+0.474, +0.854], one-sided upper +0.854 |
| Executable return M2 | -0.186 | [-0.291, -0.101], one-sided upper -0.101 |

## Candidate accuracy
| Candidate | Accuracy % | Δ vs baseline (pp) | 95% interval |
|---|---:|---:|---|
| c0 | 78.30 | -5.671 | [-7.355, -4.355] |
| c1 | 79.40 | -4.566 | [-6.209, -3.296] |
| c2 | 81.07 | -2.902 | [-3.899, -2.164] |
| c3 (baseline) | 83.97 | +0.000 | [+0.000, +0.000] |

## Resolution: can the audit see the difference?
| Measure | Value |
|---|---:|
| Paired standard error (median over 6 pairs) | 2.33 pp |
| Minimum detectable difference at 80% power | 6.52 pp |
| Observed gap, median / max | 2.84 / 5.67 pp |
| Resolvable at this audit size | **no** |
| Audit size to resolve the median gap | ≈ 678 images |
| Audit size to resolve the largest gap | ≈ 169 images |

## Profitability: does a departure pay?
| Measure | Value |
|---|---:|
| Departures (win / tie / loss) | 159 (48 / 17 / 94) |
| Mean gain on a win | +1.742 pp |
| Mean absolute loss on a loss | 2.377 pp |
| Realized non-tie win rate p | 0.338 |
| Break-even win rate p* | 0.577 |
| Gap p − p* | -0.239 [-0.390, -0.111] |
| Net return over all rounds | -0.186 pp |
| Precision uplift required | ×1.71 |

## Verdict
**blind-and-unprofitable.** The audit cannot separate the candidates and the rule does not pay. Enlarge the audit or shrink the candidate set before designing another selector.
