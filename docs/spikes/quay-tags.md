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

Phase 1A committed sanitization **without** `chart/values.yaml` and `chart/README.md` Quay changes.

Follow-up: mirror images to a pullable registry or grant pull access, then re-run gate and commit chart defaults.
