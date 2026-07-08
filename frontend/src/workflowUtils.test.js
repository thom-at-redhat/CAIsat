// Assisted by: cursor, claude

import {
  shouldUseAsyncEnhance,
  getDetectionStatusLabel,
  previewPayloadToObjectUrl,
} from './workflowUtils';

const ONE_BY_ONE_PNG_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';

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
