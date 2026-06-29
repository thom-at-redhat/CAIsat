#!/usr/bin/env bash
# Reject private cluster FQDNs, RFC1918 IPs, and personal identifiers in tracked files.
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

FAILED=0

check_pattern() {
    local DESC="${1}"
    local PATTERN="${2}"
    shift 2
    local MATCHES
    MATCHES="$(grep -En "${PATTERN}" "${@}" 2>/dev/null || true)"
    if [[ -n "${MATCHES}" ]]; then
        printf 'FAIL: %s\n' "${DESC}"
        printf '%s\n' "${MATCHES}"
        FAILED=1
    fi
}

if [[ "${#}" -gt 0 ]]; then
    FILES=("${@}")
else
    mapfile -t FILES < <(git ls-files)
fi

FILTERED=()
for FILE in "${FILES[@]}"; do
    case "${FILE}" in
        .secrets.baseline|frontend/package-lock.json|*.png|*.jpg|*.jpeg|*.gif|*.webp|*.onnx|*.pt|*.pth)
            continue
            ;;
        scripts/check-no-cluster-info.sh)
            continue
            ;;
    esac
    [[ -f "${FILE}" ]] && FILTERED+=("${FILE}")
done

if [[ "${#FILTERED[@]}" -eq 0 ]]; then
    exit 0
fi

while IFS= read -r -d '' FILE; do
    MATCHES="$(grep -En '\.apps\.[a-z0-9-]+\.(com|io|net|local)' "${FILE}" 2>/dev/null | grep -Ev 'your-cluster|example\.com|<cluster>|\<cluster\>' || true)"
    if [[ -n "${MATCHES}" ]]; then
        printf 'FAIL: OpenShift apps domain\n%s\n' "${MATCHES}"
        FAILED=1
    fi
done < <(printf '%s\0' "${FILTERED[@]}")

check_pattern "Private IP address" \
    '\b(10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3})\b' \
    "${FILTERED[@]}"

check_pattern "Hardcoded cluster.local service URL" \
    'https?://[^/<]*\.caisat\.svc\.cluster\.local' \
    "${FILTERED[@]}"

check_pattern "Personal Quay org reference" \
    'quay\.io/sara_banderby' \
    "${FILTERED[@]}"

PERSONAL_MATCHES="$(grep -En '(thom-at-redhat|thom_at_redhat|quay\.io/thom_at_redhat)' "${FILTERED[@]}" 2>/dev/null | grep -Ev 'scorecard\.dev' || true)"
if [[ -n "${PERSONAL_MATCHES}" ]]; then
    printf 'FAIL: Personal identifier (GitHub fork / Quay user)\n'
    printf '%s\n' "${PERSONAL_MATCHES}"
    FAILED=1
fi

check_pattern "kubeconfig file path" \
    '\.kube/config|KUBECONFIG=/' \
    "${FILTERED[@]}"

if [[ "${FAILED}" -ne 0 ]]; then
    exit 1
fi

exit 0
