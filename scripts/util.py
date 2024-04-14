#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess, run
from sys import exit
from typing import List

from color import Color, colorize


def eprint(msg: str) -> None:
    print(msg, flush=True)


def fatal(msg: str) -> None:
    eprint(colorize(msg, Color.X201_MAGENTA1))
    exit(1)


#
# shell wrapper
#
@dataclass
class ShResult:
    returncode: int
    stdout: List[str]
    stderr: List[str]


def sh(cmd: str, capture_output: bool, verbose: bool) -> ShResult:
    """Execute _cmd_"""

    if verbose:
        eprint(f"% {cmd}")

    cp: CompletedProcess = run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True,
    )

    returncode: int = cp.returncode
    stdout: List[str] = list()
    stderr: List[str] = list()

    if capture_output:
        stdout = cp.stdout.splitlines()
        stderr = cp.stderr.splitlines()
    else:
        pass

    return ShResult(returncode, stdout, stderr)


#
# git
#
def gitcmd(topdir: Path, cmd: str) -> ShResult:
    """git wrapper"""
    return sh(f"git -C '{str(topdir)}' {cmd}", True, False)


def commit(topdir: Path, files: List[Path]) -> None:
    """Commit format

    Args:
        topdir (:obj:`Path`): top level dir (normally, parent of _gitdir_)
        files (:obj:`List[Path]`): pushed scripts

    Returns:
        None

    Raises:
        None

    """

    # reset not to commit unintended files
    _ = gitcmd(topdir, "reset")

    # try to add files
    for f in files:
        _ = gitcmd(topdir, f"add '{str(f)}'")

    # format commit if some files are updated?
    staged_files: List[str] = gitcmd(topdir, "diff --name-only --cached").stdout

    if staged_files:
        eprint(f"  commit: {staged_files}")
        _ = gitcmd(topdir, "commit -m ':art: Format'")
    else:
        pass
