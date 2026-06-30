# CAIsat Spikes

<!-- Assisted by: cursor, claude -->

Spike artifacts record pass/fail evidence before dependent phases merge. Use the template below for each spike doc.

---

## Pass/fail template

```markdown
# Spike: <title>

| Field           | Value                   |
| --------------- | ----------------------- |
| Date            | YYYY-MM-DD              |
| Verdict         | pass \| fail \| blocked |
| Cluster/profile | (if applicable)         |
| Blocks          | Phase N                 |

## Command

\`\`\`bash

# exact command(s)

\`\`\`

## Output (snippet)

\`\`\`

# relevant stdout/stderr

\`\`\`

## Notes

Decision and follow-up.
```

---

## Spike index

| Spike                    | Doc                                    | Status                                     |
| ------------------------ | -------------------------------------- | ------------------------------------------ |
| Quay image tags          | [quay-tags.md](quay-tags.md)           | **pass** (fork mirror); upstream **fail**  |
| OpenSSF Scorecard gaps   | [scorecard-gaps.md](scorecard-gaps.md) | baseline 6.0 @ `0e4281e`                   |
| SwinIR ONNX shapes       | [swinir-onnx.md](swinir-onnx.md)       | **pass** — dynamic H/W; 256→1024 native 4× |
| Binary KServe v2         | binary-kserve-v2.md                    | not started                                |
| RHOAI GPU ServingRuntime | gpu-servingruntime.md                  | not started                                |

---

## GPU tier deferral table

Use when a GPU tier cannot be tested on schedule. Phase 15 merge requires all tiers documented **or** explicit deferral with approver.

| Tier   | Status   | Reason | Approver / date |
| ------ | -------- | ------ | --------------- |
| T4     | deferred | —      | —               |
| L40S   | deferred | —      | —               |
| Hopper | deferred | —      | —               |

**Status values:** `pass` | `blocked` | `deferred`
