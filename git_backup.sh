#!/bin/bash

cd ~/dotfiles || exit

# find . -name ".DS_Store" -print -delete || exit

git add .

git commit -m "repo backup: $(date '+%Y-%m-%d %H:%M:%S')"

git push origin main 
