# CIFAR-10-C, ResNet-50

Rounds 750 · candidates 4 · audit window 128 images · baseline candidate 3 · departures 250

## Headline estimands
| Estimand | Value (pp) | 95% interval (pp) |
|---|---:|---|
| Hindsight ceiling M1 | +0.703 | [+0.537, +0.847], one-sided upper +0.847 |
| Executable return M2 | -0.408 | [-0.558, -0.294], one-sided upper -0.294 |

## Candidate accuracy
| Candidate | Accuracy % | Δ vs baseline (pp) | 95% interval |
|---|---:|---:|---|
| c0 | 78.51 | -5.608 | [-7.074, -4.441] |
| c1 | 80.30 | -3.816 | [-5.068, -2.824] |
| c2 | 82.29 | -1.828 | [-2.359, -1.415] |
| c3 (baseline) | 84.12 | +0.000 | [+0.000, +0.000] |

## Resolution: can the audit see the difference?
| Measure | Value |
|---|---:|
| Paired standard error (median over 6 pairs) | 2.48 pp |
| Minimum detectable difference at 80% power | 6.94 pp |
| Observed gap, median / max | 2.88 / 5.61 pp |
| Resolvable at this audit size | **no** |
| Audit size to resolve the median gap | ≈ 741 images |
| Audit size to resolve the largest gap | ≈ 196 images |

## Profitability: does a departure pay?
| Measure | Value |
|---|---:|
| Departures (win / tie / loss) | 250 (66 / 48 / 136) |
| Mean gain on a win | +1.598 pp |
| Mean absolute loss on a loss | 3.027 pp |
| Realized non-tie win rate p | 0.327 |
| Break-even win rate p* | 0.655 |
| Gap p − p* | -0.328 [-0.447, -0.218] |
| Net return over all rounds | -0.408 pp |
| Precision uplift required | ×2.00 |

## Verdict
**blind-and-unprofitable.** The audit cannot separate the candidates and the rule does not pay. Enlarge the audit or shrink the candidate set before designing another selector.
