"""Core diagnostics for per-round candidate selection.

Two questions are answered separately, because they fail for different reasons:

1. **Resolution.** Given an audit window of n labeled images, can the audit tell
   the candidates apart at all? Measured as the paired standard error of each
   candidate pair and the minimum detectable difference (MDE) at 80% power.
2. **Profitability.** Given that a rule departs from a fixed comparator, does the
   win rate clear the break-even rate implied by its own gains and losses?

Both are computable from a round log and do not require any selector to be built.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

Z_975 = 1.959963984540054
Z_80 = 0.8416212335729143
POWER_FACTOR = Z_975 + Z_80          # 2.8016: MDE at two-sided 5% size, 80% power


@dataclass
class RoundLog:
    """Round-level outcomes on a labeled audit window.

    acc        (R, K)  accuracy of each candidate on the audit window, in [0, 1]
    m0_acc     (R,)    accuracy of the undeployed base state (the retention action)
    chosen     (R,)    index of the deployed candidate, -1 for retention
    baseline   int     index of the fixed comparator E
    condition  (R,)    condition label, used as the bootstrap cluster
    n_audit    int     images per audit window
    correct    (R, K, N) bool, optional: per-image correctness, enables resolution
    """

    acc: np.ndarray
    m0_acc: np.ndarray
    chosen: np.ndarray
    baseline: int
    condition: np.ndarray
    n_audit: int
    correct: np.ndarray | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.acc = np.asarray(self.acc, dtype=float)
        self.m0_acc = np.asarray(self.m0_acc, dtype=float)
        self.chosen = np.asarray(self.chosen, dtype=int)
        self.condition = np.asarray(self.condition)
        if self.acc.ndim != 2:
            raise ValueError("acc must be (rounds, candidates)")
        if len(self.m0_acc) != len(self.acc) or len(self.chosen) != len(self.acc):
            raise ValueError("acc / m0_acc / chosen must share the round axis")
        if not 0 <= self.baseline < self.acc.shape[1]:
            raise ValueError("baseline index out of range")

    # ---- constructors -------------------------------------------------
    @classmethod
    def from_archived(cls, npz_path, arms_path, baseline: int = 3, **kwargs) -> "RoundLog":
        """Read the archive layout used in the paper: cand/labels/m0 + arms.csv."""
        import csv
        from pathlib import Path

        npz = np.load(npz_path)
        correct = npz["cand"] == npz["labels"][:, None, :]
        m0 = npz["m0"] == npz["labels"]
        with Path(arms_path).open(encoding="utf-8-sig", newline="") as handle:
            chosen = np.array([int(r["chosen"]) for r in csv.DictReader(handle)])
        return cls(
            acc=correct.mean(axis=2),
            m0_acc=m0.mean(axis=1),
            chosen=chosen,
            baseline=baseline,
            condition=npz["condition"],
            n_audit=int(correct.shape[2]),
            correct=correct,
            **kwargs,
        )

    # ---- basic quantities ---------------------------------------------
    @property
    def rounds(self) -> int:
        return len(self.acc)

    def deployed_acc(self) -> np.ndarray:
        out = self.m0_acc.copy()
        keep = self.chosen >= 0
        out[keep] = self.acc[np.arange(len(keep))[keep], self.chosen[keep]]
        return out

    def delta(self) -> np.ndarray:
        """Per-round, per-candidate accuracy relative to the baseline candidate."""
        return self.acc - self.acc[:, [self.baseline]]

    def m1(self) -> np.ndarray:
        """Hindsight ceiling: best of candidates and retention, minus the baseline."""
        best = np.maximum(self.acc.max(axis=1), self.m0_acc)
        return best - self.acc[:, self.baseline]

    def m2(self) -> np.ndarray:
        """Executable return: what the rule deployed, minus the baseline."""
        return self.deployed_acc() - self.acc[:, self.baseline]


def cluster_bootstrap(values: np.ndarray, clusters: np.ndarray, repeats: int = 10000,
                      seed: int = 0, q: float = 95.0) -> tuple[float, float]:
    """Percentile interval, resampling whole clusters (conditions) with replacement."""
    names = sorted(set(np.asarray(clusters).tolist()))
    groups = [values[np.asarray(clusters) == name] for name in names]
    rng = np.random.default_rng(seed)
    draws = np.empty(repeats)
    for b in range(repeats):
        pick = rng.integers(0, len(groups), len(groups))
        draws[b] = float(np.mean([groups[j].mean() for j in pick]))
    lo = float(np.percentile(draws, (100 - q) / 2))
    hi = float(np.percentile(draws, q))
    return lo, hi


def upper_one_sided(values: np.ndarray, clusters: np.ndarray, repeats: int = 10000,
                    seed: int = 0, level: float = 95.0) -> float:
    """One-sided upper limit: the `level`-th percentile of the cluster bootstrap."""
    names = sorted(set(np.asarray(clusters).tolist()))
    groups = [values[np.asarray(clusters) == name] for name in names]
    rng = np.random.default_rng(seed)
    draws = np.empty(repeats)
    for b in range(repeats):
        pick = rng.integers(0, len(groups), len(groups))
        draws[b] = float(np.mean([groups[j].mean() for j in pick]))
    return float(np.percentile(draws, level))


def scale(log: RoundLog) -> dict:
    """Mean accuracy per candidate, the two headline estimands, and intervals."""
    m1, m2 = 100 * log.m1(), 100 * log.m2()
    lo_m1, hi_m1 = cluster_bootstrap(m1, log.condition)
    up_m1 = upper_one_sided(m1, log.condition)
    up_m2 = upper_one_sided(m2, log.condition)
    lo_m2, hi_m2 = cluster_bootstrap(m2, log.condition)
    per_candidate = []
    for j in range(log.acc.shape[1]):
        d = 100 * log.delta()[:, j]
        lo, hi = cluster_bootstrap(d, log.condition)
        per_candidate.append({"candidate": j, "acc": 100 * log.acc[:, j].mean(),
                              "delta": float(d.mean()), "ci": (lo, hi)})
    return {
        "rounds": log.rounds,
        "n_audit": log.n_audit,
        "baseline": log.baseline,
        "m1": float(m1.mean()), "m1_ci": (lo_m1, hi_m1), "m1_upper95": up_m1,
        "m2_upper95": up_m2,
        "m2": float(m2.mean()), "m2_ci": (lo_m2, hi_m2),
        "candidates": per_candidate,
        "switches": int(np.sum(log.chosen != log.baseline)),
    }


def audit_resolution(log: RoundLog) -> dict:
    """Paired standard error and minimum detectable difference at the audit size."""
    if log.correct is None:
        raise ValueError("resolution needs per-image correctness; build the log with `correct`")
    correct = log.correct.astype(float)
    n = correct.shape[2]
    K = correct.shape[1]
    ses, gaps = [], []
    for j in range(K):
        for k in range(j + 1, K):
            diff = correct[:, j, :] - correct[:, k, :]
            ses.append(float(np.mean(diff.std(axis=1, ddof=1) / np.sqrt(n))))
            gaps.append(abs(float(diff.mean())))
    ses, gaps = np.array(ses), np.array(gaps)
    med_se = float(np.median(ses))
    mde = POWER_FACTOR * med_se
    med_gap, max_gap = float(np.median(gaps)), float(np.max(gaps))
    return {
        "n_audit": n,
        "pairs": int(len(ses)),
        "paired_se_median": 100 * med_se,
        "mde_pp": 100 * mde,
        "gap_median_pp": 100 * med_gap,
        "gap_max_pp": 100 * max_gap,
        "resolvable": bool(max_gap >= mde),
        "n_for_median": float(n * (med_se / (med_gap / POWER_FACTOR)) ** 2) if med_gap > 0 else None,
        "n_for_max": float(n * (med_se / (max_gap / POWER_FACTOR)) ** 2) if max_gap > 0 else None,
    }


def breakeven(log: RoundLog) -> dict:
    """Win/tie/loss accounting for departures from the baseline, and p*."""
    d = 100 * log.m2()
    depart = d[log.chosen != log.baseline]
    win, loss = depart[depart > 1e-12], depart[depart < -1e-12]
    tie = depart[np.abs(depart) <= 1e-12]
    gain = float(win.mean()) if win.size else 0.0
    harm = float(-loss.mean()) if loss.size else 0.0
    p_star = harm / (gain + harm) if (gain + harm) > 0 else float("nan")
    p = float(win.size / (win.size + loss.size)) if (win.size + loss.size) else float("nan")

    def gap_on(idx: np.ndarray) -> float:
        dd = d[idx]
        dep = dd[np.asarray(log.chosen)[idx] != log.baseline]
        w, l = dep[dep > 1e-12], dep[dep < -1e-12]
        if w.size + l.size == 0:
            return float("nan")
        g = w.mean() if w.size else 0.0
        h = -l.mean() if l.size else 0.0
        return (w.size / (w.size + l.size)) - (h / (g + h) if (g + h) > 0 else np.nan)

    names = sorted(set(log.condition.tolist()))
    rng = np.random.default_rng(0)
    draws = []
    for _ in range(4000):
        pick = rng.integers(0, len(names), len(names))
        idx = np.concatenate([np.where(log.condition == names[j])[0] for j in pick])
        draws.append(gap_on(idx))
    arr = np.asarray(draws, dtype=float)
    if np.all(np.isnan(arr)):
        lo, hi = float("nan"), float("nan")
    else:
        lo, hi = np.nanpercentile(arr, [2.5, 97.5])

    return {
        "departures": int(depart.size),
        "win": int(win.size), "tie": int(tie.size), "loss": int(loss.size),
        "mean_gain_pp": gain, "mean_harm_pp": harm,
        "p": p, "p_star": p_star, "gap": p - p_star, "gap_ci": (float(lo), float(hi)),
        "net_per_departure_pp": float(depart.mean()) if depart.size else 0.0,
        "net_all_rounds_pp": float(d.mean()),
        "uplift_needed": (p_star / p) if p and p > 0 else float("inf"),
        "pays": bool(lo > 0),
    }


def verdict(log: RoundLog) -> dict:
    """Combine resolution and profitability into one of four situations."""
    res = audit_resolution(log)
    be = breakeven(log)
    if not res["resolvable"] and not be["pays"]:
        code, advice = "blind-and-unprofitable", (
            "The audit cannot separate the candidates and the rule does not pay. "
            "Enlarge the audit or shrink the candidate set before designing another selector.")
    elif not res["resolvable"] and be["pays"]:
        code, advice = "blind-but-profitable", (
            "The rule appears to pay, but the audit cannot resolve the candidates, so the gain "
            "may be luck. Enlarge the audit before reporting it.")
    elif res["resolvable"] and not be["pays"]:
        code, advice = "visible-but-unprofitable", (
            "The audit can see the differences and the rule still fails to capture them. "
            "The binding constraint is the win rate, not the audit size.")
    else:
        code, advice = "visible-and-profitable", (
            "The audit resolves the candidates and the departures clear break-even. "
            "Report the interval; the selector is justified at this audit size.")
    return {"resolution": res, "breakeven": be, "situation": code, "advice": advice}


def required_audit_size(gap_pp: float, se_pp: float, n0: int) -> float:
    """Audit size that would detect `gap_pp` at 80% power, given a current SE."""
    if gap_pp <= 0:
        raise ValueError("gap must be positive")
    return float(n0 * (POWER_FACTOR * se_pp / gap_pp) ** 2)
