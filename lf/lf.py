#!/usr/bin/env python3
from __future__ import annotations

"""lf (linter/formatter) frontend"""

import json
import tomllib
from argparse import ArgumentParser, Namespace
from fnmatch import fnmatchcase
from hashlib import sha256
from os import chdir
from pathlib import Path
from typing import Callable, Dict, List, Set

from lang import Lang, lf_dockerfile, lf_javascript, lf_json, lf_md, lf_none, lf_py, lf_sh, lf_toml, lf_yaml
from util import err, info, runcmd

lf: Dict[Lang, Callable[[Path, Path], None]] = {
    Lang.md: lf_md,
    Lang.py: lf_py,
    Lang.sh: lf_sh,
    Lang.toml: lf_toml,
    Lang.yaml: lf_yaml,
    Lang.json: lf_json,
    Lang.javascript: lf_javascript,
    Lang.dockerfile: lf_dockerfile,
    Lang.none: lf_none,
}


def gitcmd(toplevel: Path, cmd: str) -> str:
    return runcmd(f"git -C '{str(toplevel)}' {cmd}", capture_output=True, check=True)


def detect_lang(langmap: Dict[Lang, List[str]], filename: str) -> Lang:
    """Detect corresponding `Lang` for filename"""

    lang_matching: Set[Lang] = set()
    for lang, patterns in langmap.items():
        if any(fnmatchcase(filename, pat) for pat in patterns):
            lang_matching.add(lang)
        else:
            pass

    # Matching rules:
    # 1. If mathing to "none", return "none"
    # 2. If mathing to only one language, return it
    # 3. Else, raise error
    if Lang.none in lang_matching:
        return Lang.none
    elif len(lang_matching) == 1:
        return lang_matching.pop()
    else:
        lang_s: str = ",".join(lang_matching)
        err(f"Ambiguous rules for '{filename}'. Matching: '{lang_s}'")
        raise KeyError(f"Ambiguous rules for '{filename}'")

    # never reach here
    return


def main(toplevel: Path, allow_dirty: bool) -> None:
    """Lint and Format files under toplevel"""
    chdir(toplevel)

    #
    # cache to reduce time
    #
    cache_json: Path = toplevel / ".lfcache.json"

    cache: Dict[str, str]
    if cache_json.exists():
        cache = json.loads(cache_json.read_text())
    else:
        cache = {}

    #
    # Must be clean
    #
    if gitcmd(toplevel, "status --porcelain") and not allow_dirty:
        err("Working directory is not clean. Specify --allow-dirty to proceed.")
        for line in gitcmd(toplevel, "status --porcelain").splitlines():
            err(f"  {line}")

        return
    else:
        pass

    #
    # Load config file
    #
    config: Path = toplevel / ".lfrules.toml"
    langmap: Dict[Lang, List[str]] = {Lang(k): v for k, v in tomllib.load(config.open("rb")).items()}

    #
    # Find git controlled files
    #
    files: List[str] = gitcmd(toplevel, "ls-files --exclude-standard").splitlines()

    #
    # Check files
    #
    n: int = len(files)
    for i, file in enumerate(files):
        info(f"[{i+1}/{n}]: '{file}'...")  # noqa: E226

        # check only regular files
        p: Path = toplevel / file
        if not (p.is_file() and not p.is_symlink()):
            info(f"  skip '{file}'")
        else:
            # if cached, skip
            digest_cache: str = cache.get(file, "")
            digest_file: str = sha256(p.read_bytes()).hexdigest()
            if digest_cache == digest_file:
                pass
            else:
                lang: Lang = detect_lang(langmap, file)
                info(f"  lang: {lang}")

                lf[lang](toplevel, p)
                gitcmd(toplevel, f"add {file}")

                # update cache
                cache[file] = digest_file
                cache_json.write_text(json.dumps(cache, indent=4))

    #
    # Commit if staged
    #
    if gitcmd(toplevel, "status --porcelain"):
        _ = gitcmd(toplevel, "commit -m ':art: Format'")
    else:
        info("No changes")

    # timestamp
    config.touch()

    return


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--toplevel", type=Path, required=True, help="Top level directory")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow dirty working directory")
    args: Namespace = parser.parse_args()

    # git top level is mounted at /mnt
    main(args.toplevel, args.allow_dirty)

    exit(0)
