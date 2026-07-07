#!/usr/bin/env bash
# Pull, retag, and push pre-built CAIsat OCI images (model ONNX bundles and mirrored workloads).
# Usage: scripts/mirror-image.sh [model|yoloobb|sentinel2|backend-changedetection|all]
# Env: CAISAT_UPSTREAM_REPO (default quay.io/rh-ai-quickstart/caisat),
#      CAISAT_IMAGE_REPO (defaults to chart/values.yaml frontend.image.repository),
#      CONTAINER_CMD=podman
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

mirror_tag() {
    local IMAGE_TAG="${1}"
    local UPSTREAM_REPO="${2}"
    local DEST_REPO="${3}"
    local SOURCE_IMAGE="${UPSTREAM_REPO}:${IMAGE_TAG}"
    local DEST_IMAGE="${DEST_REPO}:${IMAGE_TAG}"

    printf 'Mirroring %s -> %s\n' "${SOURCE_IMAGE}" "${DEST_IMAGE}"
    "${CONTAINER_CMD}" pull "${SOURCE_IMAGE}"
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
