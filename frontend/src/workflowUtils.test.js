// Assisted by: cursor, claude

import {
  deriveBackendBases,
  formatPercent,
  isInvalidCorsHeaderPair,
  shouldUseAsyncEnhance,
  getDetectionStatusLabel,
  previewPayloadToObjectUrl,
  statsHasTimeSeries,
} from './workflowUtils';

const ONE_BY_ONE_PNG_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';

describe('deriveBackendBases', () => {
  test('derives cluster Routes from frontend hostname', () => {
    const bases = deriveBackendBases(
      'caisat-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com',
      'https:',
    );
    expect(bases.enhance).toBe(
      'https://caisat-backend-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com',
    );
    expect(bases.detection).toBe(
      'https://caisat-detection-backend-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com',
    );
    expect(bases.changedetection).toBe(
      'https://caisat-backend-changedetection-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com',
    );
  });

  test('uses localhost ports for local dev', () => {
    const bases = deriveBackendBases('localhost', 'http:');
    expect(bases.enhance).toBe('http://localhost:8080');
    expect(bases.detection).toBe('http://localhost:8081');
    expect(bases.changedetection).toBe('http://localhost:8082');
  });
});

describe('isInvalidCorsHeaderPair', () => {
  test('flags wildcard origin with credentials', () => {
    expect(isInvalidCorsHeaderPair('*', 'true')).toBe(true);
    expect(isInvalidCorsHeaderPair('*', 'True')).toBe(true);
  });

  test('allows explicit origin with credentials', () => {
    expect(isInvalidCorsHeaderPair('https://caisat.example.com', 'true')).toBe(false);
  });

  test('allows wildcard without credentials flag', () => {
    expect(isInvalidCorsHeaderPair('*', 'false')).toBe(false);
    expect(isInvalidCorsHeaderPair('*', null)).toBe(false);
  });
});

describe('formatPercent', () => {
  test('formats numbers and guards missing seed stats', () => {
    expect(formatPercent(1.234)).toBe('1.23%');
    expect(formatPercent(undefined)).toBe('N/A');
    expect(formatPercent(null)).toBe('N/A');
  });
});

describe('statsHasTimeSeries', () => {
  test('detects pipeline vs seed payloads', () => {
    expect(statsHasTimeSeries({ timeSeries: [{ date: '2024-01-01' }] })).toBe(true);
    expect(statsHasTimeSeries({ avgChange: 0.5, classification: 'STABLE' })).toBe(false);
    expect(statsHasTimeSeries({ timeSeries: [] })).toBe(false);
  });
});

describe('shouldUseAsyncEnhance', () => {
  test('uses async when capabilities are null and crop exceeds default', () => {
    expect(shouldUseAsyncEnhance(768, null, 1)).toBe(true);
  });

  test('uses sync when capabilities loaded and crop matches default', () => {
    expect(shouldUseAsyncEnhance(256, { default_crop: 256 }, 1)).toBe(false);
  });
});

describe('getDetectionStatusLabel', () => {
  test('returns idle when gpu exclusive and predictor is not ready', () => {
    expect(getDetectionStatusLabel(true, true, false)).toBe('idle');
  });
});

describe('previewPayloadToObjectUrl', () => {
  const originalImage = global.Image;
  const originalCreateObjectURL = URL.createObjectURL;
  const originalRevokeObjectURL = URL.revokeObjectURL;

  beforeEach(() => {
    URL.createObjectURL = jest.fn(() => 'blob:mock-preview-url');
    URL.revokeObjectURL = jest.fn();

    global.Image = class MockImage {
      set src(value) {
        this._src = value;
        setTimeout(() => {
          if (this.onload) {
            this.onload();
          }
        }, 0);
      }
    };
  });

  afterEach(() => {
    global.Image = originalImage;
    URL.createObjectURL = originalCreateObjectURL;
    URL.revokeObjectURL = originalRevokeObjectURL;
  });

  test('returns an object URL for a valid preview payload', async () => {
    const objectUrl = await previewPayloadToObjectUrl({
      media_type: 'image/png',
      preview: ONE_BY_ONE_PNG_BASE64,
    });

    expect(objectUrl).toBe('blob:mock-preview-url');
    expect(URL.createObjectURL).toHaveBeenCalled();
  });

  test('throws when preview payload is invalid', async () => {
    await expect(previewPayloadToObjectUrl({})).rejects.toThrow(
      'Server returned an invalid enhance response',
    );
    await expect(previewPayloadToObjectUrl({ preview: 'abc' })).rejects.toThrow(
      'Server returned an invalid enhance response',
    );
  });
});
