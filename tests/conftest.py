from __future__ import annotations

import datetime
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def pytest_runtest_logreport(report):
    if report.when != "call":  # только фаза выполнения, не setup/teardown
        return

    REPORTS_DIR.mkdir(exist_ok=True)

    # tests/test_discoveryagent.py::test_foo  →  test_discoveryagent
    module = Path(report.nodeid.split("::")[0]).stem
    date = datetime.date.today().isoformat()
    filepath = REPORTS_DIR / f"{module}_{date}.txt"

    status = "PASSED" if report.passed else "FAILED"
    line = f"[{status}] {report.nodeid} ({report.duration:.4f}s)\n"
    if report.failed and report.longreprtext:
        line += f"{report.longreprtext}\n"
    line += "\n"

    with filepath.open("a", encoding="utf-8") as f:
        f.write(line)
