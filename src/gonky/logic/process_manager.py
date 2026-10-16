"""Process manager — low-level helpers for launching and stopping Conky."""

import shutil
import signal
import subprocess
from pathlib import Path


def is_conky_installed() -> bool:
    """Return True if the ``conky`` executable is found on PATH."""
    return shutil.which("conky") is not None


def start_conky(config_path: Path) -> subprocess.Popen:
    """Launch Conky with *config_path* and return the resulting Popen handle.

    Conky is started with ``--daemonize`` so it backgrounds itself and returns
    control to the caller immediately.  stdout/stderr are suppressed to avoid
    polluting the terminal.
    """
    return subprocess.Popen(
        ["conky", "-c", str(config_path), "--daemonize"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_conky(proc: subprocess.Popen) -> None:
    """Terminate *proc* gracefully (SIGTERM), falling back to SIGKILL after 3 s.

    Does nothing if the process has already exited.
    """
    if proc.poll() is not None:
        # Process already finished — nothing to do.
        return

    try:
        proc.terminate()  # SIGTERM
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()  # SIGKILL fallback
        proc.wait()
    except OSError:
        # Process may have disappeared between poll() and terminate().
        pass


def is_running(proc: subprocess.Popen) -> bool:
    """Return True if *proc* is still running (i.e. has not exited)."""
    return proc.poll() is None
