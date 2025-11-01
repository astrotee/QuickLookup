#!/bin/env bash

get1="w3m -T text/html -dump <<<{4}"
get2='qlu -g {1} | w3m -T text/html'
get3="w3m -T text/html -dump {4}"
get4="w3m -T text/html {4}"
# qlu -q "$@" | sk -d '\t' --with-nth 2.. --preview 'qlu -g {1}'
qlu -q "$@" | fzf --reverse -d '\036' --with-nth='{2} {3}' --read0 \
  --preview "$get3 || $get2" --accept-nth 4 \
  --preview-window=down,80% \
  --bind="ctrl-f:preview-page-down,ctrl-b:preview-page-up" \
  --info=inline --bind "enter:execute:($get4)"
