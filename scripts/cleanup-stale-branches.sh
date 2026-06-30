#!/usr/bin/env bash
# Assisted by: cursor, claude
# Idempotent stale-branch cleanup for CAIsat fork (origin). Dry-run by default; pass --execute to delete.
set -o errexit -o nounset -o pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

EXECUTE=0
if [[ "${1:-}" == "--execute" ]]; then
  EXECUTE=1
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--execute]" >&2
  exit 1
fi

# Local branches we never delete.
KEEP_LOCAL=(
  main
  chore/devops-scripts
)

# origin/* remotes we never delete (open PR + in-flight worktree branch).
KEEP_REMOTE=(
  main
  chore/devops-scripts
)

is_kept_local() {
  local B="$1"
  local K
  for K in "${KEEP_LOCAL[@]}"; do
    [[ "${B}" == "${K}" ]] && return 0
  done
  return 1
}

is_kept_remote() {
  local B="$1"
  local K
  for K in "${KEEP_REMOTE[@]}"; do
    [[ "${B}" == "${K}" ]] && return 0
  done
  return 1
}

git fetch origin

ORIGIN_MAIN="$(git rev-parse origin/main)"
MERGED_PR_HEADS="$(
  gh pr list  --state merged --limit 200 --json headRefName \
    | jq -r '.[].headRefName' | sort -u
)"

branch_merged() {
  local REF="$1"
  if git rev-parse --verify "${REF}" >/dev/null 2>&1; then
    if git merge-base --is-ancestor "$(git rev-parse "${REF}")" "${ORIGIN_MAIN}" 2>/dev/null; then
      return 0
    fi
  fi
  local SHORT="${REF#refs/heads/}"
  SHORT="${SHORT#origin/}"
  echo "${MERGED_PR_HEADS}" | grep -qx "${SHORT}"
}

echo "=== KEEP local ==="
printf '  %s\n' "${KEEP_LOCAL[@]}"
echo "=== KEEP origin ==="
printf '  %s\n' "${KEEP_REMOTE[@]}"

echo ""
echo "=== Local branches to delete ==="
LOCAL_DELETE=()
while IFS= read -r B; do
  is_kept_local "${B}" && continue
  GONE=0
  git branch -vv | grep -F " ${B} " | grep -q ': gone]' && GONE=1
  if branch_merged "${B}" || [[ ${GONE} -eq 1 ]]; then
    echo "  ${B}"
    LOCAL_DELETE+=("${B}")
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)

echo ""
echo "=== origin/* remotes to delete ==="
REMOTE_DELETE=()
while IFS= read -r REF; do
  [[ "${REF}" == "origin" || "${REF}" == "origin/HEAD" ]] && continue
  B="${REF#origin/}"
  is_kept_remote "${B}" && continue
  if branch_merged "origin/${B}"; then
    OPEN_HEAD="$(
      gh pr list  --state open --json headRefName \
        | jq -r --arg b "${B}" '.[] | select(.headRefName == $b) | .headRefName'
    )"
    if [[ -n "${OPEN_HEAD}" ]]; then
      echo "  SKIP (open PR): ${B}"
      continue
    fi
    echo "  ${B}"
    REMOTE_DELETE+=("${B}")
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/remotes/origin/)

if [[ ${EXECUTE} -eq 0 ]]; then
  echo ""
  echo "Dry-run only. Re-run with --execute to delete branches and run git worktree prune."
  exit 0
fi

for B in "${LOCAL_DELETE[@]}"; do
  git branch -d "${B}" 2>/dev/null || git branch -D "${B}"
done

for B in "${REMOTE_DELETE[@]}"; do
  git push origin --delete "${B}"
done

git worktree prune
git remote prune origin

echo ""
echo "=== Remaining local branches ==="
git branch -vv
echo ""
echo "=== Remaining origin remotes ==="
git branch -r | grep ' origin/' || true
