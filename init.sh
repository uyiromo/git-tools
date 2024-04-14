#!/bin/bash

safe_ln() {
    target="$1"
    link_name="$2"

    mkdir -p "$(dirname "${link_name}")"

    if [[ ! -e ${link_name} ]]; then
        ln -s "${target}" "${link_name}"
    fi
}

safe_ln "$(realpath gitcmd)" "${HOME}/.gitcmd"
safe_ln "$(realpath bump_submodule.py)" "${HOME}/bin/bump_submodule.py"

#
# eXecutable
#
chmod -R u+x hooks
chmod -R u+x scripts

#
# hooks
#
git config --global core.hooksPath "$(realpath hooks)"
