#!/bin/env bash

# qlu -q "$@" | sk -d '\t' --with-nth 2.. --preview 'qlu -g {1}'
qlu -q "$@" | fzf -d '\036' --with-nth='{2} {3}' --read0 --preview "echo {4} | html2text" --accept-nth 4 --preview-window=down,80% --bind="ctrl-f:preview-page-down,ctrl-b:preview-page-up" --info=inline --bind "enter:execute:(echo {4} | w3m -T text/html)"
