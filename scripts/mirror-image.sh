#!/usr/bin/env bash
# Pull, retag, and push pre-built CAIsat ONNX/aux OCI tags (not workload builds).
# Usage: scripts/mirror-image.sh [model|yoloobb|sentinel2|backend-changedetection|all]
# Env: CAISAT_UPSTREAM_REPO (default quay.io/rh-ai-quickstart/caisat),
#      CAISAT_IMAGE_REPO (defaults to chart/values.yaml frontend.image.repository),
#      CONTAINER_CMD=podman
# Upstream auth failures: docs/spikes/quay-tags.md (set CAISAT_UPSTREAM_REPO to fork Quay).
# Workloads: scripts/build-image.sh
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

REPO_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"
# shellcheck source=scripts/resolve-image-repo.sh
source "${REPO_ROOT}/scripts/resolve-image-repo.sh"

COMPONENT="${1:-${COMPONENT:-model}}"
CONTAINER_CMD="${CONTAINER_CMD:-podman}"

MIRROR_TAGS_ALL=(model yoloobb sentinel2 backend-changedetection)

if ! command -v "${CONTAINER_CMD}" >/dev/null 2>&1; then
    printf 'mirror-image: %s is required (https://podman.io/)\n' "${CONTAINER_CMD}" >&2
    exit 1
fi

print_upstream_auth_hint() {
    local SOURCE_IMAGE="${1}"
    printf 'mirror-image: pull failed for %s (often unauthorized without rh-ai-quickstart org access).\n' "${SOURCE_IMAGE}" >&2
    printf 'mirror-image: ONNX/aux tags only; workloads use scripts/build-image.sh.\n' >&2
    printf 'mirror-image: fork override: set CAISAT_UPSTREAM_REPO to your public fork Quay (see docs/spikes/quay-tags.md).\n' >&2
}

mirror_tag() {
    local IMAGE_TAG="${1}"
    local UPSTREAM_REPO="${2}"
    local DEST_REPO="${3}"
    local SOURCE_IMAGE="${UPSTREAM_REPO}:${IMAGE_TAG}"
    local DEST_IMAGE="${DEST_REPO}:${IMAGE_TAG}"

    printf 'Mirroring %s -> %s\n' "${SOURCE_IMAGE}" "${DEST_IMAGE}"
    if ! "${CONTAINER_CMD}" pull "${SOURCE_IMAGE}"; then
        print_upstream_auth_hint "${SOURCE_IMAGE}"
        exit 1
    fi
    "${CONTAINER_CMD}" tag "${SOURCE_IMAGE}" "${DEST_IMAGE}"
    "${CONTAINER_CMD}" push "${DEST_IMAGE}"
}

DEST_REPO="$(caisat_resolve_image_repo mirror-image "${REPO_ROOT}/chart/values.yaml")"
UPSTREAM_REPO="${CAISAT_UPSTREAM_REPO:-quay.io/rh-ai-quickstart/caisat}"

case "${COMPONENT}" in
    model|yoloobb|sentinel2|backend-changedetection)
        mirror_tag "${COMPONENT}" "${UPSTREAM_REPO}" "${DEST_REPO}"
        ;;
    all)
        for IMAGE_TAG in "${MIRROR_TAGS_ALL[@]}"; do
            mirror_tag "${IMAGE_TAG}" "${UPSTREAM_REPO}" "${DEST_REPO}"
        done
        ;;
    *)
        printf 'mirror-image: unknown component %q (use model, yoloobb, sentinel2, backend-changedetection, or all)\n' "${COMPONENT}" >&2
        exit 1
        ;;
esac
