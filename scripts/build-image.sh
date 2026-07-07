#!/usr/bin/env bash
# Build (and optionally push) a CAIsat workload image to Quay.
# Usage: scripts/build-image.sh [frontend|backend|detection-backend]
# Env: CAISAT_IMAGE_REPO (defaults to chart/values.yaml frontend.image.repository), PUSH=1, CONTAINER_CMD=podman
# Assisted by: cursor, claude
set -o errexit -o nounset -o pipefail

REPO_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"
# shellcheck source=scripts/resolve-image-repo.sh
source "${REPO_ROOT}/scripts/resolve-image-repo.sh"
COMPONENT="${1:-${COMPONENT:-frontend}}"
PUSH="${PUSH:-0}"
CONTAINER_CMD="${CONTAINER_CMD:-podman}"

if ! command -v "${CONTAINER_CMD}" >/dev/null 2>&1; then
    printf 'build-image: %s is required (https://podman.io/)\n' "${CONTAINER_CMD}" >&2
    exit 1
fi

IMAGE_REPO="$(caisat_resolve_image_repo build-image "${REPO_ROOT}/chart/values.yaml")"

case "${COMPONENT}" in
    frontend)
        BUILD_CONTEXT="${REPO_ROOT}/frontend"
        IMAGE_TAG="frontend"
        ;;
    backend)
        BUILD_CONTEXT="${REPO_ROOT}/backend"
        IMAGE_TAG="backend"
        ;;
    detection-backend)
        BUILD_CONTEXT="${REPO_ROOT}/backend-detection"
        IMAGE_TAG="detection-backend"
        ;;
    *)
        printf 'build-image: unknown component %q (use frontend, backend, or detection-backend)\n' "${COMPONENT}" >&2
        exit 1
        ;;
esac

FULL_IMAGE="${IMAGE_REPO}:${IMAGE_TAG}"
CONTAINERFILE="${BUILD_CONTEXT}/Containerfile"

printf 'Building %s from %s\n' "${FULL_IMAGE}" "${CONTAINERFILE}"
"${CONTAINER_CMD}" build -f "${CONTAINERFILE}" -t "${FULL_IMAGE}" "${BUILD_CONTEXT}"

if [[ "${PUSH}" == "1" ]]; then
    printf 'Pushing %s\n' "${FULL_IMAGE}"
    "${CONTAINER_CMD}" push "${FULL_IMAGE}"
else
    printf 'Skipping push (set PUSH=1 or use make push-image)\n'
fi
