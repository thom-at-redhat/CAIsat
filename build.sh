#!/bin/bash
# ClusterFuzzLite build entrypoint (delegates to .clusterfuzzlite/).
# Assisted by: cursor, claude

set -o errexit -o nounset -o pipefail

ROOT_DIR="$(cd "$(dirname "${0}")" && pwd)"
exec bash "${ROOT_DIR}/.clusterfuzzlite/build.sh"
