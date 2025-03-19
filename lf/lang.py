#!/usr/bin/env python3
from __future__ import annotations

"""lf (linter/formatter) core"""

from enum import Enum
from pathlib import Path

from util import runcmd


class Lang(Enum):
    """Supported languages"""

    md = "md"
    py = "py"
    sh = "sh"
    toml = "toml"
    yaml = "yaml"
    json = "json"
    javascript = "javascript"
    dockerfile = "dockerfile"
    none = "none"

    @staticmethod
    def from_str(lang: str) -> Lang:
        """Get Lang from string"""
        return Lang(lang.lower())


def ensure(requirer: str, path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"`{requirer}` requires `{path}`")
    else:
        pass

    return


def dockercmd(toplevel: Path, cmd: str) -> str:
    tpl: str = str(toplevel)
    return f'docker run --rm --user $(id -u):$(id -g) -v {tpl}:{tpl}:Z --workdir {tpl} docker-lf /bin/bash -c "{cmd}"'


def fmt(toplevel: Path, cmd: str) -> None:
    runcmd(dockercmd(toplevel, cmd), capture_output=False, check=False)
    return


def lint(toplevel: Path, cmd: str) -> None:
    runcmd(dockercmd(toplevel, cmd), capture_output=False, check=True)
    return


def lf_md(toplevel: Path, path: Path) -> None:
    """Markdown linter/formatter"""

    # check config files
    pass

    # format
    # - markdownlint
    fmt(toplevel, f"markdownlint --fix '{str(path)}'")

    # lint
    # - markdownlint
    lint(toplevel, f"markdownlint '{str(path)}'")

    return


def lf_py(toplevel: Path, path: Path) -> None:
    """Python linter/formatter"""

    # check config files
    ensure("black", toplevel / "pyproject.toml")
    ensure("flake8", toplevel / ".flake8")

    # format
    # - isort
    # - black
    fmt(toplevel, f"isort '{str(path)}'")
    fmt(toplevel, f"black '{str(path)}'")

    # lint
    # - flake8
    lint(toplevel, f"flake8 '{str(path)}'")

    return


def lf_sh(toplevel: Path, path: Path) -> None:
    """Shell linter/formatter"""

    # check config files
    ensure("shfmt", toplevel / ".editorconfig")

    # format
    # - shfmt
    fmt(toplevel, f"shfmt -w '{str(path)}'")

    # lint
    # - shellcheck
    # - shck
    lint(toplevel, f"shellcheck '{str(path)}'")
    lint(toplevel, f"shck '{str(path)}'")

    return


def lf_toml(toplevel: Path, path: Path) -> None:
    """TOML linter/formatter"""

    # check config files
    ensure("taplo", toplevel / ".taplo.toml")

    # format
    # - taplo
    fmt(toplevel, f"RUST_LOG=error taplo format '{str(path)}'")

    # lint
    # - taplo
    lint(toplevel, f"RUST_LOG=error taplo lint '{str(path)}'")

    return


def lf_yaml(toplevel: Path, path: Path) -> None:
    """YAML linter/formatter"""

    # check config files
    ensure("yamlfmt", toplevel / ".yamlfmt")

    # format
    # - yamlfmt
    fmt(toplevel, f"yamlfmt '{str(path)}'")

    # lint
    pass

    return


def lf_json(toplevel: Path, path: Path) -> None:
    """JSON linter/formatter"""

    # check config files
    pass

    # format
    # - js-beautify
    fmt(toplevel, f"js-beautify --replace --quiet '{str(path)}'")

    # lint
    pass

    return


def lf_javascript(toplevel: Path, path: Path) -> None:
    """JavaScript linter/formatter"""

    # check config files
    ensure("eslint", toplevel / "eslint.config.mjs")

    # format
    # - eslint
    fmt(toplevel, f"eslint --fix '{str(path)}'")

    # lint
    # - eslint
    lint(toplevel, f"eslint '{str(path)}'")

    return


def lf_dockerfile(toplevel: Path, path: Path) -> None:
    """Dockerfile linter/formatter"""

    # check config files
    pass

    # format
    pass

    # lint
    lint(toplevel, f"hadolint '{str(path)}'")

    return


def lf_none(toplevel: Path, path: Path) -> None:
    """No-op linter/formatter"""

    # check config files
    pass

    # format
    pass

    # lint
    pass

    return
