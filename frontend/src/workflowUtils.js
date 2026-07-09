// Assisted by: cursor, claude

/** Derive cross-origin backend Route URLs from the frontend hostname (matches App.js). */
export function deriveBackendBases(hostname, protocol = 'https:', localPorts = {}) {
  const ports = {
    enhance: localPorts.enhance ?? 8080,
    detection: localPorts.detection ?? 8081,
    changedetection: localPorts.changedetection ?? 8082,
  };
  if (hostname.includes('localhost')) {
    return {
      enhance: `http://localhost:${ports.enhance}`,
      detection: `http://localhost:${ports.detection}`,
      changedetection: `http://localhost:${ports.changedetection}`,
    };
  }
  return {
    enhance: `${protocol}//${hostname.replace('caisat', 'caisat-backend')}`,
    detection: `${protocol}//${hostname.replace('caisat', 'caisat-detection-backend')}`,
    changedetection: `${protocol}//${hostname.replace('caisat', 'caisat-backend-changedetection')}`,
  };
}

/** Browsers reject Allow-Origin * together with Allow-Credentials true. */
export function isInvalidCorsHeaderPair(allowOrigin, allowCredentials) {
  return allowOrigin === '*' && String(allowCredentials).toLowerCase() === 'true';
}

/** Format percentage for Monitored Areas; seed stats may omit numeric fields. */
export function formatPercent(value, digits = 2) {
  return typeof value === 'number' ? `${value.toFixed(digits)}%` : 'N/A';
}

/** True when stats JSON has pipeline time-series (not storage-seed minimal payload). */
export function statsHasTimeSeries(stats) {
  return Array.isArray(stats?.timeSeries) && stats.timeSeries.length > 0;
}

export const ENHANCE_STAGE_LABELS = {
  preparing: 'Preparing crop…',
  uploading: 'Uploading to server…',
  inferring: 'Running AI super-resolution…',
  finalizing: 'Building preview…',
};

export const DETECT_STAGE_LABELS = {
  preparing: 'Preparing enhanced image…',
  uploading: 'Uploading to detection server…',
  activating: 'Activating detection model on GPU…',
  detecting: 'Running object detection…',
  drawing: 'Drawing bounding boxes…',
};

export function getEnhanceTileCount(cropSize, caps) {
  const maxTile = caps?.max_tile ?? 256;
  const tilingEnabled = caps?.tiling_enabled ?? cropSize > maxTile;
  if (!tilingEnabled || cropSize <= maxTile) {
    return 1;
  }
  const tilesPerSide = Math.ceil(cropSize / maxTile);
  return tilesPerSide * tilesPerSide;
}

export function shouldUseAsyncEnhance(cropSize, caps, tileCount) {
  const defaultCrop = caps?.default_crop ?? 256;
  if (tileCount > 1) {
    return true;
  }
  if (!caps && cropSize > defaultCrop) {
    return true;
  }
  return cropSize > defaultCrop;
}

export function getDetectEtaHint(gpuExclusive, predictorReady) {
  if (gpuExclusive && predictorReady === false) {
    return 'First run may take 30–90s while the model starts';
  }
  if (gpuExclusive) {
    return 'Model swap after enhance · usually ~30–90s';
  }
  return 'Usually ~10–45 seconds';
}

export async function previewPayloadToObjectUrl(payload) {
  if (!payload?.preview || !payload?.media_type) {
    throw new Error('Server returned an invalid enhance response');
  }
  const response = await fetch(`data:${payload.media_type};base64,${payload.preview}`);
  const previewBlob = await response.blob();
  const objectUrl = URL.createObjectURL(previewBlob);
  await new Promise((resolve, reject) => {
    const probe = new Image();
    probe.onload = resolve;
    probe.onerror = () => reject(new Error('Enhanced preview failed to load in browser'));
    probe.src = objectUrl;
  });
  return objectUrl;
}

export function getDetectionStatusLabel(detectionOnline, gpuExclusive, predictorReady) {
  if (!detectionOnline) {
    return 'down';
  }
  if (gpuExclusive && predictorReady === false) {
    return 'idle';
  }
  return 'up';
}
