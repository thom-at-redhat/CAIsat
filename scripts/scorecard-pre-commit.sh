#!/usr/bin/env bash
# Full-repo OpenSSF Scorecard scan for pre-commit (read-only; does not publish).
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

SCORECARD_IMAGE="${SCORECARD_IMAGE:-ghcr.io/ossf/scorecard:v5.5.0}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORK_TREE="$(mktemp -d)"
RESULTS_FILE="$(mktemp)"
LOG_FILE="$(mktemp)"
trap 'command rm -rf "${WORK_TREE}"; command rm -f "${RESULTS_FILE}" "${LOG_FILE}"' EXIT

if ! command -v podman >/dev/null 2>&1; then
    printf 'scorecard pre-commit: podman is required (https://podman.io/)\n' >&2
    exit 1
fi

cd "${REPO_ROOT}"
TREE="$(git write-tree)"
git archive "${TREE}" | tar -x -C "${WORK_TREE}"

PODMAN_ARGS=(run --rm --user 0 -v "${WORK_TREE}:/src:z" -w /src)
if [[ -n "${GITHUB_AUTH_TOKEN:-}" ]]; then
    PODMAN_ARGS+=(-e "GITHUB_AUTH_TOKEN=${GITHUB_AUTH_TOKEN}")
else
    printf 'scorecard pre-commit: GITHUB_AUTH_TOKEN unset — some checks may be incomplete\n' >&2
fi

set +o errexit
podman "${PODMAN_ARGS[@]}" "${SCORECARD_IMAGE}" \
    --local=/src --format=json --show-details >"${RESULTS_FILE}" 2>"${LOG_FILE}"
SCAN_EXIT=$?
set -o errexit

if [[ ! -s "${RESULTS_FILE}" ]]; then
    printf 'scorecard pre-commit: scan produced no JSON output\n' >&2
    cat "${LOG_FILE}" >&2
    exit 1
fi

if [[ "${SCAN_EXIT}" -ne 0 ]]; then
    grep -v 'skipping dangling symlink' "${LOG_FILE}" >&2 || true
fi

python3 - "${RESULTS_FILE}" <<'PY'
import json
import sys

ACTIONABLE = {
    "Binary-Artifacts",
    "Dangerous-Workflow",
    "License",
    "Pinned-Dependencies",
    "SAST",
    "Security-Policy",
    "Token-Permissions",
    "Vulnerabilities",
}

results_path = sys.argv[1]
with open(results_path, encoding="utf-8") as handle:
    data = json.load(handle)

score = data.get("score", "?")
checks = data.get("checks") or []
failures = [
    check
    for check in checks
    if check.get("name") in ACTIONABLE and check.get("score") == 0
]
errors = [
    check
    for check in checks
    if check.get("name") in ACTIONABLE and check.get("score") == -1
]

print(f"OpenSSF Scorecard aggregate score: {score}")
for check in checks:
    name = check.get("name", "?")
    check_score = check.get("score", "?")
    print(f"  {name}: {check_score}/10")

if errors:
    print("\nActionable checks could not run (internal error):", file=sys.stderr)
    for check in errors:
        print(f"  {check['name']}: {check.get('reason', '')}", file=sys.stderr)
    sys.exit(1)

if failures:
    print("\nActionable checks scored 0:", file=sys.stderr)
    for check in failures:
        print(f"  {check['name']}: {check.get('reason', '')}", file=sys.stderr)
    sys.exit(1)
PY
