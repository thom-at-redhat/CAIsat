#!/usr/bin/env bash
# Lint Containerfiles with native hadolint, or container fallback for CI.
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

HADOLINT_ARGS=(--ignore DL3006 --ignore DL3016 --ignore DL3041 --ignore DL3059)
HADOLINT_IMAGE="ghcr.io/hadolint/hadolint:v2.14.0"

lint_with_native() {
  hadolint "${HADOLINT_ARGS[@]}" "$@"
}

lint_with_container() {
  local RUNNER="docker"
  if ! command -v docker >/dev/null 2>&1 && command -v podman >/dev/null 2>&1; then
    RUNNER="podman"
  fi

  local FILE
  for FILE in "$@"; do
    local ABS_FILE
    ABS_FILE="$(cd "$(dirname "${FILE}")" && pwd)/$(basename "${FILE}")"
    "${RUNNER}" run --rm -v "${ABS_FILE}:/tmp/Containerfile:ro" "${HADOLINT_IMAGE}" \
      hadolint "${HADOLINT_ARGS[@]}" /tmp/Containerfile
  done
}

if command -v hadolint >/dev/null 2>&1; then
  lint_with_native "$@"
elif command -v docker >/dev/null 2>&1 || command -v podman >/dev/null 2>&1; then
  lint_with_container "$@"
else
  echo "hadolint not installed and no container runtime available"
  exit 1
fi
