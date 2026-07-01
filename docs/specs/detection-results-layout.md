# Detection Results Layout (Responsive UI)

<!-- Assisted by: cursor, claude -->

| Field      | Value                                                  |
| ---------- | ------------------------------------------------------ |
| Status     | accepted                                               |
| Spec ID    | DRL-001                                                |
| Tests      | _(manual — Playwright MT-R3a; no pytest yet)_          |
| Validation | `baseline-smoke.md` L145–157                           |
| Source     | `frontend/src/App.js`, `frontend/src/App.css` L653–730 |

## Overview

After **Enhance Selected Area**, the user may click **Detect Objects**. The results row shows three panels left-to-right: **Original** → **Enhanced** → **Detected Objects**.
Oriented bounding boxes render on the **Detected Objects** image only (third panel). Layout adapts at a CSS breakpoint and under browser zoom (MT-1b / MT-R3a).

Operator sign-off for 150% layout **pass** @ MT-R3a (2026-07-01) — see `baseline-smoke.md` L157+.

## Requirements

### DRL-001-R1: Three-panel flow

- Panel order: Original (crop) → Enhanced (4×) → Detected Objects (when detection completes)
- Arrows (`→`) separate expanded panels; collapsed panels show `▶` affordance
- Scroll hint appears after detection when horizontal scroll is needed on wide viewports
- Bounding boxes drawn only on **Detected Objects** panel image, not on Original or Enhanced

### DRL-001-R2: Wide viewport (100% zoom, width > 1400px)

- `.results-container` uses `display: flex`, horizontal row (`flex-direction: row`)
- Panels are `flex-shrink: 0`; container allows `overflow-x: auto` with scroll-snap
- Each panel image: `width: min(512px, 100%)`, `max-width: min(512px, calc(100vw - 320px))`
- **Pass:** all three panels reachable; boxes visible on panel 3 when `detections.count > 0`

### DRL-001-R3: Narrow viewport / breakpoint (≤ 1400px)

- CSS `@media (max-width: 1400px)` sets `.results-container { flex-direction: column }`
- Panels stack vertically; horizontal scroll disabled (`scroll-snap-type: none`)
- Panel width: `max-width: min(512px, calc(100vw - 80px))`
- Down arrows replace horizontal flow for stacked layout

### DRL-001-R4: 150% browser zoom (accessibility)

- At **150% browser zoom** (or `deviceScaleFactor: 1.5` in Playwright at 1600px width), effective viewport shrinks; panels **must** stack vertically per DRL-001-R3
- Third panel fully visible without clipped content off-screen
- Viewport-only resize ≤1067px is a **supplementary** CSS check, not sole pass criterion (`baseline-smoke.md` L151)
- **Pass (MT-R3a 2026-07-01):** operator retest complete — see `baseline-smoke.md` L157+

### DRL-001-R5: Box alignment

- When `detections.count > 0`, boxes align with objects in the enhanced crop on panel 3
- When `detections.count === 0` after harbor **and** airport tiles, layout may **pass** but box-alignment row stays **N/A** (not pass)

## Acceptance criteria

- [x] 100% wide layout **pass** @ 1600px — MT-R3a 2026-07-01 (1 detection with box overlay)
- [x] 150% vertical stack **pass** — MT-R3a 2026-07-01 @ 1067px effective width
- [x] Box alignment with non-zero detections — 1 detection on default map tile (MT-R3a)
- [x] Playwright artifacts under `docs/validation/artifacts/mt-r3a-20260701/`
