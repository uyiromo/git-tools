# git-tools
- my git tools (alias, hooks, scripts)

## init
```sh
GIT_USER_NAME="your name" GIT_USER_EMAIL="your email" ./init.sh
```


## git alias

| alias | command |
| --- | --- |
| `git a` | `git add` |
| `git amend` | `git commit --amend` |
| `git dif` | `git diff` |
| `git difc` | `git diff --cached` |
| `git ch` | `git checkout` |
| `git chm` | `git checkout main` |
| `git chd` | `git checkout develop` |
| `git st` | `git status -s` |
| `git sw` | `git switch` |
| `git swm` | `git switch main` |
| `git swd` | `git switch develop` |
| `git l1` | `git log --graph --oneline` |
| `git unstage` | `git reset HEAD` |
| `git bump` | `submodule-op --op bump --toplevel=$(git rev-parse --show-toplevel) --path=$1 --branch main` |
| `git bumpall` | `git submodule foreach "git -C \$toplevel bump \$path"` |
| `git m2m` | `m2m` |


## git hooks
- `hooks/commit-msg`
  - insert specified emojis to commit message
- `hooks/pre-commit`
  - disable direct commit to `main` branch
- `hooks/pre-push`
  - check if ALL submodules are up-to-date on `main` branch
  - check if ALL files are formatted and linted

