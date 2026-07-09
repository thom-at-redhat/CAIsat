#!/usr/bin/env bash
# Probe CAIsat backend Routes for CORS headers (Brazil / cross-origin troubleshooting).
# Usage:
#   FRONTEND_URL=https://caisat-caisat.apps.example.com/caisat scripts/cors-probe.sh
#   FRONTEND_ORIGIN=https://... ENHANCE_URL=... DETECT_URL=... CHANGE_URL=... scripts/cors-probe.sh
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

if ! command -v curl >/dev/null 2>&1; then
    echo "cors-probe: curl is required (dnf install curl)" >&2
    exit 1
fi

FRONTEND_URL="${FRONTEND_URL:-}"
FRONTEND_ORIGIN="${FRONTEND_ORIGIN:-${FRONTEND_URL}}"
ENHANCE_URL="${ENHANCE_BACKEND_URL:-${ENHANCE_URL:-}}"
DETECT_URL="${DETECTION_BACKEND_URL:-${DETECT_URL:-}}"
CHANGE_URL="${CHANGEDETECTION_BACKEND_URL:-${CHANGE_URL:-}}"

derive_host_from_url() {
    local URL="${1}"
    local STRIPPED="${URL#*://}"
    echo "${STRIPPED%%/*}"
}

derive_backend_url() {
    local FRONTEND_HOST="${1}"
    local REPLACEMENT="${2}"
    if [[ "${FRONTEND_HOST}" == *localhost* ]]; then
        case "${REPLACEMENT}" in
            caisat-backend) echo "http://127.0.0.1:${ENHANCE_PORT:-8000}" ;;
            caisat-detection-backend) echo "http://127.0.0.1:${DETECTION_PORT:-8001}" ;;
            caisat-backend-changedetection) echo "http://127.0.0.1:${CHANGE_PORT:-8080}" ;;
            *) echo "unknown replacement ${REPLACEMENT}" >&2; return 1 ;;
        esac
        return 0
    fi
    local PROTO="${FRONTEND_ORIGIN%%://*}"
    local HOST_REPLACED="${FRONTEND_HOST/caisat/${REPLACEMENT}}"
    echo "${PROTO}://${HOST_REPLACED}"
}

if [[ -n "${FRONTEND_ORIGIN}" ]]; then
    FRONTEND_HOST="$(derive_host_from_url "${FRONTEND_ORIGIN}")"
    FRONTEND_ORIGIN="${FRONTEND_ORIGIN%%/}"
    if [[ -z "${ENHANCE_URL}" ]]; then
        ENHANCE_URL="$(derive_backend_url "${FRONTEND_HOST}" "caisat-backend")"
    fi
    if [[ -z "${DETECT_URL}" ]]; then
        DETECT_URL="$(derive_backend_url "${FRONTEND_HOST}" "caisat-detection-backend")"
    fi
    if [[ -z "${CHANGE_URL}" ]]; then
        CHANGE_URL="$(derive_backend_url "${FRONTEND_HOST}" "caisat-backend-changedetection")"
    fi
fi

if [[ -z "${FRONTEND_ORIGIN}" || -z "${ENHANCE_URL}" || -z "${DETECT_URL}" || -z "${CHANGE_URL}" ]]; then
    echo "Usage: FRONTEND_URL=https://<frontend-route>/ scripts/cors-probe.sh" >&2
    echo "   or: FRONTEND_ORIGIN=... ENHANCE_URL=... DETECT_URL=... CHANGE_URL=... scripts/cors-probe.sh" >&2
    exit 1
fi

PASS_COUNT=0
FAIL_COUNT=0
PROBE_TMP="${TMPDIR:-/tmp}/caisat-cors-probe-$$"
mkdir -p "${PROBE_TMP}"
trap 'command rm -rf "${PROBE_TMP}"' EXIT

is_invalid_cors() {
    local ALLOW_ORIGIN="${1:-}"
    local ALLOW_CREDENTIALS="${2:-}"
    [[ "${ALLOW_ORIGIN}" == "*" && "${ALLOW_CREDENTIALS}" == "true" ]]
}

probe_cors() {
    local NAME="${1}"
    local BASE_URL="${2}"
    local PATH="${3}"
    local METHOD="${4:-GET}"
    local URL="${BASE_URL%/}${PATH}"
    local PATH_SLUG="${PATH//\//-}"
    local HEADERS_FILE="${PROBE_TMP}/${NAME}-${METHOD}-${PATH_SLUG}.headers"
    local HTTP_CODE

    if [[ "${METHOD}" == "OPTIONS" ]]; then
        HTTP_CODE="$(curl -sS -o /dev/null -w '%{http_code}' -D "${HEADERS_FILE}" -X OPTIONS \
            -H "Origin: ${FRONTEND_ORIGIN}" \
            -H "Access-Control-Request-Method: GET" \
            "${URL}" || echo "000")"
    else
        HTTP_CODE="$(curl -sS -o /dev/null -w '%{http_code}' -D "${HEADERS_FILE}" \
            -H "Origin: ${FRONTEND_ORIGIN}" \
            "${URL}" || echo "000")"
    fi

    local ALLOW_ORIGIN ALLOW_CREDENTIALS VARY
    ALLOW_ORIGIN="$(grep -i '^access-control-allow-origin:' "${HEADERS_FILE}" | tail -1 | cut -d: -f2- | tr -d ' \r\n' || true)"
    ALLOW_CREDENTIALS="$(grep -i '^access-control-allow-credentials:' "${HEADERS_FILE}" | tail -1 | cut -d: -f2- | tr -d ' \r\n' || true)"
    VARY="$(grep -i '^vary:' "${HEADERS_FILE}" | tail -1 | cut -d: -f2- | tr -d ' \r\n' || true)"

    echo "== ${NAME} ${METHOD} ${PATH} (${URL}) =="
    echo "   HTTP ${HTTP_CODE}"
    echo "   access-control-allow-origin: ${ALLOW_ORIGIN:-<missing>}"
    echo "   access-control-allow-credentials: ${ALLOW_CREDENTIALS:-<missing>}"
    echo "   vary: ${VARY:-<missing>}"

    local STATUS="PASS"
    if [[ "${HTTP_CODE}" == "000" ]]; then
        STATUS="FAIL"
        echo "   FAIL: connection error (DNS/TLS/firewall?)"
    elif is_invalid_cors "${ALLOW_ORIGIN}" "${ALLOW_CREDENTIALS}"; then
        STATUS="FAIL"
        echo "   FAIL: invalid CORS — Allow-Origin * with Allow-Credentials true"
    elif [[ "${METHOD}" == "GET" && -z "${ALLOW_ORIGIN}" ]]; then
        STATUS="FAIL"
        echo "   FAIL: missing Access-Control-Allow-Origin on GET response"
    elif [[ "${ALLOW_ORIGIN}" != "*" && "${ALLOW_ORIGIN}" != "${FRONTEND_ORIGIN}" ]]; then
        echo "   WARN: Allow-Origin does not echo frontend Origin (may still work if allow-listed)"
    fi

    if [[ "${STATUS}" == "PASS" ]]; then
        echo "   PASS"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "   ${STATUS}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo
}

echo "CAIsat CORS probe"
echo "  frontend Origin: ${FRONTEND_ORIGIN}"
echo "  enhance:         ${ENHANCE_URL}"
echo "  detection:       ${DETECT_URL}"
echo "  changedetection: ${CHANGE_URL}"
echo

probe_cors "enhance" "${ENHANCE_URL}" "/api/capabilities" "GET"
probe_cors "enhance" "${ENHANCE_URL}" "/api/enhance" "OPTIONS"
probe_cors "detection" "${DETECT_URL}" "/health" "GET"
probe_cors "changedetection" "${CHANGE_URL}" "/health" "GET"
probe_cors "changedetection" "${CHANGE_URL}" "/api/areas" "GET"
probe_cors "changedetection" "${CHANGE_URL}" "/api/areas" "OPTIONS"

echo "Summary: ${PASS_COUNT} passed, ${FAIL_COUNT} failed/warned"
if ((FAIL_COUNT > 0)); then
    echo "See docs/troubleshooting/frontend-workflow-errors.md for remediation." >&2
    exit 1
fi

echo "All CORS probes passed."
