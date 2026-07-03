# Spike: Atheris fuzz harness for `decode_kserve_binary`

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                                 |
| --------------- | --------------------------------------------------------------------- |
| Date            | 2026-07-03                                                            |
| Verdict         | **pass** — local harness runs; one uncaught `TypeError` found         |
| Cluster/profile | N/A (local-only spike; no ClusterFuzzLite CI workflow)                |
| Follow-up       | Harden `decode_kserve_binary` / `kserve_infer` for non-object headers |

**MT-ID:** MT-SC31-FUZZING-spike | **Tip SHA:** `d4ada24`

---

## Target

| Item         | Detail                                                                |
| ------------ | --------------------------------------------------------------------- |
| Function     | `decode_kserve_binary(body: bytes, header_length: int) -> np.ndarray` |
| Primary path | `backend/kserve_v2.py:66`                                             |
| Mirror       | `backend-detection/kserve_v2.py:64` (byte-identical)                  |
| Spec / tests | `docs/specs/kserve-v2-tensors.md`, `tests/test_kserve_v2.py`          |

---

## Harness

| Item       | Path                                                                           |
| ---------- | ------------------------------------------------------------------------------ |
| Fuzzer     | `.clusterfuzzlite/fuzz_kserve_binary_fuzzer.py`                                |
| Build stub | `.clusterfuzzlite/build.sh`, `.clusterfuzzlite/Dockerfile` (not wired to CI)   |
| Makefile   | `make fuzz-kserve-binary` (~45 s default; override `FUZZ_TIME` or `FUZZ_RUNS`) |

Import uses the same `importlib` pattern as `tests/conftest.py` (`_import_from_backend`), loading `backend/kserve_v2.py` only.

**Expected exceptions (swallowed in harness):** `json.JSONDecodeError`, `KeyError`, `ValueError`.

**Unexpected exceptions:** reported as libFuzzer crashes (findings).

---

## Local run

```bash
# Project venv recommended; Makefile installs deps on demand.
pip install atheris numpy -r backend/requirements.txt   # aiohttp needed for kserve_v2 import

make fuzz-kserve-binary
# or fixed run count:
FUZZ_RUNS=10000 make fuzz-kserve-binary
# or time budget:
FUZZ_TIME=60 make fuzz-kserve-binary
```

Direct invocation:

```bash
python .clusterfuzzlite/fuzz_kserve_binary_fuzzer.py -runs=10000
python .clusterfuzzlite/fuzz_kserve_binary_fuzzer.py -max_total_time=45
```

---

## Findings

| Run                               | Crashes | Notes                                             |
| --------------------------------- | ------- | ------------------------------------------------- |
| 10 000 iterations (`-runs=10000`) | **1**   | Stopped on first uncaught exception (~2 execs in) |

### Finding 1: `TypeError` on non-object JSON header

When the header slice parses to a JSON value that is not an object (e.g. bare integer `0`), `decode_kserve_binary` raises `TypeError: 'int' object is not subscriptable` at `meta["outputs"][0]`.

**Minimal repro:**

```python
decode_kserve_binary(body=b"0", header_length=1)
```

**Atheris crash artifact:** input bytes `0x30, 0x29, 0x0a` (Base64: `MCkK`) with `header_length` derived from `FuzzedDataProvider`.

**Production impact:** `kserve_infer` catches `(json.JSONDecodeError, KeyError, ValueError)` but not `TypeError`, so a malformed binary response header could propagate instead of falling back to JSON.

**Recommendation:** Follow-up PR — validate `isinstance(meta, dict)` and raise `ValueError`, or extend the `kserve_infer` except tuple to include `TypeError` / `IndexError`.

Not fixed in this spike (document-only).

---

## Verdict matrix

| Criterion                                        | Result                                |
| ------------------------------------------------ | ------------------------------------- |
| Atheris + `FuzzedDataProvider` runs locally      | **Yes**                               |
| `decode_kserve_binary` imported via backend path | **Yes**                               |
| Crashes / unexpected exceptions in 10 k runs     | **1** (`TypeError`)                   |
| ClusterFuzzLite CI workflow added                | **No** (deferred per scope)           |
| `make check` on branch                           | **pass** (pre-commit + helm + pytest) |

---

## Recommendation

**proceed_ci** — Harness is viable for ClusterFuzzLite in a follow-up phase: wire `.clusterfuzzlite/build.sh` + Dockerfile into GitHub Actions, seed corpus from round-trip tests.

Land `TypeError` hardening in a separate fix PR.
