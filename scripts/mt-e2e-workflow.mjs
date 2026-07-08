// Assisted by: cursor, claude
// MT-E2E workflow validation — enhance (256/768), detect progress stages, gpu_exclusive health idle.
// Stage labels imported from workflowUtils for parity with frontend unit tests.
// When CAISAT_GPU_EXCLUSIVE=1, scales YOLO to 0 for idle header check; restore after run:
//   oc scale deploy/yolov8m-satelite-predictor --replicas=1 -n caisat

import { chromium } from 'playwright';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DETECT_STAGE_LABELS, ENHANCE_STAGE_LABELS } from '../frontend/src/workflowUtils.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const FRONTEND_URL = process.env.CAISAT_FRONTEND_URL;
if (!FRONTEND_URL) {
  throw new Error('Set CAISAT_FRONTEND_URL to the cluster Route URL (not committed to the repo).');
}

const DATE_STAMP = process.env.MT_E2E_DATE ?? '20260708';
const ARTIFACT_DIR = process.env.MT_E2E_ARTIFACT_DIR
  ?? path.resolve(__dirname, `../docs/validation/artifacts/mt-e2e-${DATE_STAMP}`);
const ENHANCE_256_TIMEOUT_MS = 420_000;
const ENHANCE_768_TIMEOUT_MS = 420_000;
const DETECT_TIMEOUT_MS = 300_000;
const HEALTH_IDLE_TIMEOUT_MS = 60_000;
const HEALTH_IDLE_POLL_MS = Number(process.env.HEALTH_IDLE_WAIT_MS ?? 60_000);
const GPU_EXCLUSIVE = process.env.CAISAT_GPU_EXCLUSIVE === '1';
const K8S_NAMESPACE = process.env.CAISAT_NAMESPACE ?? 'caisat';
const YOLO_DEPLOYMENT = process.env.YOLO_DEPLOYMENT ?? 'yolov8m-satelite-predictor';

const results = [];

function log(line) {
  const entry = `${new Date().toISOString()} ${line}`;
  results.push(entry);
  console.log(entry);
}

function detectionHealthUrl() {
  const parsed = new URL(FRONTEND_URL);
  parsed.hostname = parsed.hostname.replace('caisat', 'caisat-detection-backend');
  return `${parsed.origin}/health`;
}

function backendCapabilitiesUrl() {
  const parsed = new URL(FRONTEND_URL);
  parsed.hostname = parsed.hostname.replace('caisat', 'caisat-backend');
  return `${parsed.origin}/api/capabilities`;
}

// OpenShift Routes use cluster CA; Node fetch fails TLS verify — use curl -sk.
function fetchDetectionHealth() {
  const response = execSync(`curl -sk --max-time 10 "${detectionHealthUrl()}"`, {
    encoding: 'utf8',
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  return JSON.parse(response);
}

async function ensureYoloScaledDown() {
  if (!GPU_EXCLUSIVE) {
    return;
  }
  log('prerequisite — scale YOLO predictor to 0 for idle header check');
  try {
    execSync(`oc scale deploy/${YOLO_DEPLOYMENT} --replicas=0 -n ${K8S_NAMESPACE}`, { stdio: 'pipe' });
  } catch (error) {
    throw new Error(`oc scale ${YOLO_DEPLOYMENT} to 0 failed: ${error.message}`);
  }

  const deadline = Date.now() + 120_000;
  while (Date.now() < deadline) {
    try {
      const payload = fetchDetectionHealth();
      if (payload.predictor_ready === false) {
        log('prerequisite — predictor_ready=false after scale-down');
        return;
      }
    } catch {
      // retry until deadline
    }
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
  throw new Error(`YOLO still warm after scale-down (GET ${detectionHealthUrl()})`);
}

function collectDeployMetadata() {
  const metadata = {
    gitSha: null,
    capabilities: null,
    helmRevision: null,
    images: {},
  };

  try {
    const fullSha = execSync('git rev-parse HEAD', {
      cwd: path.resolve(__dirname, '..'),
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
    }).trim();
    // Short SHA avoids detect-secrets false positives on full hex digests in artifacts.
    metadata.gitSha = fullSha.slice(0, 7);
  } catch {
    log('metadata — git rev-parse HEAD unavailable');
  }

  try {
    const response = execSync(`curl -sk --max-time 10 "${backendCapabilitiesUrl()}"`, {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    metadata.capabilities = JSON.parse(response);
  } catch {
    log('metadata — capabilities fetch unavailable');
  }

  try {
    execSync('oc whoami', { stdio: 'pipe' });
  } catch {
    log('metadata — oc unavailable (skip deploy digests)');
    return metadata;
  }

  try {
    const helmList = execSync(`helm list -n ${K8S_NAMESPACE} -o json`, {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    const releases = JSON.parse(helmList);
    const caisatRelease = releases.find((release) => release.name === 'caisat');
    if (caisatRelease) {
      metadata.helmRevision = caisatRelease.revision;
    }
  } catch {
    log('metadata — helm revision unavailable');
  }

  for (const [component, label] of [
    ['frontend', 'app.kubernetes.io/component=frontend'],
    ['backend', 'app.kubernetes.io/component=backend'],
  ]) {
    try {
      const imageId = execSync(
        `oc get pod -n ${K8S_NAMESPACE} -l ${label} -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'`,
        { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] },
      ).trim();
      if (imageId) {
        // Strip registry/org for commit-safe artifacts (check-no-cluster-info).
        const digestMatch = imageId.match(/sha256:[a-f0-9]{64}/);
        metadata.images[component] = digestMatch ? digestMatch[0] : imageId.replace(/[^/@]+\/[^/@]+\//, '');
      }
    } catch {
      log(`metadata — ${component} image digest unavailable`);
    }
  }

  return metadata;
}

async function waitForAnyEnhanceStage(page, timeoutMs) {
  const labels = Object.values(ENHANCE_STAGE_LABELS);
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    for (const label of labels) {
      const visible = await page.locator(`text=${label}`).isVisible().catch(() => false);
      if (visible) {
        return label;
      }
    }
    await page.waitForTimeout(500);
  }
  throw new Error(`No enhance stage label visible (expected one of: ${labels.join(', ')})`);
}

async function waitForMapReady(page) {
  await page.waitForSelector('.leaflet-tile-loaded', { timeout: 60_000 });
  await page.waitForTimeout(3000);
}

async function loadFrontend(page) {
  await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 120_000 });
  await page.waitForSelector('.status', { timeout: HEALTH_IDLE_TIMEOUT_MS });
}

async function navigateToCropUi(page) {
  await page.click('button:has-text("Satellite View")');
  await waitForMapReady(page);
  await page.click('button:has-text("Capture & Enhance")');
  await page.waitForSelector('button:has-text("Enhance Selected Area")', { timeout: 60_000 });
}

async function prepareCropEnhanceStep(page) {
  const onCropStep = await page.locator('button.crop-size-btn').first().isVisible().catch(() => false);
  if (onCropStep) {
    return;
  }
  await page.click('button.back-btn');
  await page.waitForSelector('button:has-text("Capture & Enhance")', { timeout: 60_000 });
  await page.click('button:has-text("Capture & Enhance")');
  await page.waitForSelector('button.crop-size-btn', { timeout: 60_000 });
}

async function runEnhanceScenario(page, { name, cropSize, timeoutMs, expectedNaturalWidth, assertEnhanceStages = false }) {
  const scenario = { name, pass: false, cropSize, naturalWidth: null, stagesSeen: [], error: null };
  try {
    if (cropSize !== 256) {
      await prepareCropEnhanceStep(page);
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

    if (assertEnhanceStages) {
      const stageLabel = await waitForAnyEnhanceStage(page, Math.min(timeoutMs, 60_000));
      scenario.stagesSeen.push(stageLabel);
      log(`${name} — saw enhance stage: ${stageLabel}`);
    }

    await page.waitForSelector('text=Enhancement Complete', { timeout: timeoutMs });

    const naturalWidth = await page.locator('img[alt="Enhanced"]').evaluate((img) => img.naturalWidth);
    scenario.naturalWidth = naturalWidth;
    scenario.pass = naturalWidth === expectedNaturalWidth;
    if (!scenario.pass && naturalWidth > 0) {
      scenario.error = `Expected naturalWidth ${expectedNaturalWidth}, got ${naturalWidth}`;
    }

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

    try {
      await page.waitForSelector(`text=${DETECT_STAGE_LABELS.activating}`, { timeout: 45_000 });
      scenario.stagesSeen.push('activating');
      log(`detect-progress — saw stage: activating`);
    } catch {
      log('detect-progress — activating stage not shown (detector may already be warm)');
    }

    await page.waitForSelector(`text=${DETECT_STAGE_LABELS.detecting}`, { timeout: DETECT_TIMEOUT_MS });
    scenario.stagesSeen.push('detecting');
    log(`detect-progress — saw stage: detecting`);

    await page.waitForSelector('img[alt="Detected"]', { timeout: DETECT_TIMEOUT_MS });
    scenario.pass = scenario.stagesSeen.includes('detecting');

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
    log('health-idle — poll header before any GPU work (YOLO should be scaled down)');
    const statusLocator = page.locator('.status');
    const pollStart = Date.now();
    let headerText = '';
    while (Date.now() - pollStart < HEALTH_IDLE_POLL_MS) {
      headerText = (await statusLocator.textContent())?.trim() ?? '';
      if (/Detection:\s*idle/i.test(headerText)) {
        scenario.pass = true;
        break;
      }
      await page.waitForTimeout(3000);
    }
    scenario.headerText = headerText;

    const shot = path.join(ARTIFACT_DIR, 'health-idle-header.png');
    await page.screenshot({ path: shot, fullPage: true, scale: 'css' });
    scenario.screenshot = shot;

    if (scenario.pass) {
      log(`health-idle — pass header="${headerText}"`);
    } else if (!/Detection:/i.test(headerText)) {
      scenario.error = 'Header did not show Detection status — capabilities or detection health may not have loaded';
      log(`FAIL health-idle: ${scenario.error}`);
    } else {
      scenario.error = `Expected "Detection: idle", got "${headerText}"`;
      log(`FAIL health-idle: ${scenario.error}`);
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
    '<!-- Assisted by: cursor, claude -->',
    '',
    '| Field | Value |',
    '| ----- | ----- |',
    `| Date | ${report.date} |`,
    `| Frontend URL | \`${FRONTEND_URL}\` |`,
    `| Git SHA | ${report.deploy?.gitSha ?? 'n/a'} |`,
    `| Helm revision | ${report.deploy?.helmRevision ?? 'n/a'} |`,
    `| Verdict | **${report.verdict}** |`,
    '',
    '## Deploy metadata',
    '',
    `- Frontend image: \`${report.deploy?.images?.frontend ?? 'n/a'}\``,
    `- Backend image: \`${report.deploy?.images?.backend ?? 'n/a'}\``,
    `- Capabilities: \`${report.deploy?.capabilities ? JSON.stringify(report.deploy.capabilities) : 'n/a'}\``,
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
    lines.push('## Run error', '', report.error, '');
  }

  if (GPU_EXCLUSIVE) {
    lines.push(
      '## Operator notes',
      '',
      `- Restore YOLO after gpu_exclusive run: \`oc scale deploy/${YOLO_DEPLOYMENT} --replicas=1 -n ${K8S_NAMESPACE}\``,
      `- Script scales YOLO to 0 for idle check but does not restore; operators must scale back up.`,
      '',
    );
  }

  fs.writeFileSync(path.join(ARTIFACT_DIR, 'report.md'), `${lines.join('\n')}\n`);
}

fs.mkdirSync(ARTIFACT_DIR, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1600, height: 900 },
  ignoreHTTPSErrors: true,
});
const page = await context.newPage();
const report = {
  date: new Date().toISOString().slice(0, 10),
  frontendUrl: FRONTEND_URL,
  gpuExclusive: GPU_EXCLUSIVE,
  deploy: collectDeployMetadata(),
  scenarios: [],
};

try {
  await ensureYoloScaledDown();
  if (GPU_EXCLUSIVE) {
    log(`note — restore YOLO after run: oc scale deploy/${YOLO_DEPLOYMENT} --replicas=1 -n ${K8S_NAMESPACE}`);
  }
  await loadFrontend(page);

  const healthIdle = await runHealthIdleScenario(page);
  report.scenarios.push(healthIdle);

  await navigateToCropUi(page);

  const enhance256 = await runEnhanceScenario(page, {
    name: 'enhance-256',
    cropSize: 256,
    timeoutMs: ENHANCE_256_TIMEOUT_MS,
    expectedNaturalWidth: 1024,
  });
  report.scenarios.push(enhance256);

  const enhance768 = await runEnhanceScenario(page, {
    name: 'enhance-768',
    cropSize: 768,
    timeoutMs: ENHANCE_768_TIMEOUT_MS,
    expectedNaturalWidth: 2048,
    assertEnhanceStages: true,
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

  const required = report.scenarios.filter((s) => !s.skipped);
  const hardFail = report.scenarios.some((s) => !s.pass && !s.skipped);
  report.verdict = !hardFail && required.length > 0 && required.every((s) => s.pass) ? 'pass' : 'fail';
} catch (error) {
  log(`FATAL ${error.message}`);
  report.verdict = 'fail';
  report.error = error.message;
} finally {
  await context.close();
  await browser.close();
}

// Shorten digests/SHAs in committed JSON to avoid detect-secrets false positives.
const artifactReport = JSON.parse(JSON.stringify(report));
if (artifactReport.deploy?.gitSha) {
  artifactReport.deploy.gitSha = artifactReport.deploy.gitSha.slice(0, 7);
}
fs.writeFileSync(path.join(ARTIFACT_DIR, 'results.txt'), `${results.join('\n')}\n\n${JSON.stringify(artifactReport, null, 2)}\n`);
fs.writeFileSync(path.join(ARTIFACT_DIR, 'mt-e2e-summary.json'), `${JSON.stringify(artifactReport, null, 2)}\n`);
writeReport(artifactReport);

console.log('\nFINAL:', report.verdict);
console.log('Artifacts:', ARTIFACT_DIR);
process.exit(report.verdict === 'pass' ? 0 : 1);
