"""Unit tests. Run with `python tests/test_core.py` or `pytest`."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from selaudit import RoundLog, audit_resolution, breakeven, required_audit_size, scale, verdict  # noqa: E402
from selaudit.core import POWER_FACTOR  # noqa: E402


def toy_log(rounds=200, n=64, seed=0):
    """Two candidates: c1 is better than the baseline c0 by 2 pp; the rule never switches."""
    rng = np.random.default_rng(seed)
    K = 2
    correct = np.zeros((rounds, K, n), dtype=bool)
    for r in range(rounds):
        p = (0.80, 0.82)
        for j in range(K):
            correct[r, j] = rng.random(n) < p[j]
    acc = correct.mean(axis=2)
    return RoundLog(acc=acc, m0_acc=np.full(rounds, 0.78), chosen=np.zeros(rounds, dtype=int),
                    baseline=0, condition=np.array([f"c{i % 10}" for i in range(rounds)]),
                    n_audit=n, correct=correct)


def test_m1_m2_identities():
    log = toy_log()
    m1 = log.m1()
    m2 = log.m2()
    assert np.allclose(m1, np.maximum(log.acc.max(axis=1), log.m0_acc) - log.acc[:, 0])
    # no departures -> M2 is exactly zero
    assert np.allclose(m2, 0.0)
    assert scale(log)["switches"] == 0


def test_retention_is_a_candidate():
    rng = np.random.default_rng(1)
    log = RoundLog(acc=np.full((10, 2), 0.5), m0_acc=np.full(10, 0.9),
                   chosen=-np.ones(10, dtype=int), baseline=0,
                   condition=np.array(["a"] * 10), n_audit=32, correct=None)
    assert np.allclose(log.m1(), 0.4)          # retention beats both candidates by 40 pp
    assert np.allclose(log.m2(), 0.4)


def test_breakeven_arithmetic():
    d = np.array([2.0, 1.0, -4.0])             # two wins, no tie, one loss
    acc = np.zeros((3, 2))
    acc[:, 0] = 0.80                            # baseline c0
    acc[:, 1] = 0.80 + d / 100                  # c1 relative to baseline
    log = RoundLog(acc=acc, m0_acc=np.zeros(3), chosen=np.ones(3, dtype=int), baseline=0,
                   condition=np.array(["a", "b", "c"]), n_audit=10, correct=None)
    be = breakeven(log)
    assert be["win"] == 2 and be["loss"] == 1 and be["tie"] == 0
    assert abs(be["mean_gain_pp"] - 1.5) < 1e-9
    assert abs(be["mean_harm_pp"] - 4.0) < 1e-9
    assert abs(be["p"] - 2 / 3) < 1e-9
    assert abs(be["p_star"] - 4.0 / 5.5) < 1e-9
    assert be["pays"] is False                  # 0.667 vs 0.727


def test_resolution_shrinks_with_audit_size():
    small = audit_resolution(toy_log(n=32, seed=2))
    large = audit_resolution(toy_log(n=512, seed=2))
    assert large["paired_se_median"] < small["paired_se_median"]
    assert large["mde_pp"] < small["mde_pp"]


def test_required_audit_size_matches_mde():
    n0, se = 128, 2.5
    gap = POWER_FACTOR * se                      # exactly at the current MDE
    assert abs(required_audit_size(gap, se, n0) - n0) < 1e-6


def test_verdict_quadrants():
    log = toy_log()
    v = verdict(log)
    assert v["situation"] in {"blind-and-unprofitable", "visible-and-unprofitable",
                              "blind-but-profitable", "visible-and-profitable"}


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{'all passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)
