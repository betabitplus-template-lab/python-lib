#!/usr/bin/env bash
set -euo pipefail
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT
copier copy --defaults --vcs-ref HEAD . "$out/generated"
test -f "$out/generated/.copier-answers.yml"
test ! -e "$out/generated/_components"
! find "$out/generated" -type f -print0 | xargs -0 grep -IlZ $'<<<<<<<\|=======\|>>>>>>>' | grep -q .
