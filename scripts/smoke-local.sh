#!/usr/bin/env bash
# Local smoke tests for CAIsat backends.
# Profiles: health (default; CI gate via `make smoke`) and binary (encode/decode unit test via SMOKE_PROFILE=binary).
# Cluster baseline/binary/crop round-trips are manual only — not run in CI; see docs/validation/baseline-smoke.md.
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

REPO_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"
SMOKE_PROFILE="${SMOKE_PROFILE:-health}"
ENHANCE_URL="${ENHANCE_BACKEND_URL:-}"
DETECTION_URL="${DETECTION_BACKEND_URL:-}"
ENHANCE_PORT="${ENHANCE_PORT:-8000}"
DETECTION_PORT="${DETECTION_PORT:-8001}"
DUMMY_ENDPOINT="http://127.0.0.1:9/v2/models/smoke/infer"
STARTED_PIDS=()

cleanup() {
    for PID in "${STARTED_PIDS[@]}"; do
        kill "${PID}" 2>/dev/null || true
    done
}
trap cleanup EXIT

backend_python() {
    local DIR="${1}"
    local VENV="${DIR}/.venv-smoke"
    if [[ -x "${VENV}/bin/python" ]]; then
        echo "${VENV}/bin/python"
        return 0
    fi
    local PY=""
    for CANDIDATE in python3.12 python3.11 python3; do
        if command -v "${CANDIDATE}" >/dev/null 2>&1; then
            PY="${CANDIDATE}"
            break
        fi
    done
    if [[ -z "${PY}" ]]; then
        echo "FAIL: no python3 found for ${DIR}" >&2
        return 1
    fi
    echo "Creating smoke venv in ${VENV} (${PY})" >&2
    "${PY}" -m venv "${VENV}"
    "${VENV}/bin/pip" install -q -r "${DIR}/requirements.txt"
    echo "${VENV}/bin/python"
}

wait_for_health() {
    local URL="${1}"
    local NAME="${2}"
    local ATTEMPT=0
    while ((ATTEMPT < 30)); do
        ATTEMPT=$((ATTEMPT + 1))
        if curl -sf "${URL}/health" >/dev/null 2>&1; then
            echo "OK: ${NAME} ready at ${URL}"
            return 0
        fi
        sleep 1
    done
    echo "FAIL: ${NAME} not healthy at ${URL}" >&2
    return 1
}

check_health() {
    local URL="${1}"
    local NAME="${2}"
    local RESPONSE
    RESPONSE="$(curl -sf "${URL}/health")"
    if echo "${RESPONSE}" | grep -q '"status"'; then
        echo "PASS: ${NAME} /health -> ${RESPONSE}"
        return 0
    fi
    echo "FAIL: ${NAME} unexpected /health: ${RESPONSE}" >&2
    return 1
}

start_backend() {
    local DIR="${1}"
    local PORT="${2}"
    local NAME="${3}"
    local PYTHON_BIN
    PYTHON_BIN="$(backend_python "${DIR}")"
    (
        cd "${DIR}"
        export MODEL_ENDPOINT="${DUMMY_ENDPOINT}"
        exec "${PYTHON_BIN}" -m uvicorn app:app --host 127.0.0.1 --port "${PORT}"
    ) &
    STARTED_PIDS+=("$!")
    echo "Started ${NAME} on 127.0.0.1:${PORT} (pid $!)"
}

health_profile() {
    if [[ -z "${ENHANCE_URL}" ]]; then
        start_backend "${REPO_ROOT}/backend" "${ENHANCE_PORT}" "enhancement backend"
        ENHANCE_URL="http://127.0.0.1:${ENHANCE_PORT}"
        wait_for_health "${ENHANCE_URL}" "enhancement backend"
    fi
    if [[ -z "${DETECTION_URL}" ]]; then
        start_backend "${REPO_ROOT}/backend-detection" "${DETECTION_PORT}" "detection backend"
        DETECTION_URL="http://127.0.0.1:${DETECTION_PORT}"
        wait_for_health "${DETECTION_URL}" "detection backend"
    fi
    check_health "${ENHANCE_URL}" "enhancement backend"
    check_health "${DETECTION_URL}" "detection backend"
}

binary_profile() {
    health_profile
    local PYTHON_BIN
    PYTHON_BIN="$(backend_python "${REPO_ROOT}/backend")"
    echo "Running KServe v2 encode/decode round-trip (local, no predictor)..."
    (
        cd "${REPO_ROOT}"
        "${PYTHON_BIN}" - <<'PY'
import sys
sys.path.insert(0, "backend")
import numpy as np
from kserve_v2 import encode_kserve_binary, encode_kserve_json, decode_kserve_json

rng = np.random.default_rng(42)
tensor = rng.random((1, 3, 256, 256), dtype=np.float32)
headers, body = encode_kserve_binary("input", tensor, "output")
header_len = int(headers["Inference-Header-Content-Length"])
assert header_len > 0
assert len(body) == header_len + tensor.nbytes
json_payload = encode_kserve_json("input", tensor)
roundtrip = decode_kserve_json({"outputs": [{"name": "output", "shape": list(tensor.shape), "data": tensor.flatten().tolist()}]})
assert np.allclose(roundtrip, tensor), "JSON round-trip mismatch"
print("PASS: encode_kserve_binary produces valid octet-stream body")
print("PASS: encode/decode_kserve_json round-trip within tolerance")
PY
    )
}

case "${SMOKE_PROFILE}" in
    health)
        health_profile
        ;;
    binary)
        binary_profile
        ;;
    *)
        echo "Unknown SMOKE_PROFILE: ${SMOKE_PROFILE}" >&2
        exit 1
        ;;
esac

echo "Smoke profile '${SMOKE_PROFILE}' passed."
