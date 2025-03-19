from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from subprocess import run, CompletedProcess

from typing import Optional


def err(msg: str) -> None:
    print("\033[38;5;201m" + msg + "\033[39m", flush=True)


def info(msg: str) -> None:
    print("\033[38;5;84m" + msg + "\033[39m", flush=True)


def digest(path: Path) -> bytes:
    return sha256(path.read_bytes()).digest()


def runcmd(cmd: str, capture_output: bool, check: bool) -> Optional[str]:
    info(f"  % {cmd}")

    cp: CompletedProcess = run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True,
        check=check,
    )

    if capture_output:
        return cp.stdout.rstrip()
    else:
        return None
