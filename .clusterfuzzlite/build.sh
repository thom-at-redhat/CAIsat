#!/bin/bash
# ClusterFuzzLite build stub for future Phase 31 CI (local spike uses Makefile target).
# Assisted by: cursor, claude

set -o errexit -o nounset -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
python3 -m pip install --no-cache-dir atheris numpy -r backend/requirements.txt

compile_python_fuzzer .clusterfuzzlite/fuzz_kserve_binary_fuzzer.py
