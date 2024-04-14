#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from color import Color, colorize
from util import ShResult, commit, eprint, fatal, sh


class Flake8Error:

    FORMAT: str = "%(row)d: %(code)s %(text)s"

    def __init__(self, line: str) -> Flake8Error:
        # Parse
        m: re.Match = re.fullmatch(r"(\d+): ([EFW]\d{3}) (.+)", line)

        self._row: int = int(m.group(1))
        self._code: str = m.group(2)
        self._text: str = m.group(3)

    @property
    def row(self) -> int:
        """int: the line number where the error is detected"""
        return self._row

    @property
    def code(self) -> str:
        """str: error code"""
        return self._code

    @property
    def text(self) -> str:
        """str: error text (detail)"""
        return self._text

    def __lt__(self, other: Flake8Error) -> bool:
        return (self.code < other.code) & (self.row < other.row)

    def __str__(self) -> str:
        lineno: int = self.row
        errcode: str = colorize(self.code, Color.X201_MAGENTA1)
        detail: str = self.text

        return f"{errcode}: L{lineno}: {detail}"


def flake8(topdir: Path, files: List[Path]) -> bool:
    """Check _path_ on _topdir_ using flake8

    Args:
        topdir (:obj:`Path`): top level dir (normally, parent of _gitdir_)
        files (:obj:`List[Path]`): python scripts

    Returns:
        bool: True if flake8 detects errors

    Raises:
        None

    """

    flake8_opt: str = f"--format='{Flake8Error.FORMAT}'"

    err: bool = False
    for file in files:
        print(topdir)
        r: ShResult = sh(
            f"cd '{topdir}' && flake8 {flake8_opt} '{str(file)}'",
            True,
            False,
        )
        err_file: bool = r.returncode != 0
        err = err | (r.returncode != 0)

        if err_file:
            # dump result
            errors: List[Flake8Error] = [Flake8Error(line) for line in r.stdout]
            errors.sort()

            eprint(f"  {colorize(str(file), Color.X84_SEAGREEN1)}")
            for error in errors:
                eprint(f"    {str(error)}")

    return err


def isort(topdir: Path, files: List[Path]) -> None:
    """Format _path_ on _topdir_ using isort

    Args:
        topdir (:obj:`Path`): top level dir (normally, parent of _gitdir_)
        files (:obj:`List[Path]`): python scripts

    Returns:
        None

    Raises:
        None

    """

    for file in files:
        r: ShResult = sh(
            f"cd '{topdir}' && isort '{str(file)}'",
            True,
            False,
        )

        if r.stdout:
            eprint(f"  Fixed: {str(file)}")
        else:
            pass


def black(topdir: Path, files: List[Path]) -> None:
    """Format _path_ on _topdir_ using black

    Args:
        topdir (:obj:`Path`): top level dir (normally, parent of _gitdir_)
        files (:obj:`List[Path]`): python scripts

    Returns:
        None

    Raises:
        None

    """

    for file in files:
        r: ShResult = sh(
            f"cd '{topdir}' && black '{str(file)}'",
            True,
            False,
        )

        if r.stdout:
            eprint(f"  Fixed: {str(file)}")
        else:
            pass


def format_py(topdir: Path, files: List[Path]) -> List[Path]:
    """Check format python-related files

    Args:
        topdir (:obj:`Path`): top level dir (normally, parent of _gitdir_)
        files (:obj:`List[Path]`): pushed files (absolute path)

    Returns:
        List[Path]: rest (not checked as python-related) files

    Raises:
        None

    """

    py: List[Path] = list()
    rest: List[Path] = list()
    for f in files:
        # 1. Ignore .flake8
        # 2. Check .py (lint: flake8, formatter: isort+black)
        # 3. Others
        if f.name == ".flake8":
            pass
        elif f.suffix == ".py":
            py.append(f)
        else:
            rest.append(f)

    eprint("*** format_py:isort")
    isort(topdir, py)

    eprint("*** format_py:black")
    black(topdir, py)

    eprint("*** format_py:commit")
    commit(topdir, py)

    eprint("*** format_py:flake8")
    err: bool = flake8(topdir, py)
    if err:
        fatal("flake8 detects errors!")

    return rest
