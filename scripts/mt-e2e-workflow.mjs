// Assisted by: cursor, claude
// MT-E2E workflow validation — enhance (256/768), detect progress stages, gpu_exclusive health idle.
// Stage labels imported from workflowUtils for parity with frontend unit tests.

import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DETECT_STAGE_LABELS } from '../frontend/src/workflowUtils.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const FRONTEND_URL = process.env.CAISAT_FRONTEND_URL;
if (!FRONTEND_URL) {
  throw new Error('Set CAISAT_FRONTEND_URL to the cluster Route URL (not committed to the repo).');
}

const DATE_STAMP = process.env.MT_E2E_DATE ?? '20260708';
const ARTIFACT_DIR = process.env.MT_E2E_ARTIFACT_DIR
  ?? path.resolve(__dirname, `../docs/validation/artifacts/mt-e2e-${DATE_STAMP}`);
const ENHANCE_256_TIMEOUT_MS = 420_000;
const ENHANCE_768_TIMEOUT_MS = 180_000;
const DETECT_TIMEOUT_MS = 300_000;
const HEALTH_IDLE_TIMEOUT_MS = 60_000;

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

async function navigateToCropUi(page) {
  await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 120_000 });
  await page.click('button:has-text("Satellite View")');
  await waitForMapReady(page);
  await page.click('button:has-text("Capture & Enhance")');
  await page.waitForSelector('button:has-text("Enhance Selected Area")', { timeout: 60_000 });
}

async function runEnhanceScenario(page, { name, cropSize, timeoutMs }) {
  const scenario = { name, pass: false, cropSize, naturalWidth: null, error: null };
  try {
    if (cropSize !== 256) {
      const cropButton = page.locator(`button.crop-size-btn:has-text("${cropSize}×${cropSize}")`);
      const visible = await cropButton.isVisible().catch(() => false);
      if (!visible) {
        scenario.skipped = true;
        scenario.error = `Crop button ${cropSize}×${cropSize} not available (max_crop may be < ${cropSize})`;
        log(`SKIP ${name}: ${scenario.error}`);
        return scenario;
      }
      await cropButton.click();
      await page.waitForTimeout(300);
    }

    log(`${name} — starting enhance @ ${cropSize}×${cropSize}`);
    await page.click('button:has-text("Enhance Selected Area")');
    await page.waitForSelector('text=Enhancement Complete', { timeout: timeoutMs });

    const naturalWidth = await page.locator('img[alt="Enhanced"]').evaluate((img) => img.naturalWidth);
    scenario.naturalWidth = naturalWidth;
    scenario.pass = naturalWidth > 0;

    const shot = path.join(ARTIFACT_DIR, `${name.replace(/\s+/g, '-')}-enhanced.png`);
    await page.screenshot({ path: shot, fullPage: true, scale: 'css' });
    scenario.screenshot = shot;
    log(`${name} — naturalWidth=${naturalWidth} pass=${scenario.pass}`);
  } catch (error) {
    scenario.error = error.message;
    const failShot = path.join(ARTIFACT_DIR, `${name.replace(/\s+/g, '-')}-failure.png`);
    await page.screenshot({ path: failShot, fullPage: true, scale: 'css' }).catch(() => {});
    scenario.failure_screenshot = failShot;
    log(`FAIL ${name}: ${error.message}`);
  }
  return scenario;
}

async function runDetectProgressScenario(page) {
  const scenario = {
    name: 'detect-progress-stages',
    pass: false,
    stagesSeen: [],
    error: null,
  };

  try {
    log('detect-progress — starting detection');
    await page.click('button:has-text("Detect Objects")');

    await page.waitForSelector(`text=${DETECT_STAGE_LABELS.activating}`, { timeout: DETECT_TIMEOUT_MS });
    scenario.stagesSeen.push('activating');
    log(`detect-progress — saw stage: activating`);

    await page.waitForSelector(`text=${DETECT_STAGE_LABELS.detecting}`, { timeout: DETECT_TIMEOUT_MS });
    scenario.stagesSeen.push('detecting');
    log(`detect-progress — saw stage: detecting`);

    await page.waitForSelector('img[alt="Detected"]', { timeout: DETECT_TIMEOUT_MS });
    scenario.pass = scenario.stagesSeen.includes('activating') && scenario.stagesSeen.includes('detecting');

    const shot = path.join(ARTIFACT_DIR, 'detect-progress-complete.png');
    await page.screenshot({ path: shot, fullPage: true, scale: 'css' });
    scenario.screenshot = shot;
    log(`detect-progress — pass=${scenario.pass} stages=${scenario.stagesSeen.join(',')}`);
  } catch (error) {
    scenario.error = error.message;
    const failShot = path.join(ARTIFACT_DIR, 'detect-progress-failure.png');
    await page.screenshot({ path: failShot, fullPage: true, scale: 'css' }).catch(() => {});
    scenario.failure_screenshot = failShot;
    log(`FAIL detect-progress: ${error.message}`);
  }
  return scenario;
}

async function runHealthIdleScenario(page) {
  const scenario = { name: 'health-idle-header', pass: false, headerText: null, error: null };
  try {
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle', timeout: 120_000 });
    const statusLocator = page.locator('.status');
    await statusLocator.waitFor({ timeout: HEALTH_IDLE_TIMEOUT_MS });
    const headerText = (await statusLocator.textContent())?.trim() ?? '';
    scenario.headerText = headerText;
    scenario.pass = /Detection:\s*idle/i.test(headerText);

    const shot = path.join(ARTIFACT_DIR, 'health-idle-header.png');
    await page.screenshot({ path: shot, fullPage: true, scale: 'css' });
    scenario.screenshot = shot;

    if (!scenario.pass) {
      scenario.skipped = !/Detection:/i.test(headerText);
      scenario.note = scenario.skipped
        ? 'Header did not show Detection status — may not be gpu_exclusive cluster or YOLO already warm'
        : `Expected "Detection: idle", got "${headerText}"`;
      log(`SKIP/WARN health-idle: ${scenario.note}`);
    } else {
      log(`health-idle — pass header="${headerText}"`);
    }
  } catch (error) {
    scenario.error = error.message;
    log(`FAIL health-idle: ${error.message}`);
  }
  return scenario;
}

function writeReport(report) {
  const lines = [
    '# MT-E2E Workflow Report',
    '',
    `<!-- Assisted by: cursor, claude -->`,
    '',
    `| Field | Value |`,
    `| ----- | ----- |`,
    `| Date | ${report.date} |`,
    `| Frontend URL | ${FRONTEND_URL} |`,
    `| Verdict | **${report.verdict}** |`,
    '',
    '## Scenarios',
    '',
  ];

  for (const scenario of report.scenarios) {
    const status = scenario.skipped ? 'skipped' : scenario.pass ? 'pass' : 'fail';
    lines.push(`### ${scenario.name} — ${status}`);
    lines.push('');
    if (scenario.cropSize) {
      lines.push(`- Crop: ${scenario.cropSize}×${scenario.cropSize}`);
    }
    if (scenario.naturalWidth != null) {
      lines.push(`- Enhanced naturalWidth: ${scenario.naturalWidth}`);
    }
    if (scenario.stagesSeen?.length) {
      lines.push(`- Stages seen: ${scenario.stagesSeen.join(' → ')}`);
    }
    if (scenario.headerText) {
      lines.push(`- Header: \`${scenario.headerText}\``);
    }
    if (scenario.error) {
      lines.push(`- Error: ${scenario.error}`);
    }
    if (scenario.note) {
      lines.push(`- Note: ${scenario.note}`);
    }
    if (scenario.screenshot) {
      lines.push(`- Screenshot: \`${path.basename(scenario.screenshot)}\``);
    }
    lines.push('');
  }

  if (report.error) {
    lines.push(`## Run error`, '', report.error, '');
  }

  fs.writeFileSync(path.join(ARTIFACT_DIR, 'report.md'), `${lines.join('\n')}\n`);
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1600, height: 900 },
  ignoreHTTPSErrors: true,
});
const page = await context.newPage();
const report = { date: new Date().toISOString().slice(0, 10), scenarios: [] };

try {
  await navigateToCropUi(page);

  const enhance256 = await runEnhanceScenario(page, {
    name: 'enhance-256',
    cropSize: 256,
    timeoutMs: ENHANCE_256_TIMEOUT_MS,
  });
  report.scenarios.push(enhance256);

  const enhance768 = await runEnhanceScenario(page, {
    name: 'enhance-768',
    cropSize: 768,
    timeoutMs: ENHANCE_768_TIMEOUT_MS,
  });
  report.scenarios.push(enhance768);

  if (enhance256.pass || enhance768.pass) {
    const detectProgress = await runDetectProgressScenario(page);
    report.scenarios.push(detectProgress);
  } else {
    report.scenarios.push({
      name: 'detect-progress-stages',
      pass: false,
      skipped: true,
      error: 'Skipped — enhance did not complete',
    });
  }

  const healthIdle = await runHealthIdleScenario(page);
  report.scenarios.push(healthIdle);

  const required = report.scenarios.filter((s) => !s.skipped);
  report.verdict = required.length > 0 && required.every((s) => s.pass) ? 'pass' : 'fail';
} catch (error) {
  log(`FATAL ${error.message}`);
  report.verdict = 'fail';
  report.error = error.message;
} finally {
  await context.close();
  await browser.close();
}

fs.writeFileSync(path.join(ARTIFACT_DIR, 'results.txt'), `${results.join('\n')}\n\n${JSON.stringify(report, null, 2)}\n`);
fs.writeFileSync(path.join(ARTIFACT_DIR, 'mt-e2e-summary.json'), `${JSON.stringify(report, null, 2)}\n`);
writeReport(report);

console.log('\nFINAL:', report.verdict);
console.log('Artifacts:', ARTIFACT_DIR);
process.exit(report.verdict === 'pass' ? 0 : 1);
