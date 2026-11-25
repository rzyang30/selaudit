"""Markdown renderers for selaudit results."""

from __future__ import annotations

from .core import RoundLog, scale, verdict


def _fmt(value: float, digits: int = 3) -> str:
    return "—" if value != value else f"{value:+.{digits}f}"


def report(log: RoundLog, title: str = "Selection audit") -> str:
    s = scale(log)
    v = verdict(log)
    res, be = v["resolution"], v["breakeven"]

    lines = [f"# {title}", ""]
    lines.append(f"Rounds {s['rounds']} · candidates {log.acc.shape[1]} · audit window {s['n_audit']} "
                 f"images · baseline candidate {s['baseline']} · departures {s['switches']}")
    lines.append("")

    lines.append("## Headline estimands")
    lines.append("| Estimand | Value (pp) | 95% interval (pp) |")
    lines.append("|---|---:|---|")
    lines.append(f"| Hindsight ceiling M1 | {_fmt(s['m1'])} | "
                 f"[{_fmt(s['m1_ci'][0])}, {_fmt(s['m1_ci'][1])}], one-sided upper {_fmt(s['m1_upper95'])} |")
    lines.append(f"| Executable return M2 | {_fmt(s['m2'])} | "
                 f"[{_fmt(s['m2_ci'][0])}, {_fmt(s['m2_ci'][1])}], one-sided upper {_fmt(s['m2_upper95'])} |")
    lines.append("")

    lines.append("## Candidate accuracy")
    lines.append("| Candidate | Accuracy % | Δ vs baseline (pp) | 95% interval |")
    lines.append("|---|---:|---:|---|")
    for row in s["candidates"]:
        tag = " (baseline)" if row["candidate"] == s["baseline"] else ""
        lines.append(f"| c{row['candidate']}{tag} | {row['acc']:.2f} | {_fmt(row['delta'])} | "
                     f"[{_fmt(row['ci'][0])}, {_fmt(row['ci'][1])}] |")
    lines.append("")

    lines.append("## Resolution: can the audit see the difference?")
    lines.append("| Measure | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Paired standard error (median over {res['pairs']} pairs) | {res['paired_se_median']:.2f} pp |")
    lines.append(f"| Minimum detectable difference at 80% power | {res['mde_pp']:.2f} pp |")
    lines.append(f"| Observed gap, median / max | {res['gap_median_pp']:.2f} / {res['gap_max_pp']:.2f} pp |")
    lines.append(f"| Resolvable at this audit size | {'yes' if res['resolvable'] else '**no**'} |")
    if res["n_for_median"]:
        lines.append(f"| Audit size to resolve the median gap | ≈ {res['n_for_median']:.0f} images |")
        lines.append(f"| Audit size to resolve the largest gap | ≈ {res['n_for_max']:.0f} images |")
    lines.append("")

    lines.append("## Profitability: does a departure pay?")
    lines.append("| Measure | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Departures (win / tie / loss) | {be['departures']} ({be['win']} / {be['tie']} / {be['loss']}) |")
    lines.append(f"| Mean gain on a win | {_fmt(be['mean_gain_pp'])} pp |")
    lines.append(f"| Mean absolute loss on a loss | {be['mean_harm_pp']:.3f} pp |")
    lines.append(f"| Realized non-tie win rate p | {be['p']:.3f} |")
    lines.append(f"| Break-even win rate p* | {be['p_star']:.3f} |")
    lines.append(f"| Gap p − p* | {_fmt(be['gap'])} "
                 f"[{_fmt(be['gap_ci'][0])}, {_fmt(be['gap_ci'][1])}] |")
    lines.append(f"| Net return over all rounds | {_fmt(be['net_all_rounds_pp'])} pp |")
    if be["p"] and be["p"] == be["p"]:
        lines.append(f"| Precision uplift required | ×{be['uplift_needed']:.2f} |")
    lines.append("")

    lines.append("## Verdict")
    lines.append(f"**{v['situation']}.** {v['advice']}")
    lines.append("")
    return "\n".join(lines)


def checklist_markdown() -> str:
    return r"""# Six numbers to report before claiming a selector works

1. **The fixed comparator and how it was chosen.** Name the rule, and say whether it
   was selected on the same rounds you evaluate on. A comparator tuned on the audit
   rounds depresses every ceiling you report.
2. **The hindsight ceiling, with a one-sided upper limit.** Report M1 and an interval
   clustered by condition. A point estimate without an interval cannot separate
   "small" from "zero".
3. **The paired audit resolution.** Report the paired standard error and the minimum
   detectable difference at your audit size, next to the candidate gaps you observed.
   If no gap clears the MDE, no selector can be shown to work there.
4. **The departure accounting.** Report wins, ties, losses, mean gain, mean absolute
   loss, the realized non-tie win rate p, and the break-even rate p* = L/(G+L).
5. **The gap p − p\* with an interval.** This is the quantity that decides whether a
   selector pays. A loss that is not significant is not evidence of neutrality.
6. **The departure count.** Loss grows with the number of departures. A rule that
   switches rarely can look harmless at a small ceiling and a rule that switches often
   can lose at a large one.

## Review questions

- Is the audit size justified, or inherited from a previous protocol?
- Does the paper report the ceiling and the return separately? Conflating them hides
  whether the bottleneck is the audit or the rule.
- Are intervals clustered by condition, or by round? Rounds within a condition are not
  independent.
- Is the retention action counted as a candidate? If not, the ceiling is inflated.
"""
