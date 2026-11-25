"""Command line entry point: python -m selaudit ..."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import RoundLog, verdict
from .report import checklist_markdown, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="selaudit", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    rep = sub.add_parser("report", help="run both diagnostics on an archived round log")
    rep.add_argument("--npz", required=True, help="per-image archive: cand / labels / m0 / condition")
    rep.add_argument("--arms", required=True, help="CSV with a `chosen` column")
    rep.add_argument("--baseline", type=int, default=3, help="index of the fixed comparator")
    rep.add_argument("--title", default="Selection audit")
    rep.add_argument("--md", help="write the markdown report here")
    rep.add_argument("--json", help="write the machine-readable result here")

    sub.add_parser("checklist", help="print the six-item reporting checklist")
    args = parser.parse_args(argv)

    if args.cmd == "checklist":
        print(checklist_markdown())
        return 0

    log = RoundLog.from_archived(args.npz, args.arms, baseline=args.baseline)
    text = report(log, title=args.title)
    print(text)
    if args.md:
        Path(args.md).write_text(text, encoding="utf-8")
    if args.json:
        v = verdict(log)
        Path(args.json).write_text(json.dumps(v, ensure_ascii=False, indent=2, default=float),
                                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
