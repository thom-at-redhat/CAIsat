# Spike: Quay image tags

<!-- Assisted by: cursor, claude -->

## Fork operator workflow (canonical)

Two separate image paths — do not confuse `make mirror-all` with a full image set.

**Workload images** (`frontend`, `backend`, `detection-backend`; optional `backend-changedetection` rebuild):

- Build/push with `scripts/build-image.sh` / `make image` to personal Quay
- Destination: `CAISAT_IMAGE_REPO` or chart default
- Auth: your Quay push credentials

**ONNX / aux mirror** (`model`, `yoloobb`, `sentinel2`, `backend-changedetection` only):

- `make mirror-all` → `scripts/mirror-image.sh`
- Auth: upstream org pull **or** fork override below
- Does **not** build or mirror workload tags

Without `rh-ai-quickstart` org access, the default upstream pull fails with `unauthorized`
(see [Upstream gate](#upstream-gate-rh-ai-quickstart)).

**Fork-only ONNX mirror** (no upstream org access — preferred for this fork):

```bash
export CAISAT_UPSTREAM_REPO=quay.io/thom_at_redhat/caisat
make mirror-all
```

**Workload build** (canonical for contributors):

```bash
# one component, or set COMPONENT=...
scripts/build-image.sh frontend
PUSH=1 scripts/build-image.sh backend
```

Do not pursue upstream org access for day-to-day fork work; use personal Quay builds and the
fork upstream override above. `mirror-image.sh` prints a fail-fast hint on `podman pull` failure
pointing here.

---

## Fork gate (contributor fork)

| Field           | Value                                                     |
| --------------- | --------------------------------------------------------- |
| Date            | 2026-06-29                                                |
| Verdict         | **pass** — fork chart defaults use public personal mirror |
| Cluster/profile | local podman (no Quay auth)                               |
| Blocks          | Phase 8+ deploy on fork (unblocked)                       |

### Command

```bash
for TAG in model yoloobb backend detection-backend frontend; do
  podman pull "quay.io/thom_at_redhat/caisat:${TAG}"
done
```

### Output (snippet)

```text
Writing manifest to image destination
(all five tags — 2026-06-29 re-verification)
```

### Notes

Fork `chart/values.yaml` defaults point to `quay.io/thom_at_redhat/caisat` (public repo; no `imagePullSecrets` required).
`chart/values-quay-local.yaml.example` remains for other Quay users who mirror to their own namespace.

---

## Upstream gate (rh-ai-quickstart)

| Field           | Value                                                     |
| --------------- | --------------------------------------------------------- |
| Date            | 2026-06-29                                                |
| Verdict         | **fail**                                                  |
| Cluster/profile | local podman (no Quay auth)                               |
| Blocks          | Upstream org chart defaults without mirror or pull access |

### Command

```bash
for TAG in model yoloobb backend detection-backend frontend; do
  podman pull "quay.io/rh-ai-quickstart/caisat:${TAG}"
done
```

### Output (snippet)

```text
Error: ... reading manifest model in quay.io/rh-ai-quickstart/caisat: unauthorized
(repeated for all five tags — re-verified 2026-06-29)
```

### Notes

Requires org access or public repo policy change on `quay.io/rh-ai-quickstart/caisat`. Upstream PR deferred.
Do not pursue org access for fork day-to-day work — use the
[fork operator workflow](#fork-operator-workflow-canonical) instead.

---

## Personal mirror workflow (reference)

| Field   | Value                                                                                                    |
| ------- | -------------------------------------------------------------------------------------------------------- |
| Date    | 2026-06-29                                                                                               |
| Verdict | **pass** — pull after push to `quay.io/<your-quay-user>/caisat`                                          |
| Source  | Upstream image refs from pre-sanitization `chart/values.yaml` (see `git show bf67549:chart/values.yaml`) |

All five chart tags (`model`, `yoloobb`, `backend`, `detection-backend`, `frontend`) were pulled from the upstream refs above, retagged, and pushed to a personal `caisat` repo on Quay.
The model image used a separate upstream repo name in history; destination repo and tag names match the chart.

For a non-fork deploy with your own mirror: copy `chart/values-quay-local.yaml.example` to gitignored `chart/values-quay-local.yaml`, set your Quay user, then:

```bash
helm template test ./chart -f chart/values-quay-local.yaml
```
