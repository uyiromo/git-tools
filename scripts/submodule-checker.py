#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from os import environ as env
from pathlib import Path
from subprocess import CompletedProcess, run
from sys import exit
from typing import List, Set


def eprint(msg: str) -> None:
    print(msg, flush=True)


def eprint_pass(msg: str) -> None:
    eprint(msg)


def eprint_fail(msg: str) -> None:
    eprint("\033[31m" + msg + "\033[30m")


#
# shell wrapper
#
@dataclass
class ShResult:
    returncode: int
    stdout: List[str]
    stderr: List[str]


def sh(cmd: str) -> ShResult:
    """Execute _cmd_"""

    eprint(f"% {cmd}")
    cp: CompletedProcess = run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )

    returncode: int = cp.returncode
    stdout: List[str] = cp.stdout.splitlines()
    stderr: List[str] = cp.stderr.splitlines()

    return ShResult(returncode, stdout, stderr)


#
# Git Module Wrapper
#
class GitModule:
    def __init__(self, root: Path, name: str):
        self._root: Path = root
        self._name: str = name
        self._submodules: List[GitModule] = list()

        self._checked: bool = False

    @staticmethod
    def build(root: Path, name: str) -> GitModule:
        """Build GitModule

        Args:
            root (:obj:`Path`): gitmodule directory
            name (:obj:`Path`): gitmodule name

        Returns:
            GitModule

        Raises:
            None

        """
        module: GitModule = GitModule(root, name)

        # Find submodules
        dotgitmodules: Path = root / ".gitmodules"
        submodules: List[str] = list()

        if dotgitmodules.exists():
            for line in dotgitmodules.open("r").readlines():
                line = line.strip()
                m: re.Match = re.match(r"path = (.+)", line)
                if m:
                    submodules.append(m.group(1))
                else:
                    pass
        else:
            pass

        submodules.sort()
        for submodule in submodules:
            module._submodules.append(GitModule.build(root / submodule, submodule))

        return module

    def mark(self) -> None:
        self._checked = True

    def dump(self, indent: str, last: bool, m: GitModule) -> None:
        """Dump _self_ and submodules using tree style

        Args:
            self (:obj:`GitModule`): self
            indent (:obj:`str`): indent string
            last (:obj:`bool`): True if dump _self_ as the last directory in same depth
            m (:obj:`GitModule`): the current checking module

        Returns:
            None

        Raises:
            None

        """
        arrow: str = "==>" if self == m else "   "
        mark: str = "*" if self._checked else " "

        # build tree-like str
        indent_m: str = "└──" if last else "├──"
        eprint(f"{arrow}{mark}{indent}{indent_m} {self.name}")

        # dump submodules
        indent_s: str = "    " if last else "│   "
        n: int = len(self.submodules) - 1
        for i, s in enumerate(self.submodules):
            s.dump(indent + indent_s, i == n, m)

    def gitcmd(self, gitcmd: str) -> List[str]:
        """Execute _gitcmd_ in self"""
        return sh(f"git -C '{self._root}' {gitcmd}").stdout

    @property
    def name(self) -> str:
        """str: module name"""
        return self._name

    @property
    def submodules(self) -> List[GitModule]:
        """List[GitModule]: submodules"""
        return self._submodules


def tree(root: GitModule, m: GitModule) -> None:
    """tree (mark _m_ as checking module)

    Args
        root (:obj:`GitModule`): the root
        m (:obj:`GitModule`): the current checking module

    Returns:
        None

    Raises:
        None

    """
    root.dump("", True, root)


def check(root: GitModule, m: GitModule, depth: int) -> None:
    """Check ALL submodules are latest and on main branch

    Args
        root (:obj:`GitModule`): the root
        m (:obj:`GitModule`): the current checking module
        depth (:obj:`int`): the depth from _root_ to _m_

    Returns:
        None

    Raises:
        None

    """
    dotskipmodules: Path = m._root / ".skipmodules"
    skipmodules: Set[str] = set()
    if dotskipmodules.exists():
        skipmodules = set(line.strip() for line in dotskipmodules.open("r").readlines())

    # check me
    if depth > 0:
        # dump module tree
        tree(root, m)

        # Check 1: on "main" branch or not
        eprint("1. Branch Checker")
        branch: str = m.gitcmd("describe --contains --all HEAD").pop()
        if branch == "main":
            eprint_pass("  -> Pass.")
        else:
            eprint_fail(f"  -> FAIL. Expected: 'main', Was: {branch}")
            exit(1)

        # Check 2: latest against remote (origin)
        eprint("2. Latest Checker")
        m.gitcmd("pull")  # always "main" branch
        diff: List[str] = m.gitcmd("diff origin/main")
        if not diff:
            eprint_pass("  -> Pass.")
        else:
            eprint_fail("  -> FAIL.")
            for d in diff:
                eprint_fail(f"    {d}")
            exit(1)

    # submodules
    for submodule in m.submodules:
        subname: str = submodule.name

        if subname in skipmodules:
            submodule.mark()
        else:
            check(root, submodule, depth + 1)

    # mark as checked
    m.mark()


if __name__ == "__main__":
    topdir: Path = Path(env["GIT_TOPDIR"])
    m: GitModule = GitModule.build(topdir, topdir.name)
    check(m, m, 0)

    exit(0)
