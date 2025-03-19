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


def fmt(cmd: str) -> None:
    runcmd(cmd, capture_output=False, check=False)
    return


def lint(cmd: str) -> None:
    runcmd(cmd, capture_output=False, check=True)
    return


def lf_md(confdir: Path, path: Path) -> None:
    """Markdown linter/formatter"""

    # check config files
    pass

    # format
    # - markdownlint
    fmt(f"markdownlint --fix '{str(path)}'")

    # lint
    # - markdownlint
    lint(f"markdownlint '{str(path)}'")

    return


def lf_py(confdir: Path, path: Path) -> None:
    """Python linter/formatter"""

    # check config files
    ensure("black", confdir / "pyproject.toml")
    ensure("flake8", confdir / ".flake8")

    # format
    # - isort
    # - black
    fmt(f"isort '{str(path)}'")
    fmt(f"black '{str(path)}'")

    # lint
    # - flake8
    lint(f"flake8 '{str(path)}'")

    return


def lf_sh(confdir: Path, path: Path) -> None:
    """Shell linter/formatter"""

    # check config files
    ensure("shfmt", confdir / ".editorconfig")

    # format
    # - shfmt
    fmt(f"shfmt -w '{str(path)}'")

    # lint
    # - shellcheck
    # - shck
    lint(f"shellcheck '{str(path)}'")
    lint(f"shck '{str(path)}'")

    return


def lf_toml(confdir: Path, path: Path) -> None:
    """TOML linter/formatter"""

    # check config files
    ensure("taplo", confdir / ".taplo.toml")

    # format
    # - taplo
    fmt(f"RUST_LOG=error taplo format '{str(path)}'")

    # lint
    # - taplo
    lint(f"RUST_LOG=error taplo lint '{str(path)}'")

    return


def lf_yaml(confdir: Path, path: Path) -> None:
    """YAML linter/formatter"""

    # check config files
    ensure("yamlfmt", confdir / ".yamlfmt")

    # format
    # - yamlfmt
    fmt(f"yamlfmt '{str(path)}'")

    # lint
    pass

    return


def lf_json(confdir: Path, path: Path) -> None:
    """JSON linter/formatter"""

    # check config files
    pass

    # format
    # - js-beautify
    fmt(f"js-beautify --replace --quiet '{str(path)}'")

    # lint
    pass

    return


def lf_javascript(confdir: Path, path: Path) -> None:
    """JavaScript linter/formatter"""

    # check config files
    ensure("eslint", confdir / "eslint.config.mjs")

    # format
    # - eslint
    fmt(f"eslint --fix '{str(path)}'")

    # lint
    # - eslint
    lint(f"eslint '{str(path)}'")

    return


def lf_dockerfile(confdir: Path, path: Path) -> None:
    """Dockerfile linter/formatter"""

    # check config files
    pass

    # format
    pass

    # lint
    lint(f"hadolint '{str(path)}'")

    return


def lf_none(confdir: Path, path: Path) -> None:
    """No-op linter/formatter"""

    # check config files
    pass

    # format
    pass

    # lint
    pass

    return
