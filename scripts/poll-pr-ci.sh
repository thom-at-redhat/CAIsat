#!/usr/bin/env bash
# Assisted by: cursor, claude
# Poll GitHub PR checks until all complete (success/neutral/skipped) or a failure.
# Uses gh JSON + jq — never grep '\t' on tab-separated gh pr checks output (stray \\ warning).
set -o errexit -o nounset -o pipefail

usage() {
    echo "Usage: $0 PR_NUMBER [REPO] [MAX_POLLS] [SLEEP_SEC]" >&2
    echo "  REPO defaults to gh repo view nameWithOwner (current checkout)" >&2
    exit 1
}

[[ "${#}" -ge 1 ]] || usage

PR="${1}"
REPO="${2:-$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || true)}"
[[ -n "${REPO}" ]] || {
    echo "REPO required (pass as second argument or run inside a git checkout with gh auth)" >&2
    usage
}
MAX_POLLS="${3:-40}"
SLEEP_SEC="${4:-15}"

for I in $(seq 1 "${MAX_POLLS}"); do
    echo "--- poll ${I} ---"
    ROLLUP="$(gh pr view "${PR}" --repo "${REPO}" --json statusCheckRollup 2>/dev/null)"
    echo "${ROLLUP}" | jq -r '.statusCheckRollup[] | "\(.name): \(.status) \(.conclusion // "n/a")"'
    PENDING="$(echo "${ROLLUP}" | jq '[.statusCheckRollup[] | select(.status != "COMPLETED")] | length')"
    if [[ "${PENDING}" == "0" ]]; then
        FAILED="$(echo "${ROLLUP}" | jq '[.statusCheckRollup[] | select(.conclusion != null and .conclusion != "SUCCESS" and .conclusion != "NEUTRAL" and .conclusion != "SKIPPED")] | length')"
        if [[ "${FAILED}" == "0" ]]; then
            echo "ALL_GREEN"
            exit 0
        fi
        echo "FAILED (${FAILED} check(s))"
        exit 1
    fi
    sleep "${SLEEP_SEC}"
done

echo "TIMEOUT after ${MAX_POLLS} polls"
exit 2
