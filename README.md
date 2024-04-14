# Overview

- `bump_submodule.py`
  - bump submodules recursively, then commit if needed
- `gitcmd`
  - shell unitities
- `hooks`
  - `commit-msg`: commit hook, add `COMMITMSG_PREFIX` to COMMIT_EDITMSG if specified
  - `pre-commit`: commit hook, disable direct commits to main branch
  - `pre-push`: push hook, 1. ALL submodules must be latest, 2. All files must be formatted
- `scripts`
  - helper scripts for `hooks`

```sh
.
├── bump_submodule.py
├── gitcmd
├── hooks
│   ├── commit-msg
│   ├── pre-commit
│   └── pre-push
├── init.sh
└── scripts
    ├── color.py
    ├── format-checker.py
    ├── langs
    │   ├── python.py
    │   └── zsh.py
    ├── submodule-checker.py
    └── util.py
```

## usage

- `./init.sh` to configure git-tools
