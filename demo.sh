#!/bin/bash

[ -n $DEMOSH ] || echo demo.sh from home called && exit 1
export DEMOSH=1
[[ ! -d "~/termuxscripts" ]] && git clone https://github.com/ui3o/termuxscripts.git
cd ~/termuxscripts
git reset --hard
git pull
./$(basename "$0")