# Spike: Quay image tags

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                              |
| --------------- | ------------------------------------------------------------------ |
| Date            | 2026-06-29                                                         |
| Verdict         | **fail**                                                           |
| Cluster/profile | local podman (no Quay auth)                                        |
| Blocks          | Chart default image migration to `quay.io/rh-ai-quickstart/caisat` |

## Command

```bash
for TAG in model yoloobb backend detection-backend frontend; do
  podman pull "quay.io/rh-ai-quickstart/caisat:${TAG}"
done
```

## Output (snippet)

```text
Error: ... reading manifest model in quay.io/rh-ai-quickstart/caisat: unauthorized
(repeated for all five tags)
```

## Notes

Phase 1 committed sanitization **without** `chart/values.yaml` and `chart/README.md` Quay changes.

Follow-up: mirror images to a pullable registry or grant pull access, then re-run gate and commit chart defaults.

## Personal mirror (local override)

| Field   | Value                                                                                                    |
| ------- | -------------------------------------------------------------------------------------------------------- |
| Date    | 2026-06-29                                                                                               |
| Verdict | **pass** — pull after push to `quay.io/<your-quay-user>/caisat`                                          |
| Source  | Upstream image refs from pre-sanitization `chart/values.yaml` (see `git show bf67549:chart/values.yaml`) |
| Blocks  | `quay.io/rh-ai-quickstart/caisat` still unauthorized for anonymous pull                                  |

### Mirror workflow

All five chart tags (`model`, `yoloobb`, `backend`, `detection-backend`, `frontend`) were pulled from the upstream refs above, retagged, and pushed to a personal `caisat` repo on Quay.
The model image used a separate upstream repo name in history; destination repo and tag names match the chart.

Local deploy: copy `chart/values-quay-local.yaml.example` to gitignored `chart/values-quay-local.yaml`, set your Quay user, then:

```bash
helm template test ./chart -f chart/values-quay-local.yaml
```

### Verify (personal Quay)

```bash
for TAG in model yoloobb backend detection-backend frontend; do
  podman pull "quay.io/<your-quay-user>/caisat:${TAG}"
done
```

All five tags verified with `podman pull` after push (2026-06-29).
