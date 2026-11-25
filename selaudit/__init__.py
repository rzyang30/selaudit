"""selaudit: two diagnostics for per-round candidate selection.

    from selaudit import RoundLog, verdict, report

    log = RoundLog.from_archived("per_image.npz", "arms.csv", baseline=3)
    print(report(log))
"""

from .core import (
    RoundLog, audit_resolution, breakeven, cluster_bootstrap,
    required_audit_size, scale, verdict,
)
from .report import checklist_markdown, report

__version__ = "1.0.0"
__all__ = [
    "RoundLog", "audit_resolution", "breakeven", "cluster_bootstrap",
    "required_audit_size", "scale", "verdict", "report", "checklist_markdown",
]
