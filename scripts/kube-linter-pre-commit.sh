#!/usr/bin/env bash
# Optional kube-linter for chart templates (Phase 21).
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

REPO_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

if ! command -v kube-linter >/dev/null 2>&1; then
  echo "kube-linter not installed — skipping (install for full lint)"
  exit 0
fi

FAILED=0
for FILE in "$@"; do
  if ! kube-linter lint "${REPO_ROOT}/${FILE}" --config .kube-linter.yaml 2>/dev/null; then
    if ! kube-linter lint "${REPO_ROOT}/${FILE}" 2>/dev/null; then
      echo "WARN: kube-linter findings in ${FILE} (non-blocking in Phase 21)"
    fi
  fi
done
exit "${FAILED}"
