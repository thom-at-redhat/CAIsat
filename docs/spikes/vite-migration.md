# Spike: CRA → Vite migration

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                                       |
| --------------- | --------------------------------------------------------------------------- |
| Date            | 2026-07-02                                                                  |
| Verdict         | **defer** — CRA build stable; migration cost outweighs near-term gain       |
| Cluster/profile | N/A (build-time spike only)                                                 |
| Follow-up       | MT-VITE-MIGRATE cancelled; revisit when CRA toolchain EOL or overrides fail |

**MT-ID:** MT-VITE-SPIKE | **Tip SHA:** `9f66915`

---

## Current stack

| Component          | Version / mechanism                                | Notes                                                                                |
| ------------------ | -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Build tool         | `react-scripts` 5.0.1 (CRA)                        | Webpack 5 under the hood                                                             |
| React              | 19.2.7                                             | Build passes post Phase 9                                                            |
| react-leaflet      | 5.0.0                                              | Map view; cluster UX unvalidated                                                     |
| three              | 0.185.0                                            | Globe view; cluster UX unvalidated                                                   |
| Output dir         | `build/`                                           | [`frontend/Containerfile`](../../frontend/Containerfile) serves via `serve -s build` |
| Dev proxy          | `"proxy": "http://localhost:8080"` in package.json | CRA dev-server proxy                                                                 |
| Env vars           | None (`REACT_APP_*` not used)                      | No rename to `VITE_*` required today                                                 |
| Lint in pre-commit | **excluded** — JSHint/Prettier skip `frontend/`    | CRA ESLint via `react-app` extend only                                               |

---

## Migration scope (if Proceed)

### Required changes

1. **Scaffold:** `vite.config.js` with `@vitejs/plugin-react`; `index.html` at project root (move from `public/`).
2. **Entry:** `src/index.js` — verify React 19 `createRoot` (already used).
3. **Proxy:** Replace package.json `proxy` with Vite `server.proxy` → backend `:8080`.
4. **Build output:** `dist/` instead of `build/` — update [`frontend/Containerfile`](../../frontend/Containerfile) `CMD` to `serve -s dist`.
5. **Scripts:** `vite`, `vite build`, `vitest` (optional) replacing `react-scripts` commands.
6. **ESLint:** Flat config (`eslint.config.js`) — enables removing `frontend/` exclude from [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml).
7. **Static assets:** `public/` → Vite `publicDir`; verify `leaflet` CSS import path.
8. **react-leaflet / three:** No known blockers; same imports; verify HMR and production chunking.
9. **npm overrides:** Drop `react-scripts` transitive CVE overrides after removing CRA; re-run `npm audit` and document any new findings in [`scorecard-gaps.md`](scorecard-gaps.md).
10. **Cluster smoke:** Map + globe UX per [`baseline-smoke.md`](../validation/baseline-smoke.md); Quay `:frontend` image push.

### Risk areas

| Area              | Risk   | Mitigation                                                      |
| ----------------- | ------ | --------------------------------------------------------------- |
| leaflet-image     | Medium | Test canvas export in Vite build (no Node polyfills by default) |
| Three.js bundling | Low    | Vite handles ESM; verify tree-shaking                           |
| Jest → Vitest     | Low    | CRA tests minimal; optional migration                           |
| Container image   | Low    | Single-line `dist/` path change                                 |

---

## Cost-benefit

| Cost                                         | Benefit                                                   |
| -------------------------------------------- | --------------------------------------------------------- |
| ~1–2 days migration + cluster smoke          | Faster dev HMR; modern ESLint in pre-commit               |
| Remove 9 `npm overrides` for CRA transitives | Cleaner dependency tree                                   |
| Re-validate map/globe on cluster             | Scorecard unchanged (CRA CVEs already mitigated)          |
| New vite + plugin deps                       | Future-proof when `react-scripts` stops receiving patches |

**Assessment:** CVE surface already managed via Phase 9 `overrides`; `npm audit` reports 0. CRA build passes on React 19.

Pre-commit excludes frontend lint. Migration is DX-only — no blocking gap at `9f66915`.

---

## Verdict matrix

| Criterion                         | Result                                 |
| --------------------------------- | -------------------------------------- |
| Blocking CVE in CRA toolchain     | **No** (overrides)                     |
| Build failure on current tip      | **No**                                 |
| Operator request for Vite         | **No**                                 |
| Cluster map/globe regression risk | **Medium** (unvalidated post React 19) |

**Verdict:** **defer** — MT-VITE-MIGRATE **cancelled**.

Revisit when: (a) `react-scripts` overrides fail `npm audit`, (b) CRA blocks a dependency upgrade, or (c) operator schedules map/globe validation with migration.

---

## Command (baseline — CRA build)

```bash
cd frontend
npm ci
npm run build
# Output: build/static/js/*.js, build/index.html
```

## Output (snippet)

```text
# npm run build @ 9f66915 (react-scripts 5.0.1, React 19.2.7)
Creating an optimized production build...
Compiled successfully.
File sizes after gzip:
  ~250 KB main bundle (three + leaflet + recharts)
```

## Notes

Spike complete. No `vite.config.js` or Containerfile changes in this PR. If Proceed later, use branch `feat/vite-migrate` per plan isolation rules.
