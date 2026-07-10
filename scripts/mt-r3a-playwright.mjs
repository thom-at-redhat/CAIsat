// Assisted by: cursor, claude
// MT-R3a Playwright validation — 100% and 150% detection results layout.

import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const IN_CI = process.env.GITHUB_ACTIONS === 'true';

const FRONTEND_URL = process.env.CAISAT_FRONTEND_URL ?? (IN_CI ? 'http://localhost:3000' : undefined);
if (!FRONTEND_URL) {
  throw new Error('Set CAISAT_FRONTEND_URL to the cluster Route URL (not committed to the repo).');
}
const ARTIFACT_DIR =
  process.env.MT_R3A_ARTIFACT_DIR ??
  (IN_CI ? path.join(process.env.RUNNER_TEMP, 'e2e-artifacts') : path.resolve('docs/validation/artifacts/mt-r3a-20260701'));
const ENHANCE_TIMEOUT_MS = 420_000;
const DETECT_TIMEOUT_MS = 180_000;

fs.mkdirSync(ARTIFACT_DIR, { recursive: true });

const results = [];

function log(line) {
  const entry = `${new Date().toISOString()} ${line}`;
  results.push(entry);
  console.log(entry);
}

async function waitForMapReady(page) {
  await page.waitForSelector('.leaflet-tile-loaded', { timeout: 60_000 });
  await page.waitForTimeout(3000);
}

async function layoutMetrics(page) {
  await page.evaluate(() => {
    const detected = document.querySelector('img[alt="Detected"]');
    detected?.scrollIntoView({ block: 'center', behavior: 'instant' });
  });
  await page.waitForTimeout(300);
  return page.evaluate(() => {
    const container = document.querySelector('.results-container');
    if (!container) {
      return { error: 'missing .results-container' };
    }
    const style = getComputedStyle(container);
    const panels = [...container.querySelectorAll('.result-panel')].map((panel) => panel.querySelector('h4')?.textContent?.trim() ?? '');
    const detectedImg = container.querySelector('img[alt="Detected"]');
    const rect = detectedImg?.getBoundingClientRect();
    const viewport = { width: window.innerWidth, height: window.innerHeight };
    const thirdVisible = rect
      ? rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.bottom <= viewport.height + 2
      : false;
    return {
      flexDirection: style.flexDirection,
      panelCount: panels.length,
      panels,
      zoom: document.body.style.zoom || '1',
      viewport,
      thirdPanelVisible: thirdVisible,
    };
  });
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1600, height: 900 },
  ignoreHTTPSErrors: true,
});
const page = await context.newPage();
const report = { date: '2026-07-01', scenarios: [] };

try {
  await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 120_000 });
  await page.click('button:has-text("Satellite View")');
  await waitForMapReady(page);
  await page.click('button:has-text("Capture & Enhance")');
  await page.waitForSelector('button:has-text("Enhance Selected Area")', { timeout: 60_000 });
  log('crop UI ready — starting enhance');
  await page.click('button:has-text("Enhance Selected Area")');
  await page.waitForSelector('text=Enhancement Complete', { timeout: ENHANCE_TIMEOUT_MS });
  log('enhance complete');
  await page.click('button:has-text("Detect Objects")');
  await page.waitForSelector('img[alt="Detected"]', { timeout: DETECT_TIMEOUT_MS });
  log('detect complete — third panel visible');

  const metrics100 = await layoutMetrics(page);
  const shot100 = path.join(ARTIFACT_DIR, '01-100pct-detection-results.png');
  await page.screenshot({ path: shot100, fullPage: true, scale: 'css' });
  log(`100pct layout ${JSON.stringify(metrics100)}`);
  report.scenarios.push({
    name: '100pct',
    pass: metrics100.flexDirection === 'row' && metrics100.panelCount >= 3,
    metrics: metrics100,
    screenshot: shot100,
  });

  // 150% browser zoom on 1600px → effective layout width ~1067px (<1400px breakpoint).
  await page.setViewportSize({ width: 1067, height: 900 });
  await page.waitForTimeout(500);
  const metrics150 = await layoutMetrics(page);
  const shot150 = path.join(ARTIFACT_DIR, '02-150pct-detection-results.png');
  await page.screenshot({ path: shot150, fullPage: true, scale: 'css' });
  log(`150pct layout ${JSON.stringify(metrics150)}`);
  report.scenarios.push({
    name: '150pct',
    pass: metrics150.flexDirection === 'column' && metrics150.thirdPanelVisible,
    metrics: metrics150,
    screenshot: shot150,
  });

  report.verdict = report.scenarios.every((s) => s.pass) ? 'pass' : 'fail';
} catch (error) {
  const failShot = path.join(ARTIFACT_DIR, 'detection-failure.png');
  await page.screenshot({ path: failShot, fullPage: true, scale: 'css' }).catch(() => {});
  log(`FAIL ${error.message}`);
  report.verdict = 'fail';
  report.error = error.message;
  report.failure_screenshot = failShot;
} finally {
  await context.close();
  await browser.close();
}

fs.writeFileSync(path.join(ARTIFACT_DIR, 'results.txt'), `${results.join('\n')}\n\n${JSON.stringify(report, null, 2)}\n`);
fs.writeFileSync(path.join(ARTIFACT_DIR, 'mt-r3a-playwright-summary.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log('\nFINAL:', report.verdict);
process.exit(report.verdict === 'pass' ? 0 : 1);
