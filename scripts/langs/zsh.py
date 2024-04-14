#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import List


def format_zsh(topdir: Path, files: List[Path]) -> List[Path]:
    """Check format zsh-related files

    Args:
        topdir (:obj:`Path`): top level dir (normally, parent of _gitdir_)
        files (:obj:`List[Path]`): pushed files (absolute path)

    Returns:
        List[Path]: rest (not checked as zsh-related) files

    Raises:
        None

    """

    zsh: List[Path] = list()
    rest: List[Path] = list()
    for f in files:
        # 1. Check .zshrc (lint: None, formatter: None)
        # 2. Others
        if f.name == ".zshrc":
            zsh.append(f)
        else:
            rest.append(f)

    return rest
