import '@testing-library/jest-dom';

// Polyfill URL.createObjectURL and URL.revokeObjectURL for jsdom environment
if (typeof window !== 'undefined') {
  if (!window.URL.createObjectURL) {
    window.URL.createObjectURL = (blob: Blob | MediaSource) =>
      `blob:mock-url-${blob instanceof Blob ? blob.size : 0}`;
  }
  if (!window.URL.revokeObjectURL) {
    window.URL.revokeObjectURL = () => {};
  }
}
