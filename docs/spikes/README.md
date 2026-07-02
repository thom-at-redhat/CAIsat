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

| Spike                    | Doc                                            | Status                                                                                                 |
| ------------------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Quay image tags          | [quay-tags.md](quay-tags.md)                   | **pass** (fork mirror); upstream **fail**                                                              |
| OpenSSF Scorecard gaps   | [scorecard-gaps.md](scorecard-gaps.md)         | **6.9** @ `d15eafe` (MT-W14b); Wave 10 assess in progress                                              |
| SwinIR ONNX shapes       | [swinir-onnx.md](swinir-onnx.md)               | **pass** — dynamic H/W; 256→1024 native 4×                                                             |
| Binary KServe v2         | [binary-kserve-v2.md](binary-kserve-v2.md)     | **fail** @ 3.4.0 + ea.2 — JSON pass / binary HTTP 500; ea.2 retest **done** on cloudtest2 (2026-07-01) |
| RHOAI GPU ServingRuntime | [gpu-servingruntime.md](gpu-servingruntime.md) | **pass** (T4) @ helm rev 14; L40S/Hopper **N/A** deferred                                              |
| YOLO11-OBB eval          | [yolo11-obb-eval.md](yolo11-obb-eval.md)       | **skipped** — Phase 17 QA sufficient                                                                   |

---

## GPU tier deferral table

Use when a GPU tier cannot be tested on schedule. Phase 15 merge requires all tiers documented **or** explicit deferral with approver.

| Tier   | Status   | Reason                          | Approver / date |
| ------ | -------- | ------------------------------- | --------------- |
| T4     | **pass** | MT-GPU cloudtest2 @ helm rev 14 | 2026-07-02      |
| L40S   | deferred | No L40S nodes on test cluster   | —               |
| Hopper | deferred | No Hopper nodes on test cluster | —               |

**Status values:** `pass` | `blocked` | `deferred`
