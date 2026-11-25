"""Reproduce the paper's diagnostics from archived round logs.

    python examples/reproduce_paper.py --root /path/to/实验

Writes one markdown report per run into examples/out/ and prints a comparison
table against the numbers reported in the manuscript.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from selaudit import RoundLog, audit_resolution, breakeven, report, scale  # noqa: E402

RUNS = [
    ("cifar10_rn18", "CIFAR-10-C, ResNet-18",
     "archived/cifar10_r18/arms_holdout_deploy_per_image.npz",
     "archived/cifar10_r18/arms_holdout_deploy_arms.csv", 3),
    ("cifar10_rn50", "CIFAR-10-C, ResNet-50",
     "archived/cifar10_r50/confirm_resnet50_per_image.npz",
     "archived/cifar10_r50/confirm_resnet50_arms.csv", 3),
    ("cifar100_rn18", "CIFAR-100-C, ResNet-18",
     "archived/cifar100_r18/arms_holdout_c100_per_image.npz",
     "archived/cifar100_r18/arms_holdout_c100_arms.csv", 3),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="directory that contains the experiment tree")
    parser.add_argument("--out", default="examples/out")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for key, title, npz_rel, arms_rel, baseline in RUNS:
        npz, arms = root / npz_rel, root / arms_rel
        if not npz.exists():
            print(f"skip {key}: {npz} not found")
            continue
        log = RoundLog.from_archived(npz, arms, baseline=baseline)
        s = scale(log)
        res = audit_resolution(log)
        be = breakeven(log)
        (out_dir / f"{key}.md").write_text(report(log, title=title), encoding="utf-8")
        rows.append((title, s["m1"], s["m1_upper95"], s["m2"], res["paired_se_median"],
                     res["mde_pp"], be["p"], be["p_star"]))

    print(f"{'run':<26}{'M1':>8}{'upper':>8}{'M2':>8}{'SE':>7}{'MDE':>7}{'p':>7}{'p*':>7}")
    for r in rows:
        print(f"{r[0]:<26}{r[1]:>+8.3f}{r[2]:>+8.3f}{r[3]:>+8.3f}{r[4]:>7.2f}{r[5]:>7.2f}"
              f"{r[6]:>7.3f}{r[7]:>7.3f}")
    print(f"\nreports written to {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
