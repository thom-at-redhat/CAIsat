#!/bin/bash
# ClusterFuzzLite build for decode_kserve_binary (MT-SC31-CFL).
# Assisted by: cursor, claude

set -o errexit -o nounset -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
python3 -m pip install --no-cache-dir --require-hashes -r .clusterfuzzlite/requirements-fuzz.txt

compile_python_fuzzer .clusterfuzzlite/fuzz_kserve_binary_fuzzer.py
