#!/usr/bin/env python3
from __future__ import annotations

from os import environ as env
from pathlib import Path
from sys import argv, exit
from typing import List, Set

from langs.python import format_py
from langs.zsh import format_zsh
from util import fatal, gitcmd


def get_pushed_files(
    gitdir: Path, local_commitid: str, remote_commitid: str
) -> List[Path]:
    """Get file list that will be pushed

    Args:
        gitdir (:obj:`Path`): .git dir
        local_commitid (:obj:`str`): local commit ID
        remove_commitid (:obj:`str`): remote commit ID

    Returns:
        List[Path]: absolute pathes of pushed files

    Raises:
        None

    """

    cmd: str = f"diff {local_commitid} {remote_commitid} --name-only"
    files: List[str] = gitcmd(topdir, cmd).stdout

    # ignore submodules
    cmd: str = "submodule status"
    submodules: Set[str] = set(
        [line.strip().split(" ")[1] for line in gitcmd(topdir, cmd).stdout]
    )

    return [Path(f) for f in files if f not in submodules]


if __name__ == "__main__":
    local_commitid: str
    remote_commitid: str

    # local_ref local_commitid remote_ref remote_commitid
    _, local_commitid, _, remote_commitid = argv[1:]

    if local_commitid == "" and remote_commitid == "":
        # latest against remote
        pass
    else:
        gitdir: Path = Path(env["GIT_DIR"])
        topdir: Path = Path(env["GIT_TOPDIR"])
        files: List[Path] = get_pushed_files(gitdir, local_commitid, remote_commitid)

        # ignore files
        ignore_files: Set[str] = ("requirements.txt",)
        files = list(filter(lambda p: p.name not in ignore_files, files))

        # format
        files = format_py(topdir, files)
        files = format_zsh(topdir, files)
        if files:
            rest_files: str = "\n".join([f"  {file}" for file in files])
            fatal(f"Some files are not checked...\n{rest_files}")
        else:
            pass

    exit(0)
