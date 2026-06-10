import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_channel_intake_preview_completes_successfully() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/run_channel_intake_preview.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Channel intake preview completed successfully" in completed.stdout
    assert "accepted Telegram sample" in completed.stdout
    assert "accepted Website sample" in completed.stdout
    assert "accepted CRM sample" in completed.stdout
    assert "future Mobile App sample" in completed.stdout
    assert "invalid sample" in completed.stdout