import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gateway_smoke_runner_completes_successfully() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/run_gateway_smoke.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Gateway smoke completed successfully" in completed.stdout
    assert '"status": "routed"' in completed.stdout
    