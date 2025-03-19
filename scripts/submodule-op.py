#!/usr/bin/env python3
from __future__ import annotations

"""Git submodule operator"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from sys import exit
from subprocess import run

from logging import getLogger, Logger, StreamHandler, INFO, ERROR


class ColoredStreamHandler(StreamHandler):
    def __init__(self) -> None:
        super().__init__()

    def emit(self, record) -> None:
        if record.levelno == INFO:
            record.msg = "\033[38;5;84m" + f"[ INFO] {record.msg}" + "\033[39m"
        elif record.levelno == ERROR:
            record.msg = "\033[38;5;201m" + f"[ERROR] {record.msg}" + "\033[39m"
        else:
            raise NotImplementedError("Unknown log level: {record.levelno}")

        super().emit(record)
        return


lg: Logger = getLogger("submodule-operator")
lg.setLevel(INFO)
lg.addHandler(ColoredStreamHandler())


def gitcmd(repodir: Path, cmd: str) -> str:
    """git -C _repodir_ _cmd_"""
    return run(
        f"git -C '{str(repodir)}' {cmd}", shell=True, capture_output=True, text=True
    ).stdout.rstrip()


def check(toplevel: Path, path: Path, branch: str) -> bool:
    """check submodule

    Args:
        toplevel (Path): `git rev-parse --show-toplevel`
        path (Path): submodule path
        branch (str): expected branch

    Returns:
        bool: True if up to date

    """
    lg.info(f"submodule-op::check: {toplevel} @ {path}, branch: {branch}")

    # Get submodule url
    url: str = gitcmd(toplevel, f"config --get submodule.{path}.url")

    # check only owning repo
    if not url.startswith("git@github.com"):
        lg.info("  => external repository")
        return True
    else:
        # if on expected branch?
        local_branch: str = gitcmd(toplevel / path, "rev-parse --abbrev-ref HEAD")
        lg.info(f"  checking branch: local: {local_branch}, expected: {branch}")

        if local_branch == branch:
            lg.info("    => PASS")
        else:
            lg.error("    => FAIL")
            return False

        # if latest?
        remote_commit: str = gitcmd(toplevel, f"ls-remote '{url}' '{branch}' | cut -f1")
        local_commit: str = gitcmd(toplevel / path, f"rev-parse {branch}")
        lg.info(f"  checking commit: local: {local_commit}, remote: {remote_commit}")

        if remote_commit == local_commit:
            lg.info("    => PASS.")
        else:
            lg.info("    => FAIL")
            return False

    return True


def bump(toplevel: Path, path: Path, branch: str) -> bool:
    """bump submodule

    Args:
        toplevel (Path): `git rev-parse --show-toplevel`
        path (Path): submodule path
        branch (str): expected branch

    Returns:
        bool: True

    """
    lg.info(f"submodule-op::bump: {toplevel} @ {path}, branch: {branch}")

    # Get submodule url
    url: str = gitcmd(toplevel, f"config --get submodule.{path}.url")

    # check only owning repo
    if not url.startswith("git@github.com"):
        lg.info("  => external repository")
        return True
    else:
        _ = gitcmd(toplevel / path, f"checkout {branch}")

        remote_commit: str = gitcmd(toplevel, f"ls-remote '{url}' '{branch}' | cut -f1")
        local_commit: str = gitcmd(toplevel / path, f"rev-parse {branch}")
        lg.info(f"  checking commit: local: {local_commit}, remote: {remote_commit}")

        if remote_commit == local_commit:
            lg.info("    => up to date")
        else:
            lg.info("    => bump...")
            gitcmd(toplevel / path, f"pull origin {branch}")
            gitcmd(toplevel, f"add {path}")
            gitcmd(toplevel, f"commit -m ':pushpin: Bump {path}'")

    return True


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--op", type=str, choices=["check", "bump"], required=True, help="operation"
    )
    parser.add_argument(
        "--toplevel", type=Path, required=True, help="`git rev-parse--show-toplevel`"
    )
    parser.add_argument("--path", type=Path, required=True, help="submodule path")
    parser.add_argument("--branch", type=str, required=True, help="expected branch")
    args: Namespace = parser.parse_args()

    if args.op == "check":
        uptodate: bool = check(args.toplevel, args.path, args.branch)
        if not uptodate:
            exit(1)
        else:
            exit(0)

    elif args.op == "bump":
        _ = bump(args.toplevel, args.path, args.branch)
        exit(0)
