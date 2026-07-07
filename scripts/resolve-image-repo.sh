#!/usr/bin/env bash
# Resolve CAISAT_IMAGE_REPO or read frontend.image.repository from chart/values.yaml.
# Usage: source scripts/resolve-image-repo.sh && caisat_resolve_image_repo <label> <values-file>
# Assisted by: cursor, claude

caisat_resolve_image_repo() {
    local LABEL="${1:?}"
    local VALUES_FILE="${2:?}"

    if [[ -n "${CAISAT_IMAGE_REPO:-}" ]]; then
        if [[ -z "${CAISAT_IMAGE_REPO//[[:space:]]/}" ]]; then
            printf '%s: CAISAT_IMAGE_REPO is empty\n' "${LABEL}" >&2
            return 1
        fi
        printf '%s' "${CAISAT_IMAGE_REPO}"
        return 0
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        printf '%s: set CAISAT_IMAGE_REPO or install python3 to read %s\n' "${LABEL}" "${VALUES_FILE}" >&2
        return 1
    fi

    local REPO
    if ! REPO="$(
        python3 - "${LABEL}" "${VALUES_FILE}" <<'PY'
import sys
from pathlib import Path

label = sys.argv[1]
values_path = Path(sys.argv[2])

try:
    import yaml
except ImportError:
    print(f"{label}: PyYAML required to read chart values (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)

if not values_path.is_file():
    print(f"{label}: values file not found: {values_path}", file=sys.stderr)
    sys.exit(1)

try:
    data = yaml.safe_load(values_path.read_text())
    repo = data["frontend"]["image"]["repository"]
except (TypeError, KeyError, AttributeError):
    print(f"{label}: frontend.image.repository missing in {values_path}", file=sys.stderr)
    sys.exit(1)

if not isinstance(repo, str) or not repo.strip():
    print(f"{label}: frontend.image.repository is empty in {values_path}", file=sys.stderr)
    sys.exit(1)

print(repo.strip())
PY
    )"; then
        return 1
    fi

    if [[ -z "${REPO}" ]]; then
        printf '%s: frontend.image.repository resolved to an empty value\n' "${LABEL}" >&2
        return 1
    fi

    printf '%s' "${REPO}"
}
