# Spike: Quay image tags

<!-- Assisted by: cursor, claude -->

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
