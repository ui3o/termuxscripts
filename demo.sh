#!/bin/bash

[[ -n $DEMOSH ]] && exit 1
export DEMOSH=1
cd ~
[[ ! -d "~/termuxscripts" ]] && git clone https://github.com/ui3o/termuxscripts.git
cd ~/termuxscripts
git reset --hard
git pull
./$(basename "$0")
