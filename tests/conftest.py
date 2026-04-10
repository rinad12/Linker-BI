from __future__ import annotations

import datetime
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def pytest_runtest_logreport(report):
    if report.when != "call":  # execution phase only, not setup/teardown
        return

    REPORTS_DIR.mkdir(exist_ok=True)

    # tests/test_discoveryagent.py::test_foo -> test_discoveryagent
    module = Path(report.nodeid.split("::")[0]).stem
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = REPORTS_DIR / f"{module}_{timestamp}.txt"

    status = "PASSED" if report.passed else "FAILED"
    line = f"[{status}] {report.nodeid} ({report.duration:.4f}s)\n"
    if report.failed and report.longreprtext:
        line += f"{report.longreprtext}\n"
    line += "\n"

    with filepath.open("a", encoding="utf-8") as f:
        f.write(line)
