#!/usr/bin/env python3
from __future__ import annotations

from subprocess import run, CompletedProcess
from pathlib import Path
from typing import Set, List
import re


def eprint(msg: str) -> None:
    print(msg, flush=True)


def run_and_check(cmd: str) -> str:
    eprint(f"% {cmd}")
    cp: CompletedProcess = run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )
    if cp.returncode != 0:
        eprint(f"stdout: '{cp.stdout}'")
        eprint(f"stderr: '{cp.stderr}'")
        exit(1)

    return cp.stdout.strip()


class GitModule:
    def __init__(self, root: Path, name: str):
        self._root: Path = root
        self._name: str = name
        self._submodules: List[GitModule] = list()

        self._treestr: str = None
        self._marked: bool = False

    def add_submodule(self, submodule: GitModule) -> None:
        self._submodules.append(submodule)

    def get_submodule(self, name: str) -> GitModule:
        return [s for s in self._submodules if s.name == name].pop()

    def mark(self) -> None:
        self._marked = True

    def dump(self, m: GitModule) -> None:
        arrow: str = ""
        if self == m:
            arrow = "==>"
        else:
            arrow = "   "

        mark: str = ""
        if self._marked:
            mark = "*"
        else:
            mark = " "

        eprint(f"{arrow}{mark}{self.treestr}")

        for s in self.submodules:
            s.dump(m)

    def tree(self, heading: str, last: bool) -> None:
        heading_m: str = str(heading)
        heading_s: str = str(heading)
        if last:
            heading_m += "└──"
            heading_s += "    "
        else:
            heading_m += "├──"
            heading_s += "│   "

        self._treestr = f"{heading_m} {self.name}"

        n: int = len(self.submodules) - 1
        for i, s in enumerate(self.submodules):
            s.tree(heading_s, i == n)

    def exec_cmd(self, gitcmd: str) -> str:
        return run_and_check(f"git -C '{self._root}' {gitcmd}")

    @property
    def treestr(self) -> str:
        return self._treestr

    @property
    def name(self) -> str:
        return self._name

    @property
    def submodules(self) -> List[GitModule]:
        return self._submodules


def dfs(root: Path, name: str) -> GitModule:
    """Build GitRepo using Depth-First Search"""
    module: GitModule = GitModule(root, name)

    dotgitmodules: Path = root / ".gitmodules"
    if dotgitmodules.exists():
        submodules: List[str] = list()
        for line in dotgitmodules.open("r").readlines():
            line = line.strip()
            m: re.Match = re.match(r"path = (.+)", line)
            if m:
                submodules.append(m.group(1))

        submodules.sort()
        for submodule in submodules:
            module.add_submodule(dfs(root / submodule, submodule))

    return module


def bump(root: GitModule, m: GitModule, depth: int) -> None:
    # checkout m
    root.dump(m)
    m.exec_cmd("checkout develop")
    m.exec_cmd("pull")
    m.exec_cmd("checkout main")
    m.exec_cmd("pull")

    submodules: List[GitModule] = m.submodules

    # get submodules/skipmodules
    dotskipmodules: Path = m._root / ".skipmodules"
    skipmodules: Set[str] = set()
    if dotskipmodules.exists():
        skipmodules = set(line.strip() for line in dotskipmodules.open("r").readlines())

    # bump
    for submodule in submodules:
        subname: str = submodule.name

        if subname in skipmodules:
            continue

        bump(root, submodule, depth + 1)

        root.dump(m)
        # if no diff, do nothing
        diff: str = m.exec_cmd("diff --numstat | wc -l")
        if diff == "0":
            continue

        # diff contains the submodule?
        status: List[str] = [s.strip() for s in m.exec_cmd("status -s").splitlines()]
        submodule_m: str = f"M {subname}"
        if submodule_m in status:
            # some submodules were updated
            m.exec_cmd("checkout develop")
            m.exec_cmd(f"add {subname}")
            m.exec_cmd(f"commit --no-verify -m  'Bump {subname}'")

            # merge to main
            m.exec_cmd("push -u origin develop")
            m.exec_cmd("checkout main")
            m.exec_cmd("merge develop --no-ff --no-edit")
            m.exec_cmd("push -u origin main")

        # return to main-branch
        m.exec_cmd("checkout main")

    m.mark()


if __name__ == "__main__":
    root: Path = Path(".").absolute()
    m: GitModule = dfs(root, root.name)
    m.tree("", True)
    m.exec_cmd("reset")
    bump(m, m, 0)
