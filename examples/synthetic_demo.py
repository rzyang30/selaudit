"""Self-contained demo on synthetic logs.

Shows the two failure modes the diagnostics are meant to separate:

    python examples/synthetic_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from selaudit import RoundLog, breakeven, audit_resolution, report  # noqa: E402


def make_log(rounds=300, n=128, gaps=(0.0, 0.01, 0.02, 0.03), switch_rate=0.4,
             switch_precision=0.5, seed=0) -> RoundLog:
    """Simulate K candidates with known true gaps, plus a rule that switches.

    `switch_precision` is the probability that a switch picks the truly best
    candidate; the rest of the switches pick a random other candidate.
    """
    rng = np.random.default_rng(seed)
    K = len(gaps)
    base_rate = 0.80
    true_acc = base_rate + np.array(gaps)                    # candidate skill
    acc = np.zeros((rounds, K))
    correct = np.zeros((rounds, K, n), dtype=bool)
    for r in range(rounds):
        difficulty = rng.normal(0, 0.04)                     # shared round difficulty
        for j in range(K):
            p = np.clip(true_acc[j] + difficulty, 0.05, 0.99)
            correct[r, j] = rng.random(n) < p
            acc[r, j] = correct[r, j].mean()
    m0_acc = np.clip(base_rate + rng.normal(0, 0.04, rounds), 0.05, 0.99)

    chosen = np.full(rounds, 3)
    switch = rng.random(rounds) < switch_rate
    best = np.argmax(acc, axis=1)
    for r in np.where(switch)[0]:
        chosen[r] = best[r] if rng.random() < switch_precision else rng.integers(0, K)
    return RoundLog(acc=acc, m0_acc=m0_acc, chosen=chosen, baseline=3,
                    condition=np.array([f"cell{i % 20}" for i in range(rounds)]),
                    n_audit=n, correct=correct)


def main() -> int:
    print("=" * 78)
    print("Case A: candidates 1-3 pp apart, 128-image audit, rule switches at 50% precision")
    print("=" * 78)
    log = make_log()
    print(report(log, title="Synthetic, unresolvable audit"))

    print("=" * 78)
    print("Case B: candidates 1.5-4.5 pp apart, 2048-image audit")
    print("=" * 78)
    big = make_log(n=2048, gaps=(0.0, 0.015, 0.030, 0.045), seed=1)
    res = audit_resolution(big)
    be = breakeven(big)
    print(f"paired SE {res['paired_se_median']:.2f} pp, MDE {res['mde_pp']:.2f} pp, "
          f"largest gap {res['gap_max_pp']:.2f} pp, resolvable: {res['resolvable']}")
    print(f"p {be['p']:.3f} vs p* {be['p_star']:.3f} -> pays: {be['pays']}")
    print()
    print("The audit now resolves the candidates, and the rule still fails to clear break-even.")
    print("Enlarging the audit answers a different question than improving the rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
