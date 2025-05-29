#!/bin/bash

[[ -n $DEMOSH ]] && exit 1
export DEMOSH=1
cd ~
git clone https://github.com/ui3o/termuxscripts.git || echo termuxscripts.git is already cloned...
cd ~/termuxscripts
git reset --hard
git pull
./$(basename "$0")
