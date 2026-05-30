"""User launchd integration for P0030 daily spot history ingest."""

from __future__ import annotations

from pathlib import Path
import plistlib
import subprocess
import sys

from .models import LaunchdInstallResult
from .storage import default_db_path


LABEL = "se.mlovholm.smart-home.spotprice-history-daily"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
OUT_LOG = Path.home() / ".smart-home" / "logs" / "spotprice-history-daily.out.log"
ERR_LOG = Path.home() / ".smart-home" / "logs" / "spotprice-history-daily.err.log"


def render_launch_agent_plist(
    *,
    db_path: Path | str = default_db_path(),
    python_executable: str = sys.executable,
) -> str:
    payload = {
        "Label": LABEL,
        "ProgramArguments": [
            python_executable,
            "-m",
            "src.mac.services.spotprice_history",
            "ingest-daily",
            "--area",
            "SE3",
            "--db",
            str(Path(db_path).expanduser()),
        ],
        "StartCalendarInterval": {"Hour": 14, "Minute": 0},
        "StandardOutPath": str(OUT_LOG),
        "StandardErrorPath": str(ERR_LOG),
        "WorkingDirectory": str(Path(__file__).resolve().parents[4]),
    }
    return plistlib.dumps(payload, sort_keys=False).decode("utf-8")


def install_daily_job(
    *,
    db_path: Path | str = default_db_path(),
    plist_path: Path | str = PLIST_PATH,
    python_executable: str = sys.executable,
    run_launchctl: bool = True,
) -> LaunchdInstallResult:
    target = Path(plist_path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    Path(db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_launch_agent_plist(db_path=db_path, python_executable=python_executable),
        encoding="utf-8",
    )
    if not run_launchctl:
        return LaunchdInstallResult(LABEL, str(target), False, "plist written; launchctl not requested")

    gui_target = _gui_target()
    subprocess.run(["launchctl", "bootout", gui_target, str(target)], check=False, capture_output=True, text=True)
    loaded = subprocess.run(
        ["launchctl", "bootstrap", gui_target, str(target)],
        check=False,
        capture_output=True,
        text=True,
    )
    if loaded.returncode != 0:
        message = (loaded.stderr or loaded.stdout or "launchctl bootstrap failed").strip()
        return LaunchdInstallResult(LABEL, str(target), False, message)
    enabled = subprocess.run(
        ["launchctl", "enable", f"{gui_target}/{LABEL}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if enabled.returncode != 0:
        message = (enabled.stderr or enabled.stdout or "launchctl enable failed").strip()
        return LaunchdInstallResult(LABEL, str(target), False, message)
    return LaunchdInstallResult(LABEL, str(target), True, "loaded")


def _gui_target() -> str:
    return f"gui/{subprocess.check_output(['id', '-u'], text=True).strip()}"
