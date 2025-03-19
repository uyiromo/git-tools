#!/bin/bash
set -ue
set -o pipefail

# username/email
git config --global user.name "${GIT_USER_NAME}"
git config --global user.email "${GIT_USER_EMAIL}"

# default editor
git config --replace-all core.editor vim

# Allow fast-forward marge only if pull
git config --global --add merge.ff false
git config --global --add pull.ff only

#
# scripts
#
mkdir -p "${HOME}/bin"
ln -sf "$(realpath ./scripts/m2m.sh)" "${HOME}/bin/m2m"
ln -sf "$(realpath ./scripts/submodule-op.py)" "${HOME}/bin/submodule-op"
ln -sf "$(realpath ./lf/lf.py)" "${HOME}/bin/lf"
ln -sf "$(realpath ./lf/lf-init.sh)" "${HOME}/bin/lf-init"

#
# hooks
#
hooksdir="$(realpath ./hooks)"
git config --global core.hooksPath "${hooksdir}"
chmod -R u+x "${hooksdir}"

#
# abbrev
#
git config --global alias.a 'add'
git config --global alias.amend 'commit --amend'
git config --global alias.dif 'diff'
git config --global alias.difc 'diff --cached'
git config --global alias.diffc 'diff --cached'
git config --global alias.ch 'checkout'
git config --global alias.chm 'checkout main'
git config --global alias.chd 'checkout develop'
git config --global alias.st 'status -s'
git config --global alias.sw 'switch'
git config --global alias.swm 'switch main'
git config --global alias.swd 'switch develop'
git config --global alias.l1 'log --graph --oneline'
git config --global alias.unstage 'reset HEAD'
# shellcheck disable=SC2016
git config --global alias.lf '!lf --toplevel=$(git rev-parse --show-toplevel)'
# shellcheck disable=SC2016
git config --global alias.lfdirty '!lf --toplevel=$(git rev-parse --show-toplevel) --allow-dirty'

# initialize repo
git config --global alias.init '!
git init
git switch --orphan main
git commit -m ":tada: origin" --allow-empty --no-verify

git switch --orphan develop
git commit -m ":tada: origin" --allow-empty --no-verify
'

# bump submodules
# shellcheck disable=SC2016
git config --global alias.bump '!f(){ submodule-op --op bump --toplevel=$(git rev-parse --show-toplevel) --path=$1 --branch main; }; f'
# shellcheck disable=SC2016
git config --global alias.bumpall '!git submodule foreach "git -C \$toplevel bump \$path"'

# merge to main
git config --global alias.m2m "! ${HOME}/bin/m2m"

# alias
# https://gitmoji.dev/
git config --global alias.commnew '! COMMITMSG_PREFIX=":sparkles:"     git commit '
git config --global alias.commfix '! COMMITMSG_PREFIX=":bug:"          git commit '
git config --global alias.commremove '! COMMITMSG_PREFIX=":fire:"         git commit '
git config --global alias.commformat '! COMMITMSG_PREFIX=":art:"          git commit '
git config --global alias.commrefact '! COMMITMSG_PREFIX=":recycle:"      git commit '
git config --global alias.commwip '! COMMITMSG_PREFIX=":construction:" git commit '
git config --global alias.commcfg '! COMMITMSG_PREFIX=":wrentch:"      git commit '
git config --global alias.commscript '! COMMITMSG_PREFIX=":hammer:"       git commit '
git config --global alias.commrename '! COMMITMSG_PREFIX=":truck:"        git commit '
git config --global alias.commchange '! COMMITMSG_PREFIX=":boom:"         git commit '
git config --global alias.commbump '! COMMITMSG_PREFIX=":pushpin:"      git commit '
git config --global alias.commdocs '! COMMITMSG_PREFIX=":memo:"         git commit '
git config --global alias.commtag '! COMMITMSG_PREFIX=":bookmark:"     git tag '
git config --global alias.commmerge '! COMMITMSG_PREFIX=":twisted_rightwards_arrows:" git commit '

# lf
docker build -t docker-lf docker-lf
