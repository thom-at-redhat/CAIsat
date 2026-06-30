#!/usr/bin/env bash
# Manual full --repo OpenSSF Scorecard scan (read-only; does not publish).
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

SCORECARD_IMAGE="${SCORECARD_IMAGE:-ghcr.io/ossf/scorecard:v5.5.0}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
OUTPUT_FILE="${REPO_ROOT}/scorecard-local.json"

resolve_scorecard_repo() {
    local REMOTE_URL
    REMOTE_URL="$(git -C "${REPO_ROOT}" remote get-url origin 2>/dev/null || true)"
    if [[ "${REMOTE_URL}" =~ github\.com[:/]([^/]+/[^/.]+) ]]; then
        printf 'github.com/%s\n' "${BASH_REMATCH[1]%.git}"
        return 0
    fi
    printf 'scorecard-local: set SCORECARD_REPO=github.com/owner/repo (could not parse origin remote)\n' >&2
    return 1
}

if ! command -v podman >/dev/null 2>&1; then
    printf 'scorecard-local: podman is required (https://podman.io/)\n' >&2
    exit 1
fi

if [[ -z "${GITHUB_AUTH_TOKEN:-}" ]]; then
    printf 'scorecard-local: GITHUB_AUTH_TOKEN is required (fine-grained PAT with contents:read)\n' >&2
    exit 1
fi

SCORECARD_REPO="${SCORECARD_REPO:-$(resolve_scorecard_repo)}"

printf 'Running Scorecard against %s (output: %s)\n' "${SCORECARD_REPO}" "${OUTPUT_FILE}"

podman run --rm --user 0 \
    -v "${REPO_ROOT}:/src:z" \
    -w /src \
    -e "GITHUB_AUTH_TOKEN=${GITHUB_AUTH_TOKEN}" \
    "${SCORECARD_IMAGE}" \
    --repo="${SCORECARD_REPO}" \
    --format=json \
    --show-details \
    -o /src/scorecard-local.json

printf 'Done. Aggregate score: '
python3 - "${OUTPUT_FILE}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
print(data.get("score", "?"))
PY
