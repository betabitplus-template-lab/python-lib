#!/usr/bin/env bash
set -euo pipefail
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT
copier copy --defaults --vcs-ref HEAD . "$out/generated"
test -f "$out/generated/.copier-answers.yml"
test ! -e "$out/generated/_components"
while IFS= read -r -d '' file; do
  if grep -q '^<<<<<<< ' "$file" && grep -q '^=======$' "$file" && grep -q '^>>>>>>> ' "$file"; then
    echo "Unresolved merge conflict markers in $file" >&2
    exit 1
  fi
done < <(find "$out/generated" -type f -print0)
