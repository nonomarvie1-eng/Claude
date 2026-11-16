import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { viteSingleFile } from 'vite-plugin-singlefile';
import path from 'node:path';
import fs from 'node:fs';
import type { Plugin } from 'vite';

/** Parity fixtures in shared/*.json are only for the unit tests: they are
 *  stripped from the game bundle (smaller download, faster first screen). */
function stripTestFixtures(): Plugin {
  return {
    name: 'strip-test-fixtures',
    enforce: 'pre',
    load(id) {
      if (process.env.VITEST || !id.endsWith('.json') || !id.includes(`${path.sep}shared${path.sep}`)) return null;
      const data = JSON.parse(fs.readFileSync(id, 'utf8'));
      if (Array.isArray(data) || typeof data !== 'object') return null;
      for (const k of ['fixtures', 'gameFixtures']) delete data[k];
      return JSON.stringify(data);
    },
  };
}

// SINGLEFILE=1 inlines every asset into one index.html (shareable demo build).
const single = process.env.SINGLEFILE === '1';

export default defineConfig({
  base: './', // Stake Engine serves the game from /{team}/{game}/{version}/ -> relative paths
  plugins: [stripTestFixtures(), svelte(), ...(single ? [viteSingleFile()] : [])],
  resolve: { alias: { $shared: path.resolve(__dirname, '../shared') } },
  build: {
    target: 'es2020',
    assetsInlineLimit: single ? 100_000_000 : 4096,
    chunkSizeWarningLimit: 2000,
  },
  server: { fs: { allow: ['..'] } },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
});
