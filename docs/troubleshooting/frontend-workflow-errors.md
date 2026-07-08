# Troubleshooting Frontend Workflow Errors

<!-- Assisted by: cursor, claude -->

Guidance for diagnosing user-facing failures in the CAIsat web UI: Monitored Areas, image enhancement, and cross-origin API calls.

Symptoms often look like network or CORS problems but can stem from backend configuration, incomplete data, or frontend assumptions about API shape.

---

## Architecture reminder

The React frontend is served from one OpenShift Route. It calls **three separate backend Routes** derived from the frontend hostname:

| UI feature                   | Backend component        | Typical paths                                    |
| ---------------------------- | ------------------------ | ------------------------------------------------ |
| Enhance, capabilities, stats | Enhancement backend      | `/api/enhance`, `/api/capabilities`, `/health`   |
| Object detection             | Detection backend        | `/api/detect`, `/health`                         |
| Monitored Areas              | Change-detection backend | `/api/areas`, `/api/areas/{id}/stats`, `/health` |

Each call is **cross-origin** (different subdomain). Browsers enforce CORS on every request.

A user who can load the main page may still fail on one backend if that Route is unreachable, misconfigured, or returns invalid CORS headers.

---

## Symptom index

| User-visible symptom                                 | Common causes (check in order)                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| “Failed to load monitored areas…”                    | Change-detection Route down; CORS failure; proxy blocking backend subdomain; DNS/TLS error |
| List loads, detail blank / `TypeError` on `.toFixed` | Stats JSON missing optional fields; frontend not guarding missing fields                   |
| Enhance finishes but UI shows original crop          | POST failed; job poll timeout; client error; dismissed error banner                        |
| “CORS request failed”                                | Invalid `Allow-Origin` with credentials; missing preflight headers; proxy stripping CORS   |
| OPTIONS succeeds, POST fails                         | Not preflight — inspect POST status, body, and response size                               |

---

## Step 1 — Separate network from application errors

Open browser DevTools → **Network** (preserve log enabled). Reproduce the failure and classify the failing request:

1. **No request sent** — likely a JavaScript error earlier (check **Console**).
2. **Request red / (failed)** — DNS, TLS, timeout, or connection reset; test with `curl` from the same client network.
3. **HTTP 4xx/5xx** — backend or ingress issue; read response body.
4. **HTTP 200 but UI still broken** — response shape or client parsing bug; compare JSON to what the UI expects.

Record: URL, method, status, and whether the failure is on **OPTIONS** (preflight) or the actual **GET/POST**.

---

## Step 2 — Verify CORS (cross-origin APIs)

CORS failures are reported in the browser Console or Network tab, not always as a clear HTTP status on the application request.

### Preflight (OPTIONS)

Enhancement `POST` with `multipart/form-data` triggers a preflight. From a shell (replace hostnames with your Routes):

```bash
curl -i 'https://<enhance-backend-route>/api/enhance' \
  -X OPTIONS \
  -H 'Origin: https://<frontend-route>' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type'
```

Expect `200` with:

- `access-control-allow-origin: https://<frontend-route>` (specific origin, not `*` when credentials are enabled)
- `access-control-allow-methods` including `POST`
- `access-control-allow-headers: content-type` when the browser requests it

A successful OPTIONS does **not** guarantee the POST will succeed — always check the POST separately.

### Actual response (GET/POST)

```bash
curl -i 'https://<changedetection-backend-route>/api/areas' \
  -H 'Origin: https://<frontend-route>'
```

**Invalid pattern (browsers block):** `access-control-allow-origin: *` together with `access-control-allow-credentials: true`.

**Valid pattern:** echo the request `Origin` (or an explicit allow-list) with `vary: Origin`.

Compare enhancement and change-detection backends — they must both return valid CORS on **GET** responses, not only on OPTIONS.

---

## Step 3 — Monitored Areas

### List view fails

1. Confirm change-detection pod is Ready: `oc get pods -l app.kubernetes.io/component=backend-changedetection -n <namespace>`
2. `curl -sS https://<changedetection-backend-route>/health`
3. `curl -sS https://<changedetection-backend-route>/api/areas` — expect JSON with an `areas` array
4. If `curl` works from an operator network but not the user browser, suspect CORS or firewall rules on `*-backend-*` hostnames

### List works, detail view crashes

The UI detail panel expects fields that the **analysis pipeline** produces (`maxChange`, `stdChange`, `timeSeries`, …).

**Storage seed** jobs write a minimal stats object (`location`, `avgChange`, `classification`, `dateRange`, `imageCount` only).

1. Fetch stats: `curl -sS https://<changedetection-backend-route>/api/areas/<location>/stats | jq 'keys'`
2. If `maxChange` or `timeSeries` are absent, the list should still work; the detail view must tolerate missing fields (show `N/A` / empty state) rather than calling `.toFixed()` on `undefined`
3. To populate full stats, run the change-detection analysis pipeline and confirm `metadata/<location>-stats.json` in object storage

---

## Step 4 — Enhance appears unchanged

Work through this sequence:

1. **Capabilities loaded?** Network tab should show `GET /api/capabilities` → 200. If it fails, the UI may fall back to defaults and choose sync vs async unpredictably.
2. **Which path?** Default 256×256 often uses sync `POST /api/enhance`; larger crops use `POST /api/enhance/jobs` plus polling.
3. **POST outcome** — status 200/202, response includes `preview` and `media_type` (sync or completed job).
4. **Timeouts** — large crops and GPU cold-start can exceed load-balancer or client timeouts; check for `ERR_NETWORK` or 504 in Network tab.
5. **Visual similarity** — a successful enhance can look subtle on uniform terrain; verify response `width`/`height` are larger than the crop and `preview` payload is non-empty.

---

## Step 5 — Backend health matrix

Quick checks from a machine with cluster or Route access:

```bash
FRONTEND=https://<frontend-route>
ENHANCE=https://<enhance-backend-route>
DETECT=https://<detection-backend-route>
CHANGE=https://<changedetection-backend-route>

for URL in "$ENHANCE" "$DETECT" "$CHANGE"; do
  echo "== $URL/health =="
  curl -sS -o /dev/null -w '%{http_code}\n' "$URL/health"
done
```

All should return `200`. If one backend fails while others pass, focus on that Deployment, Route, and image tag — not the frontend bundle.

---

## Step 6 — Cluster vs git drift

Images may be rolled out manually (`podman push` + `oc rollout restart`) before changes land on `main`. If production behavior differs from a fresh Helm install:

1. Compare running image digests: `oc get pod -o jsonpath='{..imageID}'` for frontend and change-detection workloads
2. Compare chart tag in `values.yaml` with the digest on the cluster
3. Confirm the frontend bundle and backend CORS fix are in the same release artifact set

---

## Resolution checklist

| Issue                            | Fix direction                                                                          |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| Invalid CORS on change-detection | Ensure backend echoes frontend `Origin`; avoid `*` with `allow_credentials: true`      |
| Detail view `TypeError` on stats | Guard optional fields in `MonitoredAreas.js`; empty state when `timeSeries` is missing |
| Backend subdomain blocked        | Network/proxy policy, or same-origin reverse proxy (not implemented by default)        |
| Incomplete monitored-area charts | Run analysis pipeline; seed data alone is insufficient for time series                 |
| Enhance timeout on large crops   | Use default crop size; confirm async job path and Route idle timeout annotations       |

---

## Related docs

- [Baseline and smoke validation](../validation/baseline-smoke.md) — automated health and enhance/detect checks
- [Capabilities API spec](../specs/capabilities-api.md) — crop sizes and async routing inputs
