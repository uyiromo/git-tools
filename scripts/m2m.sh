#!/bin/bash
set -ue
set -o pipefail

# err MAGENTA
log_err() {
    printf "\033[38;5;201m[error] %s\033[0m\n" "$1"
}

# err CYAN
log_info() {
    printf "\033[38;5;84m[info] %s\033[0m\n" "$1"
}

gitcmd() {
    cmd="$1"

    printf "\033[38;5;84m  %% %s\033[0m\n" "${cmd}"
    eval "${cmd}"
}

log_info "m2m..."

# check args
if [[ "${1}" == "--no-verity" ]]; then
    no_verify="--no-verify"
else
    no_verify=""
fi

#
# MUST BE NOT ON *main* branch
#
branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "${branch}" == "main" ]]; then
    log_err "*main* BRANCH CANNOT BE MARGED TO *main*"
    return 1
fi

datetime=$(date "+%Y%m%d-%H%M%S.%N")

# 1. push to origin
# 2. stash current status to prevent unintended push
# 3. checkout main
# 4. merge branch
# 5. restore if needed

gitcmd "git push -u origin ${branch}" "${no_verify}"
gitcmd "git stash push -m ${datetime}"
gitcmd "git checkout main"
gitcmd "git merge ${branch} --no-ff --log -m \":twisted_rightwards_arrows: Merge branch '${branch}'\""
gitcmd "git push --no-verify -u origin main"

# restore
git checkout develop
index=$(git stash list | awk '/'"${datetime}"'$/ { print $0 }' | awk -F ":" '{ print $1 }')
if [[ $index != "" ]]; then
    git stash pop "${index}"
fi
